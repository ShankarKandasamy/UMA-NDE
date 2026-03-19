// ============================================
// Report Generation Pipeline
// ============================================

const ReportPipeline = {
    STORAGE_KEY: 'uma_report_templates',
    MANIFEST_KEY: 'uma_report_manifest',

    // ---- Custom Anthropic API call (multimodal + configurable max_tokens) ----

    async callAnthropicEx(model, systemMsg, content, maxTokens = 8192) {
        if (!settings.anthropicKey || !settings.apiEndpoint) {
            throw new Error('Anthropic API key or API endpoint not configured.');
        }

        const body = {
            model,
            max_tokens: maxTokens,
            system: systemMsg,
            messages: [{ role: 'user', content }]
        };

        const response = await fetch(`${settings.apiEndpoint}/llm/anthropic`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': settings.apiKey,
                'X-Anthropic-Key': settings.anthropicKey
            },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            const errText = await response.text();
            throw new Error(`Anthropic API error ${response.status}: ${errText}`);
        }

        const data = await response.json();
        const rawText = data.content[0].text;

        if (data.usage) {
            console.log(`[Report] Anthropic ${model} — input: ${data.usage.input_tokens}, output: ${data.usage.output_tokens}`);
        }

        try {
            return JSON.parse(rawText);
        } catch {
            let cleaned = rawText.trim();
            if (cleaned.startsWith('```')) {
                cleaned = cleaned.split('\n').slice(1).join('\n').replace(/```\s*$/, '');
            }
            return JSON.parse(cleaned);
        }
    },

    // ---- Template CRUD (localStorage) ----

    getTemplates() {
        try {
            return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]');
        } catch {
            return [];
        }
    },

    saveTemplates(templates) {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(templates));
    },

    deleteTemplate(templateId) {
        const templates = this.getTemplates().filter(t => t.id !== templateId);
        this.saveTemplates(templates);
        return templates;
    },

    // ---- Phase 0: Template Analysis ----

    async analyzeTemplate(filename, blob) {
        PipelineLog.log(`Analyzing template: ${filename}`);

        const arrayBuffer = await blob.arrayBuffer();
        const base64 = btoa(
            new Uint8Array(arrayBuffer).reduce((data, byte) => data + String.fromCharCode(byte), '')
        );

        const content = [
            {
                type: 'document',
                source: {
                    type: 'base64',
                    media_type: 'application/pdf',
                    data: base64
                }
            },
            {
                type: 'text',
                text: TEMPLATE_ANALYSIS_PROMPT
            }
        ];

        const result = await this.callAnthropicEx(
            'claude-sonnet-4-20250514',
            TEMPLATE_ANALYSIS_SYSTEM_MSG,
            content,
            8192
        );

        const template = {
            id: 'tpl_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
            filename,
            uploadedAt: new Date().toISOString(),
            reportType: result.reportType || 'Inspection Report',
            title: result.title || filename,
            sections: result.sections || []
        };

        const templates = this.getTemplates();
        templates.push(template);
        this.saveTemplates(templates);

        PipelineLog.log(`Template analyzed: ${template.sections.length} sections found`);
        return template;
    },

    // ---- Phase 1: Folder Mapping ----

    async mapSectionsToFolders(template) {
        PipelineLog.log('Phase 1: Mapping sections to folders...');

        const devFolders = await DevDB.listSubfolders();
        const folders = [];

        for (const folderName of devFolders) {
            if (folderName === 'Uncategorized' || folderName === '_templates') continue;
            const meta = await DevDB.getMetadata(folderName);
            if (meta && meta.folderSummary) {
                folders.push({
                    id: folderName,
                    summary: meta.folderSummary.summary || '',
                    keywords: meta.folderSummary.keywords || [],
                    fileCount: meta.folderSummary.fileCount || 0
                });
            }
        }

        if (folders.length === 0) {
            PipelineLog.log('No folder summaries available — skipping folder mapping');
            return [];
        }

        const sectionsDesc = template.sections.map(s =>
            `- Section ${s.index}: "${s.title}"\n  Summary: ${s.summary}\n  Fields: ${s.fields.join(', ')}`
        ).join('\n');

        const foldersDesc = folders.map(f =>
            `- "${f.id}" (${f.fileCount} files)\n  Summary: ${f.summary}\n  Keywords: ${f.keywords.join(', ')}`
        ).join('\n');

        const userMsg = `Sections:\n${sectionsDesc}\n\nFolders:\n${foldersDesc}\n\n${FOLDER_MAPPING_PROMPT}`;

        const result = await Search.callOpenAI('gpt-4o-mini', SEARCH_SCORING_SYSTEM_MSG, userMsg);

        const mappings = result.mappings || [];
        PipelineLog.log(`Phase 1 complete: ${mappings.length} section mappings created`);
        return mappings;
    },

    // ---- Phase 2a-2b: Gather Section Data ----

    async gatherSectionData(section, folderMappings, subLog) {
        const mapping = folderMappings.find(m => m.sectionIndex === section.index);
        if (!mapping || !mapping.folders || mapping.folders.length === 0) {
            console.log(`[Report] No folder mapping for section ${section.index}: ${section.title}`);
            subLog({ type: 'status', message: 'No folder mapping for this section' });
            return [];
        }

        const folderIds = mapping.folders.map(f => f.folderId);
        const query = `${section.title}. ${section.summary}. Fields needed: ${section.fields.join(', ')}`;

        // Stage 2: Score files in mapped folders
        subLog({ type: 'status', message: 'Scoring files...' });
        const filesResult = await Search.scoreFiles(query, folderIds);
        const scoredFiles = filesResult.results || [];

        if (scoredFiles.length === 0) {
            console.log(`[Report] No relevant files found for section ${section.index}`);
            subLog({ type: 'status', message: 'No relevant files found' });
            return [];
        }

        const uniqueFolders = new Set(scoredFiles.map(f => f.fileId.split('/')[0]));
        subLog({ type: 'status', message: `${scoredFiles.length} files scored relevant across ${uniqueFolders.size} folder(s)` });

        const fileIds = scoredFiles.map(f => f.fileId);

        // Stage 3: Retrieve relevant sections
        const sectionsResult = await Search.retrieveSections(query, fileIds);

        // Resolve pointers to actual content
        const resolved = await Search.resolvePointers(sectionsResult.results || []);

        // Log each resolved chunk
        resolved.forEach((chunk, idx) => {
            subLog({
                type: 'chunk',
                fileTitle: chunk.fileTitle || chunk.filename,
                chunkType: chunk.type,
                folder: chunk.folder,
                reason: chunk.reason,
                isLast: idx === resolved.length - 1
            });
        });

        console.log(`[Report] Section "${section.title}": ${resolved.length} data chunks gathered`);
        return resolved;
    },

    // ---- Phase 2c-2d: Generate One Section ----

    async generateSection(template, sectionIndex, dataChunks, manifest, subLog) {
        const section = template.sections[sectionIndex];
        PipelineLog.log(`Generating section ${sectionIndex + 1}/${template.sections.length}: ${section.title}`);
        subLog({ type: 'status', message: 'Generating section content...' });

        const compactManifest = {
            inferredData: manifest.inferredData,
            userAnswers: manifest.userAnswers,
            completedSections: manifest.completedSections
        };

        const userContent = `Section specification:\n${JSON.stringify(section, null, 2)}\n\nData chunks (${dataChunks.length} items):\n${JSON.stringify(dataChunks, null, 2)}\n\nReport manifest:\n${JSON.stringify(compactManifest, null, 2)}\n\n${SECTION_GENERATION_PROMPT}`;

        const result = await Search.callOpenAI(
            'gpt-4.1',
            SECTION_GENERATION_SYSTEM_MSG,
            userContent,
            16384
        );

        // Update manifest
        if (result.manifestUpdates) {
            if (result.manifestUpdates.inferredData) {
                Object.assign(manifest.inferredData, result.manifestUpdates.inferredData);
            }
            manifest.completedSections.push({
                index: sectionIndex,
                title: section.title,
                summary: result.manifestUpdates.sectionSummary || ''
            });
        }

        // Store section output
        manifest.sectionOutputs[sectionIndex] = result.sectionContent || {};
        manifest.sectionOutputs[sectionIndex].dataGaps = result.dataGaps || [];
        manifest.sectionOutputs[sectionIndex].confidence = result.confidence ?? null;
        manifest.currentSection = sectionIndex + 1;

        return result;
    },

    // ---- Phase 3: Cross-Check ----

    async crossCheck(manifest, template) {
        PipelineLog.log('Phase 3: Cross-checking report consistency...');

        // Build compact summary of all sections
        const sectionSummaries = template.sections.map((s, i) => {
            const output = manifest.sectionOutputs[i];
            if (!output) return { index: i, title: s.title, status: 'missing' };

            const summary = {
                index: i,
                title: output.title || s.title,
                narratives: output.narratives || [],
                bulletPoints: output.bulletPoints || []
            };

            if (output.tables) {
                summary.tables = output.tables.map(t => ({
                    title: t.title,
                    headers: t.headers,
                    rowCount: (t.rows || []).length,
                    sampleRows: (t.rows || []).slice(0, 3)
                }));
            }

            return summary;
        });

        const userContent = `Report sections:\n${JSON.stringify(sectionSummaries, null, 2)}\n\nInferred data:\n${JSON.stringify(manifest.inferredData, null, 2)}\n\n${CROSS_CHECK_PROMPT}`;

        const result = await Search.callOpenAI(
            'gpt-4.1',
            CROSS_CHECK_SYSTEM_MSG,
            userContent,
            8192
        );

        manifest.crossCheck = result;
        manifest.status = 'cross-checked';

        PipelineLog.log(`Cross-check complete: consistency ${((result.overallConsistency || 0) * 100).toFixed(0)}%, ${(result.issues || []).length} issues found`);
        return result;
    },

    // ---- Full Generation Orchestrator ----

    async generateReport(templateId, onProgress, onQuestion, onSubLog) {
        const templates = this.getTemplates();
        const template = templates.find(t => t.id === templateId);
        if (!template) throw new Error('Template not found');

        const progress = onProgress || (() => {});
        const askQuestion = onQuestion || (() => {});
        const subLog = onSubLog || (() => {});

        // Check for in-progress manifest
        let manifest;
        const saved = this.getSavedManifest();
        if (saved && saved.templateId === templateId && saved.status === 'generating') {
            manifest = saved;
            PipelineLog.log(`Resuming report from section ${manifest.currentSection + 1}`);
        } else {
            manifest = {
                reportId: 'rpt_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
                templateId,
                status: 'generating',
                currentSection: 0,
                totalSections: template.sections.length,
                inferredData: {},
                userAnswers: {},
                pendingQuestions: [],
                completedSections: [],
                sectionOutputs: {},
                sectionChunks: {}
            };
        }

        const total = template.sections.length;

        // Phase 1: Folder mapping
        progress({ phase: 1, section: 0, total, message: 'Mapping sections to data folders...' });
        let folderMappings;
        try {
            folderMappings = await this.mapSectionsToFolders(template);
        } catch (err) {
            PipelineLog.log(`Folder mapping failed: ${err.message}`);
            folderMappings = [];
        }

        // Phase 2: Generate each section
        const startFrom = manifest.currentSection;
        for (let i = startFrom; i < total; i++) {
            const section = template.sections[i];
            progress({
                phase: 2,
                section: i + 1,
                total,
                message: `Section ${i + 1}/${total}: ${section.title}`,
                pct: ((i + 1) / (total + 1)) * 100
            });

            let retries = 1;
            let success = false;

            while (retries >= 0 && !success) {
                try {
                    // Phase 2a-2b: Gather data
                    const dataChunks = await this.gatherSectionData(section, folderMappings, subLog);

                    // Store chunk metadata for traceability (without heavy content)
                    manifest.sectionChunks[i] = dataChunks.map(c => ({
                        fileId: c.fileId,
                        folder: c.folder,
                        filename: c.filename,
                        fileTitle: c.fileTitle || c.filename,
                        type: c.type,
                        reason: c.reason,
                        contentIndex: c.contentIndex,
                        contentHeading: c.contentHeading
                    }));

                    // Phase 2c-2d: Generate section
                    const result = await this.generateSection(template, i, dataChunks, manifest, subLog);

                    // Emit questions
                    if (result.questions && result.questions.length > 0) {
                        for (const q of result.questions) {
                            manifest.pendingQuestions.push(q);
                            askQuestion(q);
                        }
                    }

                    success = true;
                } catch (err) {
                    retries--;
                    if (retries < 0) {
                        PipelineLog.log(`Section ${i + 1} failed: ${err.message}`);
                        manifest.sectionOutputs[i] = {
                            title: section.title,
                            narratives: [`[GENERATION FAILED: ${err.message}]`],
                            tables: [],
                            bulletPoints: []
                        };
                        manifest.completedSections.push({
                            index: i,
                            title: section.title,
                            summary: 'Generation failed'
                        });
                        manifest.currentSection = i + 1;
                    } else {
                        PipelineLog.log(`Section ${i + 1} error, retrying: ${err.message}`);
                    }
                }
            }

            // Save after each section for crash recovery
            this.saveManifest(manifest);
        }

        manifest.status = 'sections-complete';
        this.saveManifest(manifest);

        // Phase 3: Cross-check
        progress({ phase: 3, section: total, total, message: 'Cross-checking report...', pct: (total / (total + 1)) * 100 });
        try {
            await this.crossCheck(manifest, template);
        } catch (err) {
            PipelineLog.log(`Cross-check failed: ${err.message}`);
        }

        manifest.status = 'ready';
        this.saveManifest(manifest);

        progress({ phase: 4, section: total, total, message: 'Report generation complete', pct: 100 });
        PipelineLog.log('Report generation complete');

        return manifest;
    },

    // ---- Manifest Persistence ----

    getSavedManifest() {
        try {
            return JSON.parse(localStorage.getItem(this.MANIFEST_KEY));
        } catch {
            return null;
        }
    },

    saveManifest(manifest) {
        localStorage.setItem(this.MANIFEST_KEY, JSON.stringify(manifest));
    },

    clearManifest() {
        localStorage.removeItem(this.MANIFEST_KEY);
    },

    // ---- Phase 4: Word Document Rendering ----

    async renderDocx(manifest, template) {
        PipelineLog.log('Rendering Word document...');

        const {
            Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
            Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
            ShadingType, PageNumber, PageBreak, LevelFormat, TabStopType, TabStopPosition
        } = window.docx;

        const navy = '1A1A2E';
        const accent = '00D4AA';
        const contentWidthDxa = 9360; // 8.5" - 2×1" margins in DXA

        const border = { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' };
        const cellBorders = { top: border, bottom: border, left: border, right: border };

        // ---- Cover page children ----
        const titleText = manifest.inferredData.reportTitle || template.title || 'Inspection Report';
        const coverFields = [
            ['Client', manifest.inferredData.client || manifest.userAnswers.client || '\u2014'],
            ['Facility', manifest.inferredData.facility || manifest.userAnswers.facility || '\u2014'],
            ['Report No.', manifest.userAnswers.report_number || manifest.inferredData.report_number || '\u2014'],
            ['Date', manifest.inferredData.inspection_date || manifest.userAnswers.inspection_date || new Date().toLocaleDateString()]
        ];

        const coverChildren = [
            // Spacer
            new Paragraph({ spacing: { before: 4800 }, children: [] }),
            // Title
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 200 },
                children: [new TextRun({ text: titleText, bold: true, size: 48, font: 'Arial', color: navy })]
            }),
            // Report type
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 1200 },
                children: [new TextRun({ text: template.reportType || 'Inspection Report', size: 28, font: 'Arial', color: accent })]
            })
        ];

        // Cover metadata table
        const metaRows = coverFields.map(([label, value]) =>
            new TableRow({
                children: [
                    new TableCell({
                        borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } },
                        width: { size: 3000, type: WidthType.DXA },
                        children: [new Paragraph({
                            alignment: AlignmentType.RIGHT,
                            spacing: { after: 80 },
                            children: [new TextRun({ text: `${label}:`, bold: true, size: 22, font: 'Arial', color: '3C3C50' })]
                        })]
                    }),
                    new TableCell({
                        borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } },
                        width: { size: 4000, type: WidthType.DXA },
                        children: [new Paragraph({
                            spacing: { after: 80 },
                            children: [new TextRun({ text: value, size: 22, font: 'Arial', color: '3C3C50' })]
                        })]
                    })
                ]
            })
        );

        coverChildren.push(new Table({
            width: { size: 7000, type: WidthType.DXA },
            columnWidths: [3000, 4000],
            alignment: AlignmentType.CENTER,
            rows: metaRows
        }));

        // ---- Build global reference map for traceability ----
        const globalRefMap = new Map(); // dedupKey -> { ref, fileTitle, folder, type, reason, sections }
        const refBySection = new Map(); // sectionIndex -> Map(chunkIndex -> globalRefNumber)
        let refCounter = 1;

        if (manifest.sectionChunks) {
            for (const [secIdx, chunks] of Object.entries(manifest.sectionChunks)) {
                const sectionTitle = (manifest.sectionOutputs[secIdx] || {}).title || (template.sections[secIdx] || {}).title || `Section ${parseInt(secIdx) + 1}`;
                const localMap = new Map(); // chunkIndex -> globalRefNumber

                (chunks || []).forEach((chunk, chunkIdx) => {
                    const dedupKey = `${chunk.fileId}||${chunk.type}`;
                    if (!globalRefMap.has(dedupKey)) {
                        globalRefMap.set(dedupKey, {
                            ref: refCounter++,
                            fileTitle: chunk.fileTitle,
                            folder: chunk.folder,
                            type: chunk.type,
                            reason: chunk.reason,
                            sections: new Set()
                        });
                    }
                    const entry = globalRefMap.get(dedupKey);
                    entry.sections.add(sectionTitle);
                    localMap.set(chunkIdx, entry.ref);
                });

                refBySection.set(parseInt(secIdx), localMap);
            }
        }

        // ---- Helper: build TextRuns with inline citation superscripts ----
        function buildCitedRuns(text, sources, sectionIndex) {
            const localMap = refBySection.get(sectionIndex);
            if (!sources || !sources.length || !localMap) {
                return [new TextRun({ text, size: 20, font: 'Arial', color: '282832' })];
            }

            const runs = [];
            const regex = /\[(\d+)\]/g;
            let lastIndex = 0;
            let match;

            while ((match = regex.exec(text)) !== null) {
                // Text before the bracket
                if (match.index > lastIndex) {
                    runs.push(new TextRun({ text: text.slice(lastIndex, match.index), size: 20, font: 'Arial', color: '282832' }));
                }

                const chunkIdx = parseInt(match[1]);
                const globalRef = localMap.get(chunkIdx);
                if (globalRef !== undefined) {
                    runs.push(new TextRun({ text: `[${globalRef}]`, superScript: true, size: 16, font: 'Arial', color: '0066CC' }));
                } else {
                    // Invalid index — render as plain text
                    console.log(`[Report] Invalid chunk index [${chunkIdx}] in section ${sectionIndex}`);
                    runs.push(new TextRun({ text: match[0], size: 20, font: 'Arial', color: '282832' }));
                }

                lastIndex = match.index + match[0].length;
            }

            // Remaining text after last match
            if (lastIndex < text.length) {
                runs.push(new TextRun({ text: text.slice(lastIndex), size: 20, font: 'Arial', color: '282832' }));
            }

            return runs.length > 0 ? runs : [new TextRun({ text, size: 20, font: 'Arial', color: '282832' })];
        }

        // ---- Section children ----
        const sectionChildren = [];

        for (let i = 0; i < template.sections.length; i++) {
            const output = manifest.sectionOutputs[i];
            if (!output) continue;

            // Page break before each section
            sectionChildren.push(new Paragraph({ children: [new PageBreak()] }));

            // Section heading
            const heading = output.title || template.sections[i].title;
            sectionChildren.push(new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: heading })]
            }));

            // Accent underline
            sectionChildren.push(new Paragraph({
                border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: accent, space: 1 } },
                spacing: { after: 240 },
                children: []
            }));

            // Narratives
            if (output.narratives && output.narratives.length > 0) {
                for (const para of output.narratives) {
                    if (typeof para === 'string') {
                        sectionChildren.push(new Paragraph({
                            spacing: { after: 200 },
                            children: [new TextRun({ text: para, size: 20, font: 'Arial', color: '282832' })]
                        }));
                    } else if (para && typeof para === 'object' && para.text) {
                        sectionChildren.push(new Paragraph({
                            spacing: { after: 200 },
                            children: buildCitedRuns(para.text, para.sources, i)
                        }));
                    }
                }
            }

            // Bullet points
            if (output.bulletPoints && output.bulletPoints.length > 0) {
                for (const bullet of output.bulletPoints) {
                    if (typeof bullet === 'string') {
                        sectionChildren.push(new Paragraph({
                            numbering: { reference: 'bullets', level: 0 },
                            spacing: { after: 80 },
                            children: [new TextRun({ text: bullet, size: 20, font: 'Arial', color: '282832' })]
                        }));
                    } else if (bullet && typeof bullet === 'object' && bullet.text) {
                        sectionChildren.push(new Paragraph({
                            numbering: { reference: 'bullets', level: 0 },
                            spacing: { after: 80 },
                            children: buildCitedRuns(bullet.text, bullet.sources, i)
                        }));
                    }
                }
                // Extra spacing after bullets
                sectionChildren.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
            }

            // Tables
            if (output.tables && output.tables.length > 0) {
                for (const table of output.tables) {
                    if (!table.headers || !table.rows) continue;

                    if (table.title) {
                        sectionChildren.push(new Paragraph({
                            spacing: { before: 200, after: 100 },
                            children: [new TextRun({ text: table.title, bold: true, size: 20, font: 'Arial', color: navy })]
                        }));
                    }

                    const colCount = table.headers.length;
                    const colWidth = Math.floor(contentWidthDxa / colCount);
                    const columnWidths = Array(colCount).fill(colWidth);
                    // Adjust last column to account for rounding
                    columnWidths[colCount - 1] = contentWidthDxa - colWidth * (colCount - 1);

                    // Header row
                    const headerRow = new TableRow({
                        children: table.headers.map((h, ci) => new TableCell({
                            borders: cellBorders,
                            width: { size: columnWidths[ci], type: WidthType.DXA },
                            shading: { fill: navy, type: ShadingType.CLEAR },
                            margins: { top: 80, bottom: 80, left: 120, right: 120 },
                            children: [new Paragraph({
                                children: [new TextRun({ text: String(h), bold: true, size: 16, font: 'Arial', color: 'F0F0F5' })]
                            })]
                        }))
                    });

                    // Data rows (with optional rowSources citations)
                    const localMap = refBySection.get(i);
                    const dataRows = table.rows.map((row, ri) => {
                        const cells = row.map((cell, ci) => {
                            const isLastCol = ci === row.length - 1;
                            const rowRefs = (table.rowSources && table.rowSources[ri]) || [];
                            const cellRuns = [new TextRun({ text: String(cell), size: 16, font: 'Arial', color: '282832' })];

                            // Append superscript citation to last cell if rowSources exist
                            if (isLastCol && rowRefs.length > 0 && localMap) {
                                const refNums = rowRefs.map(idx => localMap.get(idx)).filter(r => r !== undefined);
                                if (refNums.length > 0) {
                                    cellRuns.push(new TextRun({ text: ` [${refNums.join(',')}]`, superScript: true, size: 14, font: 'Arial', color: '0066CC' }));
                                }
                            }

                            return new TableCell({
                                borders: cellBorders,
                                width: { size: columnWidths[ci], type: WidthType.DXA },
                                shading: ri % 2 === 1 ? { fill: 'F5F5FA', type: ShadingType.CLEAR } : undefined,
                                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                                children: [new Paragraph({ children: cellRuns })]
                            });
                        });
                        return new TableRow({ children: cells });
                    });

                    sectionChildren.push(new Table({
                        width: { size: contentWidthDxa, type: WidthType.DXA },
                        columnWidths,
                        rows: [headerRow, ...dataRows]
                    }));

                    // Spacing after table
                    sectionChildren.push(new Paragraph({ spacing: { after: 240 }, children: [] }));
                }
            }
        }

        // ---- Traceability Matrix (final section) ----
        if (manifest.sectionChunks && globalRefMap.size > 0) {
            sectionChildren.push(new Paragraph({ children: [new PageBreak()] }));

            sectionChildren.push(new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: 'Traceability Matrix' })]
            }));

            sectionChildren.push(new Paragraph({
                border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: accent, space: 1 } },
                spacing: { after: 240 },
                children: []
            }));

            sectionChildren.push(new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: 'The table below maps each item in this report to its source document.', size: 20, font: 'Arial', color: '282832' })]
            }));

            const matrixHeaders = ['Ref', 'Report Section(s)', 'Source Document', 'Folder', 'Type', 'Relevance'];
            const matrixColWidths = [550, 1700, 2800, 1300, 900, 2110];

            const matrixHeaderRow = new TableRow({
                children: matrixHeaders.map((h, ci) => new TableCell({
                    borders: cellBorders,
                    width: { size: matrixColWidths[ci], type: WidthType.DXA },
                    shading: { fill: navy, type: ShadingType.CLEAR },
                    margins: { top: 80, bottom: 80, left: 120, right: 120 },
                    children: [new Paragraph({
                        children: [new TextRun({ text: h, bold: true, size: 16, font: 'Arial', color: 'F0F0F5' })]
                    })]
                }))
            });

            // Sort by ref number
            const sortedEntries = [...globalRefMap.values()].sort((a, b) => a.ref - b.ref);

            const matrixDataRows = sortedEntries.map((entry, ri) => {
                const rowData = [
                    String(entry.ref),
                    [...entry.sections].join(', '),
                    entry.fileTitle || '',
                    entry.folder || '',
                    entry.type || '',
                    entry.reason || ''
                ];
                return new TableRow({
                    children: rowData.map((cell, ci) => new TableCell({
                        borders: cellBorders,
                        width: { size: matrixColWidths[ci], type: WidthType.DXA },
                        shading: ri % 2 === 1 ? { fill: 'F5F5FA', type: ShadingType.CLEAR } : undefined,
                        margins: { top: 80, bottom: 80, left: 120, right: 120 },
                        children: [new Paragraph({
                            children: [new TextRun({ text: cell, size: 16, font: 'Arial', color: '282832' })]
                        })]
                    }))
                });
            });

            sectionChildren.push(new Table({
                width: { size: contentWidthDxa, type: WidthType.DXA },
                columnWidths: matrixColWidths,
                rows: [matrixHeaderRow, ...matrixDataRows]
            }));

            sectionChildren.push(new Paragraph({ spacing: { after: 240 }, children: [] }));
        }

        // ---- Build Document ----
        const doc = new Document({
            styles: {
                default: { document: { run: { font: 'Arial', size: 24 } } },
                paragraphStyles: [
                    {
                        id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
                        run: { size: 32, bold: true, font: 'Arial', color: navy },
                        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 }
                    },
                    {
                        id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
                        run: { size: 28, bold: true, font: 'Arial', color: navy },
                        paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 1 }
                    }
                ]
            },
            numbering: {
                config: [{
                    reference: 'bullets',
                    levels: [{
                        level: 0,
                        format: LevelFormat.BULLET,
                        text: '\u2022',
                        alignment: AlignmentType.LEFT,
                        style: { paragraph: { indent: { left: 720, hanging: 360 } } }
                    }]
                }]
            },
            sections: [
                {
                    properties: {
                        page: {
                            size: { width: 12240, height: 15840 },
                            margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
                        }
                    },
                    headers: {
                        default: new Header({
                            children: [new Paragraph({
                                children: [
                                    new TextRun({ text: template.title || 'Inspection Report', size: 16, font: 'Arial', color: '78788C' }),
                                    new TextRun({ text: '\t', size: 16 })
                                ],
                                tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }]
                            })]
                        })
                    },
                    footers: {
                        default: new Footer({
                            children: [new Paragraph({
                                alignment: AlignmentType.CENTER,
                                children: [
                                    new TextRun({ text: 'Page ', size: 16, font: 'Arial', color: '78788C' }),
                                    new TextRun({ children: [PageNumber.CURRENT], size: 16, font: 'Arial', color: '78788C' }),
                                    new TextRun({ text: ' of ', size: 16, font: 'Arial', color: '78788C' }),
                                    new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, font: 'Arial', color: '78788C' })
                                ]
                            })]
                        })
                    },
                    children: [...coverChildren, ...sectionChildren]
                }
            ]
        });

        // ---- Generate and download ----
        const buffer = await Packer.toBlob(doc);
        const client = manifest.inferredData.client || 'Report';
        const date = new Date().toISOString().slice(0, 10);
        const safeName = client.replace(/[^a-zA-Z0-9]/g, '_');
        const filename = `${safeName}_${template.reportType.replace(/\s+/g, '_')}_${date}.docx`;

        const url = URL.createObjectURL(buffer);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        PipelineLog.log('Word document downloaded');
    },

    // ---- Phase 5: HTML Preview Rendering ----

    renderHtml(manifest, template) {
        // Build global reference map (same logic as renderDocx)
        const globalRefMap = new Map();
        const refBySection = new Map();
        const chunkMetaMap = new Map();
        let refCounter = 1;

        if (manifest.sectionChunks) {
            for (const [secIdx, chunks] of Object.entries(manifest.sectionChunks)) {
                const sectionTitle = (manifest.sectionOutputs[secIdx] || {}).title
                    || (template.sections[secIdx] || {}).title
                    || `Section ${parseInt(secIdx) + 1}`;
                const localMap = new Map();

                (chunks || []).forEach((chunk, chunkIdx) => {
                    chunkMetaMap.set(`${secIdx}:${chunkIdx}`, chunk);
                    const dedupKey = `${chunk.fileId}||${chunk.type}`;
                    if (!globalRefMap.has(dedupKey)) {
                        globalRefMap.set(dedupKey, {
                            ref: refCounter++,
                            fileId: chunk.fileId,
                            fileTitle: chunk.fileTitle,
                            folder: chunk.folder,
                            type: chunk.type,
                            reason: chunk.reason,
                            contentIndex: chunk.contentIndex,
                            contentHeading: chunk.contentHeading,
                            sections: new Set()
                        });
                    }
                    const entry = globalRefMap.get(dedupKey);
                    entry.sections.add(sectionTitle);
                    localMap.set(chunkIdx, entry.ref);
                });

                refBySection.set(parseInt(secIdx), localMap);
            }
        }

        // Reverse lookup: ref number -> globalRefMap entry
        const refToEntry = new Map();
        for (const entry of globalRefMap.values()) {
            refToEntry.set(entry.ref, entry);
        }

        function esc(str) {
            return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
        }

        function buildCitedHtml(text, sources, sectionIndex) {
            const localMap = refBySection.get(sectionIndex);
            const escaped = esc(text);
            if (!sources || !sources.length || !localMap) return escaped;

            return escaped.replace(/\[(\d+)\]/g, (match, idx) => {
                const chunkIdx = parseInt(idx);
                const globalRef = localMap.get(chunkIdx);
                if (globalRef === undefined) return match;

                const chunk = chunkMetaMap.get(`${sectionIndex}:${chunkIdx}`);
                if (!chunk) return `<span class="report-cite">[${globalRef}]</span>`;

                return `<a class="report-cite" data-ref="${globalRef}" data-file-id="${esc(chunk.fileId)}" data-type="${esc(chunk.type)}" data-content-index="${chunk.contentIndex != null ? chunk.contentIndex : ''}" data-content-heading="${esc(chunk.contentHeading || '')}" title="Source: ${esc(chunk.fileTitle || chunk.filename)}">[${globalRef}]</a>`;
            });
        }

        let html = '<div class="report-preview">';

        // Cover
        const titleText = manifest.inferredData.reportTitle || template.title || 'Inspection Report';
        html += `<div class="rp-cover">`;
        html += `<h1 class="rp-title">${esc(titleText)}</h1>`;
        html += `<div class="rp-subtitle">${esc(template.reportType || 'Inspection Report')}</div>`;

        const coverFields = [
            ['Client', manifest.inferredData.client || manifest.userAnswers.client || '\u2014'],
            ['Facility', manifest.inferredData.facility || manifest.userAnswers.facility || '\u2014'],
            ['Report No.', manifest.userAnswers.report_number || manifest.inferredData.report_number || '\u2014'],
            ['Date', manifest.inferredData.inspection_date || manifest.userAnswers.inspection_date || new Date().toLocaleDateString()]
        ];
        html += '<table class="rp-meta-table">';
        for (const [label, value] of coverFields) {
            html += `<tr><td class="rp-meta-label">${esc(label)}:</td><td class="rp-meta-value">${esc(value)}</td></tr>`;
        }
        html += '</table></div>';

        // Sections
        for (let i = 0; i < template.sections.length; i++) {
            const output = manifest.sectionOutputs[i];
            if (!output) continue;

            const heading = output.title || template.sections[i].title;
            html += `<div class="rp-section">`;
            html += `<h2>${esc(heading)}</h2>`;

            if (output.dataGaps && output.dataGaps.length > 0) {
                html += '<div class="rp-data-gaps">';
                html += '<strong>Missing data:</strong> ';
                html += output.dataGaps.map(g => esc(g)).join(' | ');
                html += '</div>';
            }

            // Narratives
            if (output.narratives) {
                for (const para of output.narratives) {
                    if (typeof para === 'string') {
                        html += `<p>${esc(para)}</p>`;
                    } else if (para && para.text) {
                        const chunk = para.sources && para.sources[0] != null ? chunkMetaMap.get(`${i}:${para.sources[0]}`) : null;
                        const tooltip = chunk ? `Source: ${chunk.fileTitle || chunk.filename}` : '';
                        html += `<p class="report-sourced" title="${esc(tooltip)}">${buildCitedHtml(para.text, para.sources, i)}</p>`;
                    }
                }
            }

            // Bullet points
            if (output.bulletPoints && output.bulletPoints.length > 0) {
                html += '<ul>';
                for (const bullet of output.bulletPoints) {
                    if (typeof bullet === 'string') {
                        html += `<li>${esc(bullet)}</li>`;
                    } else if (bullet && bullet.text) {
                        const chunk = bullet.sources && bullet.sources[0] != null ? chunkMetaMap.get(`${i}:${bullet.sources[0]}`) : null;
                        const tooltip = chunk ? `Source: ${chunk.fileTitle || chunk.filename}` : '';
                        html += `<li class="report-sourced" title="${esc(tooltip)}">${buildCitedHtml(bullet.text, bullet.sources, i)}</li>`;
                    }
                }
                html += '</ul>';
            }

            // Tables
            if (output.tables) {
                const localMap = refBySection.get(i);
                for (const table of output.tables) {
                    if (!table.headers || !table.rows) continue;
                    if (table.title) {
                        html += `<div class="rp-table-title">${esc(table.title)}</div>`;
                    }
                    html += '<table class="rp-table"><thead><tr>';
                    for (const h of table.headers) {
                        html += `<th>${esc(h)}</th>`;
                    }
                    html += '</tr></thead><tbody>';
                    table.rows.forEach((row, ri) => {
                        const rowClass = ri % 2 === 1 ? ' class="rp-alt-row"' : '';
                        html += `<tr${rowClass}>`;
                        row.forEach((cell, ci) => {
                            let cellHtml = esc(cell);
                            // Append citation to last cell if rowSources exist
                            if (ci === row.length - 1 && table.rowSources && table.rowSources[ri] && localMap) {
                                const refNums = table.rowSources[ri].map(idx => localMap.get(idx)).filter(r => r !== undefined);
                                if (refNums.length > 0) {
                                    const chunk = chunkMetaMap.get(`${i}:${table.rowSources[ri][0]}`);
                                    if (chunk) {
                                        cellHtml += ` <a class="report-cite" data-ref="${refNums[0]}" data-file-id="${esc(chunk.fileId)}" data-type="${esc(chunk.type)}" data-content-index="${chunk.contentIndex != null ? chunk.contentIndex : ''}" data-content-heading="${esc(chunk.contentHeading || '')}" title="Source: ${esc(chunk.fileTitle || chunk.filename)}">[${refNums.join(',')}]</a>`;
                                    }
                                }
                            }
                            html += `<td>${cellHtml}</td>`;
                        });
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                }
            }

            html += '</div>';
        }

        // Traceability Matrix
        if (globalRefMap.size > 0) {
            html += '<div class="rp-section">';
            html += '<h2>Traceability Matrix</h2>';
            html += '<p>The table below maps each item in this report to its source document.</p>';
            html += '<table class="rp-table"><thead><tr><th>Ref</th><th>Report Section(s)</th><th>Source Document</th><th>Folder</th><th>Type</th><th>Relevance</th></tr></thead><tbody>';

            const sorted = [...globalRefMap.values()].sort((a, b) => a.ref - b.ref);
            sorted.forEach((entry, ri) => {
                const rowClass = ri % 2 === 1 ? ' class="rp-alt-row"' : '';
                html += `<tr${rowClass}>`;
                html += `<td>${entry.ref}</td>`;
                html += `<td>${esc([...entry.sections].join(', '))}</td>`;
                html += `<td>${esc(entry.fileTitle || '')}</td>`;
                html += `<td>${esc(entry.folder || '')}</td>`;
                html += `<td>${esc(entry.type || '')}</td>`;
                html += `<td>${esc(entry.reason || '')}</td>`;
                html += '</tr>';
            });

            html += '</tbody></table></div>';
        }

        html += '</div>';
        return html;
    }
};
