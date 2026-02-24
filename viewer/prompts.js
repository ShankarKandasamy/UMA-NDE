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
  "category": "<MUST be exactly one of: Inspection Data | Historical Data | Inspection Photos | Calibration Records | Personnel Records | Technical Drawings | Project Documents | Safety Documents | Field Reports | Site Photos | Reference Materials>"
}

Rules:
- category: MUST be one of these exact values (no variations):
  - "Inspection Data" — measurement readings, UT gauge exports, thickness data, field data CSVs
  - "Historical Data" — previous survey data, baseline measurements, trend comparisons
  - "Inspection Photos" — CML location photos, gauge display photos, surface condition photos, anomaly documentation
  - "Calibration Records" — equipment calibration certificates, daily calibration check photos, reference standards
  - "Personnel Records" — inspector certifications, NDE qualifications, training documentation
  - "Technical Drawings" — piping isometrics, P&IDs, engineering diagrams, schematics
  - "Project Documents" — RFQs, work orders, scope documents, contracts, proposals
  - "Safety Documents" — job safety analyses, safety plans, work permits, hazard assessments
  - "Field Reports" — inspector field notes, daily logs, narrative reports, completion summaries
  - "Site Photos" — general site overview, equipment context, unit area photos
  - "Reference Materials" — standards, procedures, technical guides, code requirements, textbooks
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
  "category": "<MUST be exactly one of: Inspection Data | Historical Data | Inspection Photos | Calibration Records | Personnel Records | Technical Drawings | Project Documents | Safety Documents | Field Reports | Site Photos | Reference Materials>"
}

Rules:
- category: MUST be one of these exact values (no variations):
  - "Inspection Data" — measurement readings, UT gauge exports, thickness data, field data CSVs
  - "Historical Data" — previous survey data, baseline measurements, trend comparisons
  - "Inspection Photos" — CML location photos, gauge display photos, surface condition photos, anomaly documentation
  - "Calibration Records" — equipment calibration certificates, daily calibration check photos, reference standards
  - "Personnel Records" — inspector certifications, NDE qualifications, training documentation
  - "Technical Drawings" — piping isometrics, P&IDs, engineering diagrams, schematics
  - "Project Documents" — RFQs, work orders, scope documents, contracts, proposals
  - "Safety Documents" — job safety analyses, safety plans, work permits, hazard assessments
  - "Field Reports" — inspector field notes, daily logs, narrative reports, completion summaries
  - "Site Photos" — general site overview, equipment context, unit area photos
  - "Reference Materials" — standards, procedures, technical guides, code requirements, textbooks
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

// ============================================
// Folder Summary Prompts
// ============================================

const FOLDER_SUMMARY_SYSTEM_MSG =
  "You are a document collection analyst. Always respond with valid JSON only. No markdown, no code fences, no commentary.";

const FOLDER_SUMMARY_PROMPT = `You are given a folder name and the individual summaries + keywords of every file in that folder. Synthesize them into a single folder-level summary optimized for relevance filtering.

A downstream LLM will read ONLY this folder summary to decide whether to search inside the folder for a given query. The summary must capture the breadth and depth of the folder's contents so the downstream system can make accurate relevance decisions without scanning individual files.

Return ONLY a valid JSON object:

{
  "summary": "<300-800 character folder summary. Cover: what types of documents/images are in this folder, the key subjects and entities across all files, the types of data and measurements available, and what categories of questions this folder's contents could answer. Be specific — include equipment tags, measurement types, date ranges, and document types where available.>",
  "keywords": ["<5-15 aggregated keywords that represent the most important and distinctive topics across all files in this folder. Deduplicate and consolidate similar terms. Prioritize terms that distinguish this folder from other folders.>"]
}

Rules:
- summary MUST be 300-800 characters (not words)
- keywords MUST have 5-15 entries
- Deduplicate and consolidate keywords from individual files — prefer broader terms when many files share similar specific terms
- Focus on what makes this folder's contents unique and queryable`;
