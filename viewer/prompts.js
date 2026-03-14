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
      "type": "<line_chart | bar_chart | scatter_plot | a_scan | heatmap | contour_map | pie_chart | histogram | box_plot | diagram | flowchart | other>",
      "title": "<chart title or inferred title>",
      "axes": {"x_label": "<x-axis label with unit>", "y_label": "<y-axis label with unit>"},
      "data_points": [{"x": "<x value>", "y": "<y value>", "label": "<optional annotation>"}],
      "reference_lines": [{"label": "<e.g. Nominal, t_min>", "value": "<numeric>", "axis": "y"}],
      "statistics": {"min": "<if shown>", "max": "<if shown>", "avg": "<if shown>", "count": "<if shown>"},
      "regions": [{"description": "<for heatmaps/contour maps — zone description>", "bounds": "<location>", "severity": "<if applicable>"}],
      "insights": "<trends, conclusions, key takeaways from the chart>"
    }
  ],
  "category": "<MUST be exactly one of: Inspection Data | Historical Data | Inspection Photos | Calibration Records | Personnel Records | Technical Drawings | Project Documents | Safety Documents | Field Reports | Site Photos | Reference Materials | Governing Documents>",
  "notes": "<verbatim user-provided note, or empty string if none>"
}

Rules:
- notes: Return the user-provided note exactly as given. If no note was provided, return an empty string.
- USER NOTE (if provided) is a highly influential input. It was written by the person who uploaded this file and may carry context not visible in the document itself — such as the correct category, job number, equipment tag, material spec, inspection type, or client name. When a note is present:
  - Prioritize it when selecting category — the note often signals the correct folder directly.
  - Use any job numbers, equipment tags, or client names from the note in the title, summary, and keywords.
  - Let the note resolve ambiguity in readings, section headings, or document purpose.
  - If the note contradicts something visible in the document, flag both but weight the note heavily.
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
  - "Governing Documents" — client specifications, engineering standards, or project-specific documents that define acceptance criteria, pass/fail thresholds, or inspection requirements that override or supplement industry codes. Recognize by: imperative language ("shall", "must", "shall not exceed"), override clauses ("notwithstanding [code]", "in lieu of", "takes precedence over"), numbered specification clauses, referenced codes with modifications, and acceptance criteria tables with custom thresholds. If a document establishes the controlling requirements for a job — even if it also resembles a reference material — categorize it here.
- Split text into sections at logical boundaries (numbered headings, bold headings, topic shifts).
- For tables: extract ALL rows and columns as structured data. Do not summarize table contents.
- For images: describe what is visible and provide OCR'd text. If the image is purely decorative (logo, border), still include it but note it as decorative.
- For charts/diagrams: extract EVERY individual data point as {x, y} pairs in data_points. For line charts, record every plotted point. For bar charts, record every bar's value. For heatmaps, describe regions instead of individual points. Extract reference lines (nominal, t_min, thresholds) and any summary statistics shown. If exact values aren't readable, provide approximate values and add "label": "~approx" to the data point.
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
  "chart_data": {
    "chart_type": "<line_chart | bar_chart | scatter_plot | a_scan | heatmap | contour_map | pie_chart | histogram | box_plot | other | none>",
    "chart_title": "<chart title as shown, or empty string if not a chart>",
    "axes": {
      "x_label": "<x-axis label with unit>",
      "y_label": "<y-axis label with unit>",
      "x_range": [<min>, <max>],
      "y_range": [<min>, <max>]
    },
    "data_points": [
      {"x": "<x value>", "y": <y value>, "label": "<optional data label or annotation>"}
    ],
    "reference_lines": [
      {"label": "<e.g. Nominal Wall, t_min>", "value": <numeric value>, "axis": "x or y"}
    ],
    "regions": [
      {"description": "<region description, e.g. severe corrosion zone>", "bounds": "<approximate location/extent>", "severity": "<if applicable>"}
    ],
    "statistics": {
      "min": "<min value with label if shown>",
      "max": "<max value with label if shown>",
      "avg": "<average if shown>",
      "count": "<number of data points or readings>"
    }
  },
  "tables": [
    {
      "title": "<table title or inferred title>",
      "headers": ["col1", "col2"],
      "rows": [["val1", "val2"]]
    }
  ],
  "category": "<MUST be exactly one of: Inspection Data | Historical Data | Inspection Photos | Calibration Records | Personnel Records | Technical Drawings | Project Documents | Safety Documents | Field Reports | Site Photos | Reference Materials | Governing Documents>",
  "notes": "<verbatim user-provided note, or empty string if none>"
}

