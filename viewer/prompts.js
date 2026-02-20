// ============================================
// LLM Extraction Prompts
// ============================================

const EXTRACTION_SYSTEM_MSG =
  "You are a document analysis specialist. Always respond with valid JSON only. No markdown, no code fences, no commentary.";

const PDF_EXTRACTION_PROMPT = `Analyze this PDF document and return ONLY a valid JSON object with the following structure. No markdown, no code fences — just raw JSON.

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
  "keywords": "[<list of keywords that capture the main concepts, topics, and data points of the image and its context. These keywords will be used to help the user search for this image in the future.>]
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
  ],
  "category": "<a short, descriptive folder name for this document, e.g. Inspection Data, Client Procedures, Engineering Drawings, Reports, Calibration Records, Equipment Nameplates, etc.>"
}

Rules:
- category: Choose a concise, professional folder name (2-3 words) that describes the type/purpose of this document. Use title case.
- Split text into sections at logical boundaries (numbered headings, bold headings, topic shifts).
- For tables: extract ALL rows and columns as structured data. Do not summarize table contents.
- For images: describe what is visible and provide OCR'd text. If the image is purely decorative (logo, border), still include it but note it as decorative.
- For charts/diagrams: extract data points where possible. If exact values aren't readable, provide approximate values and note they are approximate.
- If no images, charts, or tables exist, return empty arrays for those fields.
- The summary MUST be 550-1100 characters (not words).`;

const IMAGE_EXTRACTION_PROMPT = `Analyze this image and return ONLY a valid JSON object with the following structure. No markdown, no code fences — just raw JSON.

{
  "image_type": "<classify as one of: document | technical_diagram | inspection_photo | instrument_screen | calibration_setup | nameplate | other>",
  "title": "<descriptive title for this image>",
  "summary": "<550-1100 character summary designed for retrieval. A downstream LLM will read this summary to decide whether this image is relevant to a given query. Cover: what type of image this is, what it shows, the key entities/subjects, any measurable data or readings present, and what questions this image could help answer.>",
  "ocr_text": "<all readable text visible in the image, verbatim, separated by newlines. Include labels, tags, numbers, units, dates, titles, and annotations.>",
  "image_quality": "<clear | partially_obscured | blurry | low_light | other>",
  "readings": [
    {
      "parameter": "<measured quantity, e.g. thickness, temperature, pressure>",
      "value": "<numeric or string value as shown>",
      "unit": "<unit of measure, e.g. mm, °C, PSI>"
    }
  ],
  "observations": [
    "<notable visible detail, condition, feature, or contextual information. If any instrument readings are visible, include them in the observations array.>"
  ],
  "keywords": "[<list of keywords that capture the main concepts, topics, and data points of the image and its context. These keywords will be used to help the user search for this image in the future.>]
  "anomalies": [
    "<any visible defect, damage, corrosion, crack, irregularity, or concern>"
  ],
  "components": [
    {
      "tag": "<equipment tag or label if visible, e.g. V-101>",
      "type": "<vessel | pipe | valve | instrument | fitting | structural | other>",
      "description": "<what this component is and its notable characteristics>"
    }
  ],
  "tables": [
    {
      "title": "<table title or inferred title>",
      "headers": ["col1", "col2"],
      "rows": [["val1", "val2"]]
    }
  ],
  "category": "<a short, descriptive folder name for this image, e.g. Inspection Data, Client Procedures, Engineering Drawings, Reports, Calibration Records, Equipment Nameplates, etc.>"
}

Rules:
- category: Choose a concise, professional folder name (2-3 words) that describes the type/purpose of this image. Use title case.
- ALWAYS populate image_type, title, summary, ocr_text, and image_quality — these are required for every image.
- ocr_text: extract ALL readable text verbatim, even partial or worn text. If no text is visible, use an empty string.
- summary MUST be 550-1100 characters (not words).
- Type-specific rules:
  - instrument_screen: populate readings with every visible parameter/value/unit pair. Only include values that are clearly readable — do not guess.
  - inspection_photo: populate observations describing the subject, location, orientation, and environment. Populate anomalies with any defects, corrosion, damage, or concerns. Leave anomalies as an empty array if the condition appears normal.
  - technical_diagram: populate components with every labeled equipment item visible. Include drawing title, revision, and drawing number in title if visible.
  - document: populate tables if any tabular data is visible. Capture key text content in observations.
  - nameplate: put all nameplate data (model, serial, rating, spec values) verbatim in ocr_text and as individual observation entries.
  - calibration_setup: describe equipment visible and any procedure indicators or reference standards in observations.
- If a field is not applicable to the image type, return an empty array for array fields.`;
