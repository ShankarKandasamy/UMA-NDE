## What UMA AI Is

UMA AI is a solo-developed, AI-powered platform for the Non-Destructive Examination (NDE) industry. NDE inspectors examine infrastructure (pipelines, pressure vessels, nuclear components) using methods like Ultrasonic Testing (UT), Radiographic Testing (RT), Magnetic Particle Testing (MT), etc.

**The problem:** Inspection data is messy — handwritten notes, photos of gauge screens, PDFs, spreadsheets, scanned reports. Turning this into structured, searchable, actionable information is manual, error-prone, and slow.

**The product:** UMA AI ingests this messy inspection data, uses AI to extract and structure it, then makes it searchable via natural language queries and (planned) generates compliance-ready inspection reports.

## Target Market & Business Model

- **Direct customers:** NDE inspection vendors (companies that perform inspections)
- **End users of those vendors:** Asset owners — gas pipeline operators, nuclear facilities, petrochemical plants, maritime companies
- **Current status:** Pre-revenue MVP, actively recruiting design partners
- **Design partner pitch:** Provide real-world noisy NDE data + feedback → get design input on development + preferred pricing

## Architecture Overview

```
UMA CAPTURE (Mobile PWA)     →    CLOUDFLARE WORKER (API)    →    UMA VIEWER (Desktop PWA)
Field data collection              Serverless backend              Browse, Search, Reports
Camera, voice input, upload        R2 storage, LLM proxy           AI extraction & querying
```

**Tech:** Vanilla JS (no frameworks), Cloudflare Workers + R2, Anthropic Claude (extraction), OpenAI GPT-4 (search scoring), IndexedDB for offline caching. Fully serverless, offline-capable PWAs.

## The Data Pipeline

1. **Field Capture** — Inspector uses mobile PWA to photograph gauge readings, upload PDFs/spreadsheets, dictate voice notes
2. **AI Extraction** — Claude Opus processes each file and produces structured JSON:
   - Images → type classification, OCR text, readings (parameter/value/unit), observations, anomalies, component tags
   - PDFs → sections, tables, charts, images, keywords
   - Spreadsheets → data summaries, observations, key findings
3. **Folder Summarization** — Claude Sonnet generates folder-level summaries and aggregated keywords
4. **Indexed for Search** — All extracted content stored in IndexedDB, ready for querying
5. **Search / Reports** — Users query or generate reports from the structured data

## Feature: Search (The Strong Contender)

The Search feature implements a **3-stage hierarchical relevance pipeline**:

```
User's Natural Language Query
        ↓
[STAGE 1] Score Folders — GPT-4o-mini scores folder summaries (0.0–1.0)
        ↓  Keep folders ≥ 0.5 relevance
[STAGE 2] Score Files — GPT-4o-mini ranks files within relevant folders
        ↓  Keep files ≥ 0.5 relevance
[STAGE 3] Extract Sections — GPT-4.1 finds specific content items
        ↓  Returns pointers: Section@index:1, Table@index:0, Reading@index:2
[RESOLVE] Fetch actual content from IndexedDB
        ↓
Display results with relevance explanations
```

**What makes it powerful:**

- Natural language queries against messy, multi-format inspection data
- Semantic understanding of NDE domain concepts (degradation patterns, retirement thickness, corrosion rates)
- Returns specific sections, tables, readings, charts, and images — not just documents
- Results include explanations of _why_ each piece of content matched
- Content type badges: Section, Table, Chart, Image, Reading
- 8–13 second total search time, ~$0.12–0.20 per query in LLM costs

**Strategic value of Search:**

- An NDE vendor could expose this to their pipeline company client: "Query all your inspection history with natural language"
- Asset owners could ask predictive/analytical questions across years of inspection data
- Creates a new service offering for NDE vendors (not just "we inspect" but "we provide asset intelligence")
- Becomes stickier over time as more data is ingested

## Feature: Report Generation (The Original Vision)

**Status:** Planned, placeholder UI exists, not yet implemented.

**Intended workflow:**

1. Select inspection images and measurement data
2. Choose report template (UT, MT/PT, Visual)
3. AI generates formatted inspection report
4. Export to PDF or Word

**Value proposition:**

- Reduces manual report writing time (currently hours per report)
- Standardizes format across inspectors
- Reduces transcription errors
- Compliance-ready output

**Strategic position:** Primarily an efficiency/cost-reduction tool for the NDE vendor. Saves time and reduces errors, but doesn't create new revenue streams for the vendor.

## Current Product State

- ✅ Mobile field capture (camera, voice, file upload)
- ✅ File browsing with folder tree and thumbnails
- ✅ Image gallery view
- ✅ AI extraction pipeline (images, PDFs, spreadsheets)
- ✅ 3-stage semantic search
- ✅ Real-time pipeline activity logging
- ⏳ Report generation (placeholder UI, not implemented)

## Key Differences: Search vs. Report Generation

| Dimension            | Search                                  | Report Generation               |
| -------------------- | --------------------------------------- | ------------------------------- |
| **Value type**       | Revenue-enabling (new service offering) | Cost-reducing (efficiency tool) |
| **Who benefits**     | NDE vendor AND their end-customer       | Primarily NDE vendor            |
| **Stickiness**       | Increases with more data ingested       | Per-report, transactional       |
| **Competitive moat** | Domain-specific AI + accumulated data   | Commoditizable (template-based) |
| **B2B2B potential**  | High — exposable to end-customers       | Low — internal tool             |
| **Current status**   | Fully implemented, working              | Not yet built                   |
| **Implementation**   | 3-stage LLM pipeline, proven            | Planned                         |

## Landing Page & Positioning

Currently positioned around Report Generation as the core product:

- Hero: "Become a Design Partner"
- How It Works: Import messy data → Generate reports → Deliver production output
- Pain points: Manual reports, errors, no standardization

**If pivoting to Search-first:** The messaging, How It Works flow, and value proposition would need to shift toward "asset intelligence" and the B2B2B value chain.