Rules:
- notes: Return the user-provided note exactly as given. If no note was provided, return an empty string.
- USER NOTE (if provided) is a highly influential input. It was written by the person who uploaded this file and may carry context not visible in the image itself — such as the correct category, job number, equipment tag, material spec, inspection type, or client name. When a note is present:
  - Prioritize it when selecting category — the note often signals the correct folder directly.
  - Use any job numbers, equipment tags, or client names from the note in the title, summary, and keywords.
  - Let the note resolve ambiguity in readings, observations, or image purpose.
  - Notes may contain instructions and if so; they shall override all other instructions and guidelines.
  - If the note contradicts something visible in the image, flag both but weight the note heavily.
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
  - "Governing Documents" — client specifications, engineering standards, or project-specific documents that define acceptance criteria, pass/fail thresholds, or inspection requirements that override or supplement industry codes. Recognize by: imperative language ("shall", "must", "shall not exceed"), override clauses ("notwithstanding [code]", "in lieu of", "takes precedence over"), numbered specification clauses, referenced codes with modifications, and acceptance criteria tables with custom thresholds. If a document establishes the controlling requirements for a job — even if it also resembles a reference material — categorize it here.
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
- If a field is not applicable to the image type, return an empty array for array fields or null for object fields.

Chart/Graph Data Extraction — CRITICAL for any image containing a chart, graph, plot, or data visualization:
- chart_data.chart_type: MUST be set for ANY image containing a chart or graph. Set to "none" only for non-chart images (photos, documents, diagrams).
- data_points: Extract EVERY individually identifiable data point as an {x, y} pair. This is the most important field.
  - LINE CHARTS: Read each plotted point where the line changes direction or where a marker dot is visible. Walk left-to-right along the x-axis and record every point. Example: [{"x": "12:00", "y": 8.45}, {"x": "1:00", "y": 8.38}, ...]
  - BAR CHARTS: Record the x-position label and height (y-value) of every bar. If bars are grouped, include a "label" field to identify the series. Example: [{"x": "0", "y": 0.353}, {"x": "0.5", "y": 0.354}, ...]
  - A-SCANS / WAVEFORMS: Record each significant peak — the x-position (time) and y-value (amplitude). Label peaks with their identity if annotated (IP, BE, etc.). Example: [{"x": 10, "y": 98, "label": "IP"}, {"x": 20, "y": 48, "label": "BE"}, {"x": 31, "y": 45, "label": "BE"}]
  - SCATTER PLOTS: Record every visible point as {x, y}.
  - PIE CHARTS: Record each slice as {"x": "<category>", "y": <percentage or value>, "label": "<category label>"}.
  - HISTOGRAMS: Record each bin as {"x": "<bin range or center>", "y": <count or frequency>}.
- HEATMAPS / CONTOUR MAPS: data_points may be sparse or unavailable. Instead, populate the "regions" array:
  - Identify distinct zones by their color/intensity and describe their approximate location, extent, and the value range they represent.
  - Example: [{"description": "Severe thinning zone", "bounds": "center-left quadrant, x: 200-600, y: 400-800", "severity": "critical — values 10-12 (near minimum)"}]
  - If a color scale legend is present, reference its values in the region descriptions.
- reference_lines: Extract any horizontal or vertical reference lines (nominal wall thickness, t_min, alarm thresholds, code limits). These are critical for engineering context.
- statistics: Extract any summary statistics shown on the chart (min, max, avg, count, THK values). If shown as annotations, capture them exactly.
- axes: ALWAYS populate axis labels and ranges for any chart. Read the axis tick marks to determine the range.
- When exact values are not readable from the chart, estimate from the grid/axis and note in the data point's "label" field that the value is approximate (e.g., "label": "~approx").
- Prefer over-extraction to under-extraction. It is better to include an approximate data point than to skip it.`;

const SPREADSHEET_EXTRACTION_PROMPT = `Analyze this spreadsheet data and return ONLY a valid JSON object with the following structure. No markdown, no code fences — just raw JSON.

The spreadsheet has been pre-parsed and is provided as tab-delimited text below. The metadata header shows filename, sheet count, total rows, total columns, and file size. Each sheet is delimited by "=== Sheet: <name> ===" markers with headers on the first row.

