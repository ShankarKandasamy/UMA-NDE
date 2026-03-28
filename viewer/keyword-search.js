/**
 * KeywordSearch — FlexSearch-based keyword search over extraction JSONs.
 * Provides search-as-you-type with field-weighted results grouped by folder > file > match.
 */
const KeywordSearch = {
    _index: null,
    _nextId: 1,
    _records: new Map(),     // numericId -> full record
    _idMap: new Map(),       // numericId -> stringId
    _reverseMap: new Map(),  // stringId -> numericId
    _fileRecords: new Map(), // fileKey -> [numericIds]

    init() {
        this._index = new FlexSearch.Document({
            tokenize: 'forward',
            resolution: 9,
            document: {
                id: 'id',
                index: ['heading', 'keywords', 'text'],
                store: false
            }
        });
        this._nextId = 1;
        this._records.clear();
        this._idMap.clear();
        this._reverseMap.clear();
        this._fileRecords.clear();
    },

    async buildIndex() {
        const allFiles = await DevDB.listFiles();
        let count = 0;
        for (const file of allFiles) {
            if (!file.key.endsWith('_extraction.json')) continue;
            try {
                const text = await file.blob.text();
                const extraction = JSON.parse(text);
                const baseKey = file.key.replace(/_extraction\.json$/, '');
                const actualFileKey = this._resolveFileKey(baseKey, allFiles);
                count += this._addExtractionRecords(actualFileKey || baseKey, extraction);
            } catch (e) {
                console.warn('[KeywordSearch] Failed to parse:', file.key, e);
            }
        }
        console.log(`[KeywordSearch] Indexed ${count} records from ${this._fileRecords.size} files`);
    },

    _resolveFileKey(baseKey, allFiles) {
        const match = allFiles.find(f =>
            f.key.startsWith(baseKey + '.') && !f.key.endsWith('_extraction.json')
        );
        return match ? match.key : null;
    },

    addFile(fileKey, extraction) {
        this.removeFile(fileKey);
        const count = this._addExtractionRecords(fileKey, extraction);
        console.log(`[KeywordSearch] Added ${count} records for ${fileKey}`);
    },

    removeFile(fileKey) {
        const ids = this._fileRecords.get(fileKey);
        if (!ids) return;
        for (const numId of ids) {
            this._index.remove(numId);
            this._records.delete(numId);
            const strId = this._idMap.get(numId);
            if (strId) this._reverseMap.delete(strId);
            this._idMap.delete(numId);
        }
        this._fileRecords.delete(fileKey);
    },

    _allocId(stringId) {
        const numId = this._nextId++;
        this._idMap.set(numId, stringId);
        this._reverseMap.set(stringId, numId);
        return numId;
    },

    _addExtractionRecords(fileKey, extraction) {
        const parts = fileKey.split('/');
        const folder = parts[0];
        const file = parts.slice(1).join('/');
        const fileTitle = extraction.title || file;
        const keywords = (extraction.keywords || []).join(' ');
        const headingTree = extraction.headingTree || [];
        const numericIds = [];

        const addRecord = (stringId, record) => {
            record.keywords = keywords;
            const numId = this._allocId(stringId);
            this._index.add({ id: numId, heading: record.heading, keywords: record.keywords, text: record.text });
            this._records.set(numId, record);
            numericIds.push(numId);
        };

        // File-level summary record (ensures every file is searchable by keywords,
        // title, summary, ocr_text, observations, anomalies — even if no sub-arrays exist)
        const summaryParts = [];
        if (extraction.summary) summaryParts.push(extraction.summary);
        if (extraction.ocr_text) summaryParts.push(extraction.ocr_text);
        if (extraction.observations) summaryParts.push(extraction.observations.join(' '));
        if (extraction.anomalies) summaryParts.push(extraction.anomalies.join(' '));
        if (extraction.components) {
            summaryParts.push(extraction.components.map(c => `${c.tag || ''} ${c.type || ''} ${c.description || ''}`).join(' '));
        }
        addRecord(`${fileKey}::summary`, {
            folder, file, fileKey, fileTitle,
            type: 'section',
            heading: extraction.title || '',
            text: summaryParts.join(' '),
            page: extraction.pages ? 1 : null
        });

        // Sections
        if (extraction.sections) {
            extraction.sections.forEach((section, i) => {
                let page = this._findPageForHeading(section.heading, headingTree);
                // Fallback: estimate page from section position within headingTree
                if (!page && headingTree.length > 0) {
                    const ratio = extraction.sections.length > 1
                        ? i / (extraction.sections.length - 1)
                        : 0;
                    const treeIdx = Math.min(
                        Math.round(ratio * (headingTree.length - 1)),
                        headingTree.length - 1
                    );
                    page = headingTree[treeIdx]?.page || 1;
                }
                addRecord(`${fileKey}::section:${i}`, {
                    folder, file, fileKey, fileTitle,
                    type: 'section',
                    heading: section.heading || '',
                    text: section.text || '',
                    page
                });
            });
        }

        // Tables
        if (extraction.tables) {
            extraction.tables.forEach((table, i) => {
                const textParts = [];
                if (table.headers) textParts.push(table.headers.join(' '));
                if (table.rows) {
                    table.rows.forEach(row => {
                        if (Array.isArray(row)) textParts.push(row.join(' '));
                    });
                }
                // Build rowOffsets: character position where each textPart starts in the joined string
                const rowOffsets = [];
                let offset = 0;
                for (let r = 0; r < textParts.length; r++) {
                    rowOffsets.push(offset);
                    offset += textParts[r].length + 1; // +1 for join(' ') separator
                }
                addRecord(`${fileKey}::table:${i}`, {
                    folder, file, fileKey, fileTitle,
                    type: 'table',
                    heading: table.title || '',
                    text: textParts.join(' '),
                    page: table.page || null,
                    rowOffsets
                });
            });
        }

        // Images
        if (extraction.images) {
            extraction.images.forEach((img, i) => {
                addRecord(`${fileKey}::image:${i}`, {
                    folder, file, fileKey, fileTitle,
                    type: 'image',
                    heading: img.description || '',
                    text: img.ocr_text || '',
                    page: img.page || null
                });
            });
        }

        // Charts
        if (extraction.charts) {
            extraction.charts.forEach((chart, i) => {
                const textParts = [];
                if (chart.insights) textParts.push(chart.insights);
                if (chart.data_points) {
                    chart.data_points.forEach(dp => {
                        textParts.push(`${dp.label || ''} ${dp.x || ''} ${dp.y || ''}`);
                    });
                }
                addRecord(`${fileKey}::chart:${i}`, {
                    folder, file, fileKey, fileTitle,
                    type: 'chart',
                    heading: chart.title || '',
                    text: textParts.join(' '),
                    page: chart.page || null
                });
            });
        }

        // Readings
        if (extraction.readings) {
            extraction.readings.forEach((reading, i) => {
                addRecord(`${fileKey}::reading:${i}`, {
                    folder, file, fileKey, fileTitle,
                    type: 'reading',
                    heading: reading.parameter || '',
                    text: `${reading.value || ''} ${reading.unit || ''}`.trim(),
                    page: null
                });
            });
        }

        this._fileRecords.set(fileKey, numericIds);
        return numericIds.length;
    },

    _findPageForHeading(heading, headingTree) {
        if (!heading || !headingTree.length) return null;
        const norm = heading.toLowerCase().trim();

        // 1. Exact match
        const exact = headingTree.find(h =>
            h.title && h.title.toLowerCase().trim() === norm
        );
        if (exact) return exact.page;

        // 2. Substring match (heading contains tree title or vice versa)
        const substring = headingTree.find(h => {
            if (!h.title) return false;
            const t = h.title.toLowerCase().trim();
            return norm.includes(t) || t.includes(norm);
        });
        if (substring) return substring.page;

        // 3. Word-overlap match (best overlap wins, minimum 50%)
        const normWords = new Set(norm.split(/\s+/).filter(w => w.length > 2));
        if (normWords.size === 0) return null;
        let bestPage = null;
        let bestRatio = 0;
        for (const h of headingTree) {
            if (!h.title || !h.page) continue;
            const treeWords = new Set(h.title.toLowerCase().trim().split(/\s+/).filter(w => w.length > 2));
            if (treeWords.size === 0) continue;
            let overlap = 0;
            for (const w of normWords) {
                if (treeWords.has(w)) overlap++;
            }
            const ratio = overlap / Math.max(normWords.size, treeWords.size);
            if (ratio > bestRatio && ratio >= 0.5) {
                bestRatio = ratio;
                bestPage = h.page;
            }
        }
        return bestPage;
    },

    search(query) {
        if (!this._index || !query || query.length < 2) {
            return { query, total: 0, groups: [] };
        }

        // Search each field separately for weighted scoring
        const headingHits = this._index.search(query, { index: 'heading' }) || [];
        const keywordHits = this._index.search(query, { index: 'keywords' }) || [];
        const textHits = this._index.search(query, { index: 'text' }) || [];

        // Score: heading match = 3, keyword match = 2, text match = 1
        const scores = new Map();
        const collectIds = (hits, weight) => {
            for (const fieldResult of hits) {
                const ids = fieldResult.result || [];
                for (const numId of ids) {
                    scores.set(numId, (scores.get(numId) || 0) + weight);
                }
            }
        };
        collectIds(headingHits, 3);
        collectIds(keywordHits, 2);
        collectIds(textHits, 1);

        if (scores.size === 0) {
            return { query, total: 0, groups: [] };
        }

        const matchedIds = [...scores.keys()];
        const queryLower = query.toLowerCase();
        const matches = [];

        // Expand each matched record into individual occurrence matches
        for (const numId of matchedIds) {
            const record = this._records.get(numId);
            if (!record) continue;
            const stringId = this._idMap.get(numId) || numId;
            const page = record.page;

            const base = {
                fileKey: record.fileKey,
                folder: record.folder,
                file: record.file,
                fileTitle: record.fileTitle,
                type: record.type,
                heading: record.heading,
                page
            };

            // Find all occurrences in heading (score 3 each)
            const headingOccurrences = this._findAllOccurrences(record.heading, queryLower);
            for (const charIdx of headingOccurrences) {
                matches.push({
                    ...base,
                    id: stringId,
                    snippet: this._generateSnippetAt(record.heading, queryLower, charIdx),
                    score: 3
                });
            }

            // Find all occurrences in text (score 1 each)
            const textOccurrences = this._findAllOccurrences(record.text, queryLower);
            for (const charIdx of textOccurrences) {
                const rowIndex = record.rowOffsets
                    ? this._charIdxToRow(record.rowOffsets, charIdx)
                    : null;
                matches.push({
                    ...base,
                    id: stringId,
                    snippet: this._generateSnippetAt(record.text, queryLower, charIdx),
                    score: 1,
                    rowIndex
                });
            }

            // Keyword-only match: no literal heading/text occurrences
            if (headingOccurrences.length === 0 && textOccurrences.length === 0) {
                const fallbackPage = page || this._secondaryScanForPage(record.fileKey, queryLower);
                matches.push({
                    ...base,
                    id: stringId,
                    page: fallbackPage,
                    snippet: this._generateSnippetAt(record.text || record.heading || '', queryLower, -1),
                    score: 2
                });
            }
        }

        // Suppress summary matches when file has specific chunk matches
        const filesWithSpecificMatches = new Set();
        for (const m of matches) {
            if (typeof m.id === 'string' && !m.id.endsWith('::summary')) {
                filesWithSpecificMatches.add(m.fileKey);
            }
        }
        const filtered = matches.filter(m => {
            if (typeof m.id === 'string' && m.id.endsWith('::summary') && filesWithSpecificMatches.has(m.fileKey)) {
                return false;
            }
            return true;
        });

        // Sort by score descending (heading 3 > keyword-only 2 > text 1)
        filtered.sort((a, b) => b.score - a.score);

        // Group by folder > file
        const folderMap = new Map();
        for (const match of filtered) {
            if (!folderMap.has(match.folder)) {
                folderMap.set(match.folder, new Map());
            }
            const fileMap = folderMap.get(match.folder);
            if (!fileMap.has(match.fileKey)) {
                fileMap.set(match.fileKey, {
                    fileKey: match.fileKey,
                    fileTitle: match.fileTitle,
                    fileName: match.file,
                    matches: []
                });
            }
            fileMap.get(match.fileKey).matches.push({
                id: match.id,
                type: match.type,
                heading: match.heading,
                snippet: match.snippet,
                page: match.page,
                score: match.score,
                rowIndex: match.rowIndex
            });
        }

        const groups = [];
        for (const [folder, fileMap] of folderMap) {
            groups.push({
                folder,
                files: [...fileMap.values()]
            });
        }

        return { query, total: filtered.length, groups };
    },

    _secondaryScanForPage(fileKey, queryLower) {
        const ids = this._fileRecords.get(fileKey) || [];
        for (const numId of ids) {
            const r = this._records.get(numId);
            if (!r) continue;
            if (r.text && r.text.toLowerCase().includes(queryLower) && r.page) return r.page;
            if (r.heading && r.heading.toLowerCase().includes(queryLower) && r.page) return r.page;
        }
        return null;
    },

    _charIdxToRow(rowOffsets, charIdx) {
        if (!rowOffsets || rowOffsets.length === 0) return null;
        let lo = 0, hi = rowOffsets.length - 1;
        while (lo < hi) {
            const mid = (lo + hi + 1) >> 1;
            if (rowOffsets[mid] <= charIdx) lo = mid;
            else hi = mid - 1;
        }
        return lo;
    },

    _findAllOccurrences(source, queryLower) {
        if (!source) return [];
        const indices = [];
        const lower = source.toLowerCase();
        let pos = 0;
        while (true) {
            const idx = lower.indexOf(queryLower, pos);
            if (idx === -1) break;
            indices.push(idx);
            pos = idx + queryLower.length;
        }
        return indices;
    },

    _generateSnippetAt(source, queryLower, charIndex) {
        if (!source) return '';
        if (charIndex === -1) {
            // No literal match — return start of text
            return source.length > 120 ? source.substring(0, 120) + '...' : source;
        }

        const contextRadius = 60;
        const start = Math.max(0, charIndex - contextRadius);
        const end = Math.min(source.length, charIndex + queryLower.length + contextRadius);
        let snippet = '';
        if (start > 0) snippet += '...';
        snippet += source.substring(start, end);
        if (end < source.length) snippet += '...';
        return snippet;
    }
};
