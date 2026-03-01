// ============================================
// Hierarchical Relevance Search Pipeline
// ============================================
// 3-stage "zoom-in" retrieval:
//   Stage 1: Score folders (GPT-4o-mini via OpenAI proxy)
//   Stage 2: Score files within relevant folders (GPT-4o-mini)
//   Stage 3: Retrieve relevant sections from top files (GPT-4.1)

const Search = {
    SCORE_THRESHOLD: 0.5,

    // ---- LLM Call Helpers ----

    async callOpenAI(model, systemMsg, userMsg) {
        if (!settings.openaiKey || !settings.apiEndpoint) {
            throw new Error('OpenAI API key or API endpoint not configured. Add your OpenAI key in Settings.');
        }

        const body = {
            model,
            temperature: 0,
            response_format: { type: 'json_object' },
            messages: [
                { role: 'system', content: systemMsg },
                { role: 'user', content: userMsg }
            ]
        };

        const response = await fetch(`${settings.apiEndpoint}/llm/openai`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': settings.apiKey,
                'X-OpenAI-Key': settings.openaiKey
            },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            const errText = await response.text();
            throw new Error(`OpenAI API error ${response.status}: ${errText}`);
        }

        const data = await response.json();
        const rawText = data.choices[0].message.content;

        if (data.usage) {
            console.log(`[Search] OpenAI ${model} — input: ${data.usage.prompt_tokens}, output: ${data.usage.completion_tokens}`);
        }

        return JSON.parse(rawText);
    },

    async callAnthropic(model, systemMsg, userMsg) {
        if (!settings.anthropicKey || !settings.apiEndpoint) {
            throw new Error('Anthropic API key or API endpoint not configured.');
        }

        const body = {
            model,
            max_tokens: 4096,
            system: systemMsg,
            messages: [{ role: 'user', content: userMsg }]
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
            console.log(`[Search] Anthropic ${model} — input: ${data.usage.input_tokens}, output: ${data.usage.output_tokens}`);
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

    // ---- Stage 1: Folder Scoring ----

    async scoreFolders(query) {
        console.log('[Search] Stage 1: Scoring folders...');

        const devFolders = await DevDB.listSubfolders();
        const folders = [];

        for (const folderName of devFolders) {
            if (folderName === 'Uncategorized') continue;
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
            console.log('[Search] No folder summaries available');
            return [];
        }

        const userMsg = `Query: "${query}"\n\nFolders:\n${folders.map(f =>
            `- "${f.id}" (${f.fileCount} files)\n  Summary: ${f.summary}\n  Keywords: ${f.keywords.join(', ')}`
        ).join('\n\n')}`;

        const result = await this.callOpenAI('gpt-4o-mini', SEARCH_SCORING_SYSTEM_MSG, userMsg + '\n\n' + FOLDER_SCORING_PROMPT);

        const scored = (result.results || [])
            .filter(r => r.score >= this.SCORE_THRESHOLD)
            .sort((a, b) => b.score - a.score);

        console.log(`[Search] Stage 1 results: ${scored.length} folders above threshold (${folders.length} total)`);
        scored.forEach(r => console.log(`  ${r.folderId}: ${r.score.toFixed(2)}`));

        return scored;
    },

    // ---- Stage 2: File Scoring ----

    async scoreFiles(query, folderIds) {
        console.log(`[Search] Stage 2: Scoring files in ${folderIds.length} folders...`);

        const files = [];

        for (const folderId of folderIds) {
            const folderFiles = await DevDB.listFiles(folderId);
            const extractionFiles = folderFiles.filter(f => f.key.endsWith('_extraction.json'));

            for (const extFile of extractionFiles) {
                try {
                    const text = await extFile.blob.text();
                    const extraction = JSON.parse(text);
                    // Derive the source filename from the extraction key
                    const extFilename = extFile.key.split('/').pop();
                    const sourceFilename = extFilename.replace(/_extraction\.json$/, '');

                    files.push({
                        id: `${folderId}/${sourceFilename}`,
                        folder: folderId,
                        summary: extraction.summary || '',
                        keywords: extraction.keywords || [],
                        title: extraction.title || sourceFilename
                    });
                } catch (_) {
                    // Skip unparseable extraction
                }
            }
        }

        if (files.length === 0) {
            console.log('[Search] No file extractions available in relevant folders');
            return [];
        }

        const userMsg = `Query: "${query}"\n\nFiles:\n${files.map(f =>
            `- ID: "${f.id}"\n  Title: ${f.title}\n  Folder: ${f.folder}\n  Summary: ${f.summary}\n  Keywords: ${Array.isArray(f.keywords) ? f.keywords.join(', ') : f.keywords}`
        ).join('\n\n')}`;

        const result = await this.callOpenAI('gpt-4o-mini', SEARCH_SCORING_SYSTEM_MSG, userMsg + '\n\n' + FILE_SCORING_PROMPT);

        const scored = (result.results || [])
            .filter(r => r.score >= this.SCORE_THRESHOLD)
            .sort((a, b) => b.score - a.score);

        console.log(`[Search] Stage 2 results: ${scored.length} files above threshold (${files.length} total)`);
        scored.forEach(r => console.log(`  ${r.fileId}: ${r.score.toFixed(2)}`));

        return scored;
    },

    // ---- Stage 3: Section-Level Retrieval ----

    async retrieveSections(query, fileIds) {
        console.log(`[Search] Stage 3: Retrieving relevant sections from ${fileIds.length} files...`);

        const filesContent = [];

        for (const fileId of fileIds) {
            // fileId format: "FolderName/filename" (without extension)
            // The extraction key is: "FolderName/filename_extraction.json"
            const extKey = `${fileId}_extraction.json`;

            try {
                const extRecord = await DevDB.getFile(extKey);
                if (!extRecord || !extRecord.blob) continue;

                const text = await extRecord.blob.text();
                const extraction = JSON.parse(text);

                const fileContent = {
                    fileId,
                    title: extraction.title || fileId.split('/').pop()
                };

                // Add sections
                if (extraction.sections && extraction.sections.length > 0) {
                    fileContent.sections = extraction.sections.map((s, i) => ({
                        index: i,
                        heading: s.heading || `Section ${i + 1}`,
                        text: s.text || ''
                    }));
                }

                // Add tables
                if (extraction.tables && extraction.tables.length > 0) {
                    fileContent.tables = extraction.tables.map((t, i) => ({
                        index: i,
                        title: t.title || `Table ${i + 1}`,
                        headers: t.headers || [],
                        rows: t.rows || []
                    }));
                }

                // Add charts
                if (extraction.charts && extraction.charts.length > 0) {
                    fileContent.charts = extraction.charts.map((c, i) => ({
                        index: i,
                        title: c.title || `Chart ${i + 1}`,
                        type: c.type || 'unknown',
                        data: c.data || {},
                        insights: c.insights || ''
                    }));
                }

                // Add images
                if (extraction.images && extraction.images.length > 0) {
                    fileContent.images = extraction.images.map((img, i) => ({
                        index: i,
                        page: img.page,
                        description: img.description || '',
                        ocr_text: img.ocr_text || ''
                    }));
                }

                // Add readings (from image extractions)
                if (extraction.readings && extraction.readings.length > 0) {
                    fileContent.readings = extraction.readings.map((r, i) => ({
                        index: i,
                        parameter: r.parameter || '',
                        value: r.value || '',
                        unit: r.unit || ''
                    }));
                }

                // For image-type extractions, add observations, OCR text, components, and summary as pseudo-sections
                if (extraction.image_type) {
                    if (!fileContent.sections) fileContent.sections = [];

                    if (extraction.summary) {
                        fileContent.sections.push({
                            index: fileContent.sections.length,
                            heading: 'Summary',
                            text: extraction.summary
                        });
                    }

                    if (extraction.ocr_text) {
                        fileContent.sections.push({
                            index: fileContent.sections.length,
                            heading: 'OCR Text',
                            text: extraction.ocr_text
                        });
                    }

                    if (extraction.observations && extraction.observations.length > 0) {
                        fileContent.sections.push({
                            index: fileContent.sections.length,
                            heading: 'Observations',
                            text: extraction.observations.join('\n')
                        });
                    }

                    if (extraction.components && extraction.components.length > 0) {
                        fileContent.sections.push({
                            index: fileContent.sections.length,
                            heading: 'Components',
                            text: extraction.components.map(c =>
                                `${c.tag ? c.tag + ': ' : ''}${c.type} — ${c.description}`
                            ).join('\n')
                        });
                    }
                }

                // For spreadsheet-type extractions, add summary, observations, and file metadata as pseudo-sections
                if (extraction.spreadsheet_type) {
                    if (!fileContent.sections) fileContent.sections = [];

                    if (extraction.summary) {
                        fileContent.sections.push({
                            index: fileContent.sections.length,
                            heading: 'Summary',
                            text: extraction.summary
                        });
                    }

                    if (extraction.observations && extraction.observations.length > 0) {
                        fileContent.sections.push({
                            index: fileContent.sections.length,
                            heading: 'Observations',
                            text: extraction.observations.join('\n')
                        });
                    }

                    if (extraction.file_metadata) {
                        const fm = extraction.file_metadata;
                        fileContent.sections.push({
                            index: fileContent.sections.length,
                            heading: 'File Metadata',
                            text: `Filename: ${fm.filename}\nSheets: ${fm.sheet_count}\nTotal rows: ${fm.total_rows}\nTotal columns: ${fm.total_columns}\nFile size: ${fm.file_size}`
                        });
                    }
                }

                filesContent.push(fileContent);
            } catch (err) {
                console.warn(`[Search] Could not load extraction for ${fileId}:`, err);
            }
        }

        if (filesContent.length === 0) {
            console.log('[Search] No file content available for section retrieval');
            return [];
        }

        const userMsg = `Query: "${query}"\n\nFiles:\n${JSON.stringify(filesContent, null, 2)}`;

        // Use GPT-4.1 for the more demanding extraction task
        const result = await this.callOpenAI('gpt-4.1', SEARCH_SCORING_SYSTEM_MSG, userMsg + '\n\n' + SECTION_RETRIEVAL_PROMPT);

        console.log(`[Search] Stage 3 results: ${(result.results || []).length} files with relevant content`);

        return result.results || [];
    },

    // ---- Resolve Pointers to Content ----

    async resolvePointers(searchResults) {
        const resolved = [];

        for (const fileResult of searchResults) {
            const extKey = `${fileResult.fileId}_extraction.json`;
            try {
                const extRecord = await DevDB.getFile(extKey);
                if (!extRecord || !extRecord.blob) continue;

                const text = await extRecord.blob.text();
                const extraction = JSON.parse(text);
                const folder = fileResult.fileId.split('/')[0];
                const filename = fileResult.fileId.split('/').slice(1).join('/');

                for (const item of (fileResult.relevant || [])) {
                    const resolvedItem = {
                        fileId: fileResult.fileId,
                        folder,
                        filename,
                        fileTitle: extraction.title || filename,
                        type: item.type,
                        reason: item.reason,
                        content: null
                    };

                    const arr = extraction[item.type + 's'] || extraction[item.type] || [];
                    if (item.type === 'reading') {
                        const readings = extraction.readings || [];
                        if (readings[item.index]) {
                            resolvedItem.content = readings[item.index];
                        }
                    } else if (item.type === 'section') {
                        const sections = extraction.sections || [];
                        if (sections[item.index]) {
                            resolvedItem.content = sections[item.index];
                        } else if (extraction.image_type) {
                            // Resolve pseudo-sections for image extractions
                            // Reconstruct the same order used in retrieveSections
                            const pseudoSections = [];
                            if (extraction.summary) {
                                pseudoSections.push({ heading: 'Summary', text: extraction.summary });
                            }
                            if (extraction.ocr_text) {
                                pseudoSections.push({ heading: 'OCR Text', text: extraction.ocr_text });
                            }
                            if (extraction.observations && extraction.observations.length > 0) {
                                pseudoSections.push({ heading: 'Observations', text: extraction.observations.join('\n') });
                            }
                            if (extraction.components && extraction.components.length > 0) {
                                pseudoSections.push({
                                    heading: 'Components',
                                    text: extraction.components.map(c =>
                                        `${c.tag ? c.tag + ': ' : ''}${c.type} — ${c.description}`
                                    ).join('\n')
                                });
                            }
                            const pseudoIndex = item.index - sections.length;
                            if (pseudoIndex >= 0 && pseudoIndex < pseudoSections.length) {
                                resolvedItem.content = pseudoSections[pseudoIndex];
                            }
                        } else if (extraction.spreadsheet_type) {
                            // Resolve pseudo-sections for spreadsheet extractions
                            const pseudoSections = [];
                            if (extraction.summary) {
                                pseudoSections.push({ heading: 'Summary', text: extraction.summary });
                            }
                            if (extraction.observations && extraction.observations.length > 0) {
                                pseudoSections.push({ heading: 'Observations', text: extraction.observations.join('\n') });
                            }
                            if (extraction.file_metadata) {
                                const fm = extraction.file_metadata;
                                pseudoSections.push({
                                    heading: 'File Metadata',
                                    text: `Filename: ${fm.filename}\nSheets: ${fm.sheet_count}\nTotal rows: ${fm.total_rows}\nTotal columns: ${fm.total_columns}\nFile size: ${fm.file_size}`
                                });
                            }
                            const pseudoIndex = item.index - sections.length;
                            if (pseudoIndex >= 0 && pseudoIndex < pseudoSections.length) {
                                resolvedItem.content = pseudoSections[pseudoIndex];
                            }
                        }
                    } else if (item.type === 'table') {
                        const tables = extraction.tables || [];
                        if (tables[item.index]) {
                            resolvedItem.content = tables[item.index];
                        }
                    } else if (item.type === 'chart') {
                        const charts = extraction.charts || [];
                        if (charts[item.index]) {
                            resolvedItem.content = charts[item.index];
                        }
                    } else if (item.type === 'image') {
                        const images = extraction.images || [];
                        if (images[item.index]) {
                            resolvedItem.content = images[item.index];
                        }
                    }

                    if (resolvedItem.content) {
                        resolved.push(resolvedItem);
                    }
                }
            } catch (err) {
                console.warn(`[Search] Could not resolve pointers for ${fileResult.fileId}:`, err);
            }
        }

        return resolved;
    },

    // ---- Main Search Orchestrator ----

    async search(query, onProgress) {
        const progress = onProgress || (() => {});

        console.log(`[Search] Starting search: "${query}"`);
        const startTime = performance.now();

        // Stage 1: Score folders
        progress({ stage: 1, message: 'Scoring folder relevance...' });
        const scoredFolders = await this.scoreFolders(query);

        if (scoredFolders.length === 0) {
            progress({ stage: 1, message: 'No relevant folders found', done: true });
            return { folders: [], files: [], results: [], elapsed: performance.now() - startTime };
        }

        const folderIds = scoredFolders.map(f => f.folderId);

        // Stage 2: Score files
        progress({ stage: 2, message: `Scoring files in ${folderIds.length} folder${folderIds.length > 1 ? 's' : ''}...` });
        const scoredFiles = await this.scoreFiles(query, folderIds);

        if (scoredFiles.length === 0) {
            progress({ stage: 2, message: 'No relevant files found', done: true });
            return { folders: scoredFolders, files: [], results: [], elapsed: performance.now() - startTime };
        }

        const fileIds = scoredFiles.map(f => f.fileId);

        // Stage 3: Retrieve sections
        progress({ stage: 3, message: `Extracting relevant content from ${fileIds.length} file${fileIds.length > 1 ? 's' : ''}...` });
        const sectionResults = await this.retrieveSections(query, fileIds);

        // Resolve pointers to actual content
        progress({ stage: 3, message: 'Resolving content...' });
        const resolved = await this.resolvePointers(sectionResults);

        const elapsed = performance.now() - startTime;
        console.log(`[Search] Complete in ${(elapsed / 1000).toFixed(1)}s — ${resolved.length} results`);
        progress({ stage: 3, message: `Found ${resolved.length} result${resolved.length !== 1 ? 's' : ''}`, done: true });

        return {
            folders: scoredFolders,
            files: scoredFiles,
            results: resolved,
            elapsed
        };
    }
};