{
  "spreadsheet_type": "<csv or excel — already provided in metadata>",
  "title": "<descriptive title for this spreadsheet based on its content>",
  "summary": "<550-1100 character summary designed for retrieval. A downstream LLM will read this summary to decide whether this spreadsheet is relevant to a given query. Cover: what type of data this contains, the key entities/subjects, column descriptions, row count and scope, measurement types and units present, date ranges if applicable, and what questions this data could answer.>",
  "sections": [
    {
      "heading": "<one of: Data Summary | Column Analysis | Data Quality | Key Findings>",
      "text": "<analytical paragraph about this aspect of the data>"
    }
  ],
  "observations": [
    "<notable pattern, trend, outlier, or characteristic of the data>"
  ],
  "keywords": ["<list of keywords that capture the main concepts, data types, entities, and topics in this spreadsheet>"],
  "category": "<MUST be exactly one of: Inspection Data | Historical Data | Inspection Photos | Calibration Records | Personnel Records | Technical Drawings | Project Documents | Safety Documents | Field Reports | Site Photos | Reference Materials | Governing Documents>",
  "notes": "<verbatim user-provided note, or empty string if none>"
}

Rules:
- notes: Return the user-provided note exactly as given. If no note was provided, return an empty string.
- USER NOTE (if provided) is a highly influential input. It was written by the person who uploaded this file and may carry context not visible in the data itself — such as the correct category, job number, equipment tag, material spec, inspection type, or client name. When a note is present:
  - Prioritize it when selecting category — the note often signals the correct folder directly.
  - Use any job numbers, equipment tags, or client names from the note in the title, summary, and keywords.
  - Let the note resolve ambiguity in column meanings, data purpose, or document context.
  - Notes may contain instructions and if so; they shall override all other instructions and guidelines.
  - If the note contradicts something visible in the data, flag both but weight the note heavily.
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
  - "Governing Documents" — client specifications, engineering standards, or project-specific documents that define acceptance criteria, pass/fail thresholds, or inspection requirements that override or supplement industry codes. Recognize by: imperative language ("shall", "must", "shall not exceed"), override clauses ("notwithstanding [code]", "in lieu of", "takes precedence over"), numbered specification clauses, referenced codes with modifications, and acceptance criteria tables with custom thresholds. If a document establishes the controlling requirements for a job — even if it also resembles a reference material — categorize it here.
- Generate 2-4 analytical sections from: Data Summary, Column Analysis, Data Quality, Key Findings
  - Data Summary: overview of what the data represents, row/column count, key columns
  - Column Analysis: describe each column's data type, range, and meaning
  - Data Quality: note missing values, inconsistencies, duplicates, or formatting issues
  - Key Findings: notable patterns, outliers, trends, or aggregations
- Do NOT include sheets, file_metadata, or tables in your response — those are populated from the pre-parsed data.
- summary MUST be 550-1100 characters (not words).
- keywords should include column names, data types, entity names, and domain-specific terms.`;

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

// ============================================
// Search Pipeline Prompts
// ============================================

const SEARCH_SCORING_SYSTEM_MSG =
  "You are a relevance scoring specialist. Always respond with valid JSON only. No markdown, no code fences, no commentary.";

const FOLDER_SCORING_PROMPT = `You are given a user query and a list of folder summaries with keywords. Score each folder's relevance to the query on a scale from 0.0 to 1.0.

Return ONLY a valid JSON object:

{
  "results": [
    { "folderId": "<exact folder name>", "score": <0.0 to 1.0> }
  ]
}

Scoring guidelines:
- 0.9-1.0: Folder almost certainly contains documents directly answering the query
- 0.7-0.89: Folder likely contains relevant documents
- 0.5-0.69: Folder might contain tangentially relevant information
- 0.0-0.49: Folder is unlikely to contain relevant information
- Consider both the summary text and keywords when scoring
- A folder can score high even if only some of its files might be relevant
- Be generous — it's better to include a marginally relevant folder than miss a relevant one`;

const FILE_SCORING_PROMPT = `You are given a user query and a list of file summaries with keywords. Score each file's relevance to the query on a scale from 0.0 to 1.0.

Return ONLY a valid JSON object:

{
  "results": [
    { "fileId": "<exact file ID as provided>", "score": <0.0 to 1.0> }
  ]
}

Scoring guidelines:
- 0.9-1.0: File almost certainly contains information directly answering the query
- 0.7-0.89: File likely contains relevant information
- 0.5-0.69: File might contain tangentially relevant information
- 0.0-0.49: File is unlikely to contain relevant information
- Consider both the summary text and keywords when scoring
- Be generous — it's better to include a marginally relevant file than miss one`;

