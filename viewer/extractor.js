// ============================================
// Client-Side Text & Structure Extraction
// ============================================
// Pre-extracts text and heading trees from PDFs and DOCX files
// before sending to LLM, reducing token costs significantly.
// Dependencies: pdfjs-dist (global pdfjsLib), mammoth (global mammoth)

const Extractor = {

    // Detect file type from filename extension
    detectFileType(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        if (ext === 'pdf') return 'pdf';
        if (ext === 'docx') return 'docx';
        if (ext === 'doc') return 'doc-legacy';
        if (/^(csv|xlsx?|xls)$/.test(ext)) return 'spreadsheet';
        if (/^(jpg|jpeg|png|gif|webp|bmp|tiff?|heic|heif)$/.test(ext)) return 'image';
        return 'unknown';
    },

    // Extract text and heading tree from a PDF blob
    async extractPdfText(blob) {
        const arrayBuffer = await blob.arrayBuffer();
        const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        const pageCount = pdf.numPages;

        const pages = [];
        const fontSizes = [];

        // Pass 1: collect all text items with font sizes
        for (let i = 1; i <= pageCount; i++) {
            const page = await pdf.getPage(i);
            const content = await page.getTextContent();
            const items = [];

            for (const item of content.items) {
                if (!item.str || !item.str.trim()) continue;
                const fontSize = Math.abs(item.transform[0]);
                fontSizes.push(fontSize);
                items.push({ str: item.str, fontSize, page: i });
            }
            pages.push(items);
        }

        if (fontSizes.length === 0) {
            return { text: '', headingTree: [], pageCount };
        }

        // Find body text size (most frequent font size)
        const sizeHistogram = {};
        for (const size of fontSizes) {
            const rounded = Math.round(size * 10) / 10;
            sizeHistogram[rounded] = (sizeHistogram[rounded] || 0) + 1;
        }
        const bodySize = parseFloat(
            Object.entries(sizeHistogram)
                .sort((a, b) => b[1] - a[1])[0][0]
        );

        // Pass 2: build text and heading tree
        const textParts = [];
        const headingTree = [];

        for (const items of pages) {
            const lineBuffer = [];

            for (const item of items) {
                const ratio = item.fontSize / bodySize;

                // Detect headings by font size ratio
                if (ratio > 1.2 && item.str.trim().length > 1) {
                    // Flush line buffer
                    if (lineBuffer.length > 0) {
                        textParts.push(lineBuffer.join(' '));
                        lineBuffer.length = 0;
                    }

                    let level;
                    if (ratio > 2.0) level = 1;
                    else if (ratio > 1.5) level = 2;
                    else level = 3;

                    headingTree.push({
                        level,
                        title: item.str.trim(),
                        page: item.page
                    });
                    textParts.push(item.str.trim());
                } else {
                    lineBuffer.push(item.str);
                }
            }

            if (lineBuffer.length > 0) {
                textParts.push(lineBuffer.join(' '));
            }
            textParts.push(''); // page break
        }

        return {
            text: textParts.join('\n').trim(),
            headingTree,
            pageCount
        };
    },

    // Extract text and heading tree from a DOCX blob
    async extractDocxText(blob) {
        const arrayBuffer = await blob.arrayBuffer();
        const result = await mammoth.convertToHtml({ arrayBuffer });
        const html = result.value;

        // Parse HTML to extract headings and text
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        const headingTree = [];
        const headingTags = doc.querySelectorAll('h1, h2, h3, h4, h5, h6');
        for (const h of headingTags) {
            const level = parseInt(h.tagName[1]);
            const title = h.textContent.trim();
            if (title) {
                headingTree.push({ level, title });
            }
        }

        const text = doc.body.textContent.trim();

        return { text, headingTree };
    }
};
