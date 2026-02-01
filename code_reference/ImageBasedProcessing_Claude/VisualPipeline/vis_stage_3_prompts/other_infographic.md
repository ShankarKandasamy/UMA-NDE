# Other: Infographic

You are extracting structured intelligence from an INFOGRAPHIC — a designed visual communication combining data visualization, text, icons, and images to present information in an engaging, easy-to-digest format.

## WHAT INFOGRAPHICS FUNDAMENTALLY REPRESENT

Infographics answer: "What's the big picture? What are the key facts and statistics?"

The core intelligence is:
- **Key Statistics**: Numbers, percentages, metrics with context
- **Structured Sections**: Distinct topical areas with related content
- **Comparisons**: Side-by-side comparisons, rankings, before/after
- **Process/Flow**: Sequential steps or timeline if present
- **Visual Hierarchy**: What's emphasized as most important
- **Data Sources**: Attribution for statistics and claims

## EXTRACTION OBJECTIVES

### 1. TITLE AND SUBJECT
- Main title/headline
- Subject or topic being presented
- Target message or takeaway

### 2. KEY STATISTICS
For EACH statistic or metric:
- Numerical value
- Unit of measurement
- Context (what it represents)
- Label or description
- Emphasis level (headline stat vs. supporting detail)

### 3. SECTIONS
For EACH distinct section:
- Section title or heading
- Content type (list, comparison, process, data visualization)
- Key points or items
- Visual treatment (icons, colors, emphasis)

### 4. COMPARISONS
- Items being compared
- Comparison type (side-by-side, ranking, before/after, A vs. B)
- Values or descriptions for each item
- Conclusion or implication

### 5. PROCESS/FLOW
If sequential steps are shown:
- Step number or order
- Step description
- Visual indicators (arrows, numbering, timeline)

### 6. EMBEDDED ELEMENTS
- Embedded charts (bar, pie, line)
- Embedded diagrams or icons
- Embedded photographs or illustrations
- Tables or data grids

### 7. SOURCE ATTRIBUTION
- Data sources
- Publication information
- Author or organization
- Date or version

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction
Extract all readable text into `ocr_text`. This includes:
- Main title and subtitle
- All section headings
- All statistics and metrics
- All labels and descriptions
- All list items and bullet points
- Source attributions
- Any footnotes or disclaimers
- Legend text

### 2. Title and Subject Extraction
Identify:
- Main title/headline (often largest text)
- Subtitle or tagline
- Overall subject or topic
- Target audience if indicated

### 3. Statistics Extraction
For each statistic:
- Extract exact numerical value
- Extract unit (%, $, millions, etc.)
- Extract label/description
- Note context (what it measures)
- Identify if it's a headline stat or supporting detail
- Assign confidence score

### 4. Section Identification
For each section:
- Extract section title/heading
- Identify content structure (list, comparison, process, chart)
- Extract all content items
- Note visual emphasis (icons, colors, size)
- Describe relationship to other sections

### 5. Comparison Extraction
For comparisons:
- Identify items being compared
- Extract values or descriptions for each
- Note comparison type
- Extract any conclusion or implication

### 6. Process/Flow Extraction
If sequential content exists:
- Extract step numbers or sequence indicators
- Extract description for each step
- Note directional indicators (arrows, flow)
- Identify start and end points

### 7. Embedded Elements Recognition
Identify and extract:
- Type of embedded element (chart, diagram, photo)
- Extract data from embedded charts using chart extraction rules
- Describe embedded diagrams or illustrations
- Note purpose of embedded element

### 8. Source Attribution Extraction
Extract:
- All data sources cited
- Organization or author name
- Publication date
- Website or reference URL
- Copyright or disclaimer text

### 9. Miscategorization Check
Assess if this might be:
- A standalone chart (should be categorized as graph/chart)
- A standalone diagram (should be categorized as diagram)
- A photograph with captions (should be categorized as photograph)
- Note in warnings if miscategorization is suspected

### 10. Key Insights
Extract 3-5 key insights about the infographic:
- What is the primary message or conclusion?
- What are the most significant statistics?
- What patterns or trends are highlighted?
- What comparisons reveal important differences?

### 11. Summary
Provide 1-2 sentence summary of the infographic's main message and key data.

### 12. Keywords
Generate 3-8 keywords capturing the main concepts, topics, and data points.

## CONFIDENCE SCORING

High confidence (0.8-1.0):
- Clear infographic structure
- All text readable
- Statistics clearly labeled with context
- Sections well-defined

Medium confidence (0.5-0.8):
- Some structural ambiguity
- Partial text readability
- Context requires interpretation
- Section boundaries unclear

Low confidence (0.3-0.5):
- Complex mixed layout
- Poor text quality
- Unclear structure
- Ambiguous statistics

Below 0.3:
- Provide general description only
- Note extraction challenges


## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Infographic",

  "ocr_text": "All readable text extracted from the infographic",

  "title_and_subject": {
    "main_title": "Main title/headline",
    "subtitle": "Subtitle or tagline",
    "subject": "Overall topic or subject",
    "target_message": "Primary takeaway or conclusion"
  },

  "statistics": [
    {
      "value": "75%",
      "unit": "percent",
      "label": "Market share increase",
      "context": "Description of what this measures",
      "emphasis": "headline | supporting",
      "confidence": 0.9
    }
  ],

  "sections": [
    {
      "section_id": "section_1",
      "title": "Section heading",
      "content_type": "list | comparison | process | chart | text",
      "items": ["Item 1", "Item 2", "Item 3"],
      "visual_treatment": "Description of icons, colors, emphasis",
      "confidence": 0.9
    }
  ],

  "comparisons": [
    {
      "comparison_type": "side_by_side | ranking | before_after | a_vs_b",
      "items": [
        {
          "label": "Item A",
          "value": "Value or description"
        },
        {
          "label": "Item B",
          "value": "Value or description"
        }
      ],
      "conclusion": "Implication or takeaway from comparison"
    }
  ],

  "process_flow": {
    "has_process": true,
    "steps": [
      {
        "step_number": 1,
        "description": "Step description",
        "visual_indicator": "Arrow, numbering, or timeline marker"
      }
    ]
  },

  "embedded_elements": [
    {
      "element_type": "chart | diagram | photo | table | icon",
      "description": "Description of embedded element",
      "data_extracted": "Data or information from element",
      "purpose": "Why this element is included"
    }
  ],

  "source_attribution": {
    "data_sources": ["Source 1", "Source 2"],
    "organization": "Author or organization name",
    "publication_date": "Date if shown",
    "url": "Website or reference",
    "disclaimer": "Copyright or disclaimer text"
  },

  "miscategorization_check": {
    "might_be_miscategorized": false,
    "suggested_category": "graph_chart | diagram | photograph",
    "reason": "Explanation if miscategorized"
  },

  "key_insights": [
    "First insight about the infographic's main message",
    "Second insight about significant statistics",
    "Third insight about patterns or trends"
  ],

  "summary": "1-2 sentence summary of the infographic's main message and key data",

  "keywords": ["keyword1", "keyword2", "keyword3"],

  "meta": {
    "extraction_confidence": 0.0,
    "warnings": []
  }
}
```

**IMPORTANT**:
- Capture ALL statistics with their full context
- Preserve the structure and hierarchy
- Extract embedded visual elements separately
- Note any source attributions for data
- If it looks like a miscategorized chart/diagram, flag this in warnings