const SECTION_RETRIEVAL_PROMPT = `You are given a user query and the full extracted content from one or more files. Each file may contain sections, tables, charts, images, and readings. Identify which specific content items are relevant to the query.

Return ONLY a valid JSON object:

{
  "results": [
    {
      "fileId": "<exact file ID as provided>",
      "relevant": [
        { "type": "section", "index": <0-based index>, "reason": "<1-2 sentence explanation of why this is relevant>" },
        { "type": "table", "index": <0-based index>, "reason": "<explanation>" },
        { "type": "chart", "index": <0-based index>, "reason": "<explanation>" },
        { "type": "image", "index": <0-based index>, "reason": "<explanation>" },
        { "type": "reading", "index": <0-based index>, "reason": "<explanation>" }
      ]
    }
  ]
}

Rules:
- Only include content items that are genuinely relevant to the query
- The "type" must be one of: section, table, chart, image, reading
- The "index" must match the 0-based position in the file's content arrays
- The "reason" should explain WHY this content answers or relates to the query, not just describe what it contains
- If a file has no relevant content items, omit it from results entirely
- Prefer specific, targeted selections over returning everything
- Tables with relevant data are often highly valuable — don't overlook them`;

const ANSWER_SYNTHESIS_SYSTEM_MSG =
  "You are an expert NDE (Non-Destructive Examination) technical analyst. You answer questions by synthesizing information from inspection documents, data, and images. Be precise, cite specific values, and flag any gaps or uncertainties.";

const ANSWER_SYNTHESIS_PROMPT = `You are given a user's query and a set of relevant content retrieved from their document corpus. Synthesize a clear, direct answer to the query based on the provided evidence.

Rules:
- Answer the query directly and concisely — lead with the answer, not background
- Cite specific values, measurements, dates, and document names from the evidence
- If the evidence partially answers the query, answer what you can and note what's missing
- If the evidence does not answer the query at all, say so clearly
- Use professional NDE/inspection terminology where appropriate
- For numerical data, include units and context (e.g. "minimum thickness of 0.285 in. at CML 12")
- If multiple sources provide conflicting information, note the discrepancy
- Keep the answer focused — typically 2-6 sentences, longer only if the query demands detail
- Do NOT fabricate information not present in the provided evidence
- Format the answer as plain text (no markdown, no bullet points unless listing multiple items)`;

// ============================================
// Report Generation Prompts
// ============================================

const TEMPLATE_ANALYSIS_SYSTEM_MSG =
  "You are an inspection report template analyst. Always respond with valid JSON only. No markdown, no code fences, no commentary.";

const TEMPLATE_ANALYSIS_PROMPT = `Analyze this PDF report template/example and identify every section and sub-section. Return ONLY a valid JSON object:

{
  "reportType": "<type of report, e.g. UT Thickness Survey, MT/PT Inspection, Visual Inspection>",
  "title": "<report title as shown or inferred>",
  "sections": [
    {
      "index": 0,
      "title": "<section title as it appears>",
      "summary": "<100-300 character description of what content is NEEDED for this section — not what the template says, but what data/narrative must be provided>",
      "fields": ["<list of specific data fields this section requires, e.g. report_number, client, facility, inspection_dates>"],
      "hasTables": false,
      "tableSchemas": [
        {
          "title": "<table title>",
          "columns": ["<column headers>"],
          "rowDescription": "<what each row represents>"
        }
      ]
    }
  ]
}

Rules:
- Extract EVERY section including appendices, attachments, and signature blocks
- Order sections exactly as they appear in the document
- Summaries must describe what content/data is needed, not what text is printed
- For tables: capture column headers and describe what each row represents
- If a section has no tables, set hasTables to false and tableSchemas to []
- fields should list specific data items needed (not generic descriptions)
- Be thorough — missing a section means missing content in the final report`;

const FOLDER_MAPPING_PROMPT = `You are given a list of report template sections and a list of data folders with summaries. Map each section to the folders most likely to contain relevant data for generating that section's content.

Return ONLY a valid JSON object:

{
  "mappings": [
    {
      "sectionIndex": 0,
      "sectionTitle": "<section title>",
      "folders": [
        { "folderId": "<exact folder name>", "score": 0.8, "reason": "<why this folder is relevant>" }
      ]
    }
  ]
}

Rules:
- Include ALL sections in the mappings array
- Only include folders with relevance score >= 0.3
- Be generous — it is better to include a marginally relevant folder than miss critical data
- Some sections (e.g. Cover Page, Table of Contents) may map to many folders for metadata
- Data-heavy sections (Results, Trending) should map to inspection data and historical folders
- Score 0.9-1.0: folder almost certainly has data needed for this section
- Score 0.7-0.89: folder likely has relevant data
- Score 0.5-0.69: folder might have tangentially relevant data
- Score 0.3-0.49: folder has marginal relevance but worth checking`;

const SECTION_GENERATION_SYSTEM_MSG =
  "You are an expert NDE (Non-Destructive Examination) report writer with deep knowledge of UT thickness surveys, corrosion assessment, and inspection standards. Always respond with valid JSON only. No markdown, no code fences, no commentary.";

