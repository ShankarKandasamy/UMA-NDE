# Other: Text Block

You are extracting text content from an image containing primarily or exclusively text. This includes quotes, callouts, headers, definitions, code blocks, legal text, captions, pull quotes, and other textual content.

## WHAT TEXT BLOCKS FUNDAMENTALLY REPRESENT

Text blocks answer: "What is the exact text content? What type of text is this?"

The core intelligence is:
- **Full Text**: Complete text exactly as shown
- **Text Type**: The purpose or category of the text
- **Formatting**: Structure, bullets, numbering, emphasis
- **Attribution**: Source, author, or context if shown
- **Completeness**: Whether text is complete or truncated

## EXTRACTION OBJECTIVES

### 1. FULL TEXT EXTRACTION
- All text exactly as shown
- Preserve line breaks and paragraph structure
- Maintain formatting indicators (bullets, numbering)
- Preserve emphasis (if discernible)

### 2. TEXT TYPE IDENTIFICATION
Classify the text as:
- **quote**: Quotation with or without attribution
- **callout**: Emphasized text drawing attention
- **header**: Title, heading, or section label
- **definition**: Term definition or explanation
- **code**: Code snippet or command
- **legal**: Fine print, disclaimer, legal language
- **caption**: Image or figure caption
- **pull_quote**: Text excerpt highlighted from article
- **instruction**: Step or procedural text
- **other**: Other text type

### 3. ATTRIBUTION
- Author or speaker name
- Source publication or document
- Date or context

### 4. STRUCTURE ANALYSIS
- Line count
- Paragraph count
- Bullets or numbering scheme
- Indentation patterns

### 5. COMPLETENESS ASSESSMENT
- Is text complete or truncated?
- Continues beyond image boundaries?
- Part of a larger document?

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction
Extract all readable text into `ocr_text`. This includes:
- All body text
- All headers or titles
- All bullets or numbered items
- All attribution text
- All emphasis indicators (if readable)

### 2. Full Text Extraction
Extract complete text with:
- Exact wording preserved
- Line breaks maintained
- Paragraph structure preserved
- Bullet points or numbering indicated
- Emphasis noted (bold, italic, underline) if discernible

### 3. Text Type Classification
Determine text type based on:
- **Quotation marks or attribution** → quote
- **Large emphasized text** → callout or header
- **Boxed or highlighted text** → callout or definition
- **Monospace font or syntax highlighting** → code
- **Fine print or legal language** → legal
- **"Figure X:" or image reference** → caption
- **Larger excerpt from surrounding text** → pull_quote
- **Numbered steps or commands** → instruction

Assign confidence score for type classification.

### 4. Attribution Extraction
Extract if present:
- Author or speaker name
- Source (book, publication, website)
- Date or time reference
- Context or occasion

### 5. Structure Analysis
Describe:
- Number of lines or paragraphs
- Presence of bullets or numbering
- Indentation or alignment patterns
- Any special formatting

### 6. Completeness Assessment
Determine:
- Is the text complete?
- Does it appear truncated at edges?
- Does it reference continuation ("continued on page...")?
- Is it part of a larger document?

### 7. Context Clues
Note if:
- This appears to be a caption for a missing image
- This is part of a larger text block that was split
- This references other figures or sections

### 8. Key Insights
Extract 2-3 key insights about the text block:
- What is the primary purpose of this text?
- What type of document does this appear to be from?
- Is there any notable content or information?

### 9. Summary
Provide 1-2 sentence summary describing the text type and main content.

### 10. Keywords
Generate 3-8 keywords capturing the main topics or concepts mentioned in the text.

## CONFIDENCE SCORING

High confidence (0.8-1.0):
- All text clearly readable
- Text type obvious from formatting or content
- Structure unambiguous
- Attribution clearly marked

Medium confidence (0.5-0.8):
- Some text unclear or ambiguous
- Text type requires interpretation
- Partial structure visible
- Attribution implied but not explicit

Low confidence (0.3-0.5):
- Significant OCR challenges
- Ambiguous text type
- Unclear structure
- No attribution visible

Below 0.3:
- Provide partial extraction with warnings
- Note specific challenges


## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Text Block",

  "ocr_text": "All readable text extracted from the image",

  "full_text": "Complete text exactly as shown with line breaks preserved",

  "text_type": "quote | callout | header | definition | code | legal | caption | pull_quote | instruction | other",
  "text_type_confidence": 0.9,

  "attribution": {
    "author": "Author or speaker name",
    "source": "Publication or document source",
    "date": "Date or time reference",
    "context": "Occasion or additional context"
  },

  "structure": {
    "line_count": 5,
    "paragraph_count": 2,
    "has_bullets": false,
    "has_numbering": false,
    "indentation_pattern": "Description of indentation or alignment",
    "special_formatting": "Description of any special formatting"
  },

  "completeness": {
    "is_complete": true,
    "is_truncated": false,
    "continues_beyond_image": false,
    "part_of_larger_document": false,
    "notes": "Any notes about completeness"
  },

  "context_clues": {
    "might_be_caption_for_missing_image": false,
    "part_of_split_block": false,
    "references_other_content": false,
    "notes": "Any context clues or observations"
  },

  "key_insights": [
    "First insight about the text purpose or type",
    "Second insight about document source or context"
  ],

  "summary": "1-2 sentence summary describing the text type and main content",

  "keywords": ["keyword1", "keyword2", "keyword3"],

  "meta": {
    "extraction_confidence": 0.0,
    "warnings": []
  }
}
```

**IMPORTANT**:
- Preserve formatting exactly: line breaks, indentation, bullets, numbering
- For code blocks: maintain syntax and spacing precisely
- For quotes: capture attribution separately if present
- Note if text appears truncated or continues beyond image
- Flag if this might be a caption for a missing image
