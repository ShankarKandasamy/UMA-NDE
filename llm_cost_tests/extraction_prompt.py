"""Shared extraction prompt and system message for all model tests."""

SYSTEM_MSG = "You are a document analysis specialist. Always respond with valid JSON only. No markdown, no code fences, no commentary."

EXTRACTION_PROMPT = r"""Analyze this PDF document and return ONLY a valid JSON object with the following structure. No markdown, no code fences — just raw JSON.

{
  "title": "<document title or descriptive title if none explicit>",
  "pages": <integer number of pages>,
  "summary": "<550-1100 character summary designed for retrieval. A downstream LLM will read this summary to decide whether this document is likely to contain the answer to a given query. Cover: what type of document this is, the key entities/subjects, the types of data and specifications it contains, and what questions it could answer. Also serve as an executive summary.>",
  "sections": [
    {
      "heading": "<section heading or inferred heading>",
      "text": "<full text content of this section, preserving important details>"
    }
  ],
  "tables": [
    {
      "title": "<table title or inferred title from context>",
      "headers": ["col1", "col2", "..."],
      "rows": [["val1", "val2", "..."], ["..."]]
    }
  ],
  "images": [
    {
      "page": <page number>,
      "ocr_text": "<any text extracted/visible in the image>",
      "description": "<what the image shows and how it relates to the surrounding text>"
    }
  ],
  "charts": [
    {
      "page": <page number>,
      "type": "<bar chart | line chart | pie chart | diagram | flowchart | other>",
      "title": "<chart title or inferred title>",
      "data": {"x": ["..."], "y": ["..."]},
      "insights": "<trends, conclusions, key takeaways from the chart>"
    }
  ]
}

Rules:
- Split text into sections at logical boundaries (numbered headings, bold headings, topic shifts).
- For tables: extract ALL rows and columns as structured data. Do not summarize table contents.
- For images: describe what is visible and provide OCR'd text. If the image is purely decorative (logo, border), still include it but note it as decorative.
- For charts/diagrams: extract data points where possible. If exact values aren't readable, provide approximate values and note they are approximate.
- If no images, charts, or tables exist, return empty arrays for those fields.
- The summary MUST be 550-1100 characters (not words).
"""