const SECTION_GENERATION_PROMPT = `Generate the content for one section of an NDE inspection report. You are given:
1. The section specification (what content is needed)
2. Relevant data chunks extracted from the corpus
3. The report manifest (data inferred so far, user answers, completed sections)

Return ONLY a valid JSON object:

{
  "sectionContent": {
    "title": "<section title>",
    "narratives": [
      "plain paragraph (when no specific source)",
      { "text": "paragraph referencing data [0][3]", "sources": [0, 3] }
    ],
    "tables": [
      {
        "title": "<table title>",
        "headers": ["col1", "col2"],
        "rows": [["val1", "val2"]],
        "rowSources": [[0, 1], [2]]
      }
    ],
    "bulletPoints": [
      "plain bullet",
      { "text": "bullet citing chunk [5]", "sources": [5] }
    ]
  },
  "manifestUpdates": {
    "inferredData": { "<key>": "<value inferred from data>" },
    "sectionSummary": "<50-150 char summary of what was generated>"
  },
  "questions": [
    {
      "id": "<unique_id>",
      "text": "<question to ask the user>",
      "field": "<manifest field name for the answer>",
      "type": "text",
      "choices": [],
      "required": false,
      "default": "<suggested default value if any>"
    }
  ],
  "dataGaps": ["<description of missing data that could improve this section>"],
  "confidence": 0.85
}

Source citation rules:
- Each narrative or bulletPoint MAY be a plain string OR an object { "text": "...", "sources": [N, ...] } where sources is an array of 0-based indices into the data chunks array
- For tables, include "rowSources" parallel to "rows" — each entry is an array of chunk indices that sourced that row
- Insert [N] bracket references in the text near the claims they support (N = chunk index from the data chunks array)
- Source annotations are best-effort — omit rather than guess. Only cite when you are confident which chunk supports a claim
- Plain strings are acceptable when no specific source chunk applies

Rules:
- ALL calculations must be performed by you (corrosion rates, remaining life, min/max, averages, categories)
- Corrosion rate = (previous_thickness - current_thickness) / years_between_surveys
- Remaining life = (current_thickness - t_min) / corrosion_rate
- Use the manifest for cross-section consistency (reuse client name, dates, CML counts from earlier sections)
- Generate questions ONLY for truly missing information that cannot be inferred from the data
- Include EVERY data row in tables — never summarize or truncate table data
- Use exact values from the source data — do not round or approximate unless standard practice
- narratives should be professional NDE report language
- If data chunks are empty/insufficient for this section, generate reasonable boilerplate and flag in dataGaps
- type can be "text" or "choice" — use "choice" when there are known valid options
- confidence: 0.0-1.0 indicating how well the data supports this section`;

const CROSS_CHECK_SYSTEM_MSG =
  "You are a quality assurance reviewer for NDE inspection reports. Always respond with valid JSON only. No markdown, no code fences, no commentary.";

const CROSS_CHECK_PROMPT = `Review the complete generated report for internal consistency and technical accuracy. Check:

1. CML counts: do totals match across Executive Summary, Results, and Trending sections?
2. Client/facility/dates: consistent across all sections?
3. Personnel: do initials/names in signature blocks trace to the Personnel section?
4. Equipment serials: do calibration references trace to Calibration Records section?
5. Category assignments: do thickness categories match t-min values and actual readings?
6. Corrosion rate calculations: rate = (previous - current) / years — verify sample calculations
7. Remaining life calculations: life = (current - t_min) / rate — verify samples
8. Recommendations: do they match the severity of findings?
9. Table data: are there any obvious data entry errors (e.g. current > nominal, negative thickness)?

Return ONLY a valid JSON object:

{
  "overallConsistency": 0.85,
  "issues": [
    {
      "severity": "critical|warning|info",
      "sections": [0, 3],
      "description": "<what is inconsistent>",
      "suggestion": "<how to fix it>"
    }
  ],
  "corrections": [
    {
      "sectionIndex": 3,
      "field": "<which field or table cell>",
      "currentValue": "<what it says now>",
      "correctedValue": "<what it should say>",
      "reason": "<why>"
    }
  ]
}

Rules:
- overallConsistency: 0.0-1.0 score for the entire report
- severity "critical": must fix before publishing (wrong calculations, contradictory data)
- severity "warning": should fix (inconsistent naming, missing cross-references)
- severity "info": minor improvements (formatting, optional additions)
- Check at least 5 sample corrosion rate calculations if data is available
- Verify every CML count mentioned in narrative matches table row counts`;
