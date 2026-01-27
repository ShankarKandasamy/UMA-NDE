# UMA Viewer - UI Design Specification

## Overview

UMA Viewer is a web-based file management and viewing interface for NDT/NDE inspection data stored in Cloudflare R2. It provides browsing, gallery viewing, and report generation capabilities with a focus on nuclear, maritime, and petrochemical inspection workflows.

**Primary Use Cases:**
- Browse and manage job-related documents and inspection data
- View uploaded images from field inspections (via UMA Capture)
- Generate AI-assisted inspection reports
- Access project specifications and code requirements

---

## Design System

### Visual Style
- **Color Palette:**
  - Background: Dark (`#0a0a0f` / `#12121a`)
  - Cards: Slightly lighter (`#1a1a24`) with subtle borders
  - Accent: Teal/cyan (`#00d4aa`)
- **Typography:** Clean sans-serif, monospace for logo
- **Borders:** Dashed for drop zones, solid subtle for cards
- **Border Radius:** Generous (12-16px)
- **Vibe:** Technical but approachable, dark mode, minimal

---

## Folder Structure

```
UMA_VIEWER/
├─ 📁 Recent                      ← Auto-populated, chronological list
│  └─ (files listed newest → oldest)
│
├─ 📁 Jobs
│  ├─ 📁 job123
│  │  ├─ 📁 Job Package           ← Project inputs/reference docs
│  │  │  ├─ 📁 [AI-Generated]*    ← Folder names determined by AI
│  │  │  ├─ 📁 [AI-Generated]*      based on document content
│  │  │  └─ 📁 ...                  (editable by user)
│  │  ├─ 📁 Uploads               ← From UMA Capture (field data)
│  │  ├─ 📁 Processed             ← AI processing outputs
│  │  └─ 📂 Development           ← Logs/debug (dev only, grayed)
│  │
│  ├─ 📁 job456
│  └─ ...
```

### AI-Generated Folder Examples (Job Package)
When documents are uploaded to Job Package, AI analyzes content and suggests folder names:

| Document Type Detected | Example Folder Name |
|------------------------|---------------------|
| Purchase orders, quotes | `PO & RFQ` |
| Equipment drawings, specs | `Asset Descriptions` |
| Client requirements | `Client Specs` |
| ASME, API, CSA standards | `Codes & Standards` |
| Work procedures, methods | `Procedures` |
| Calibration certificates | `Calibration Records` |
| Safety documentation | `Safety & Permits` |
| Previous inspection reports | `Historical Reports` |

*Folder names are suggestions—users can rename, merge, or reorganize at any time.*

### Folder Definitions

| Folder | Purpose | Contents |
|--------|---------|----------|
| **Recent** | Quick access to latest uploads | Flat chronological list (newest first), links to actual file locations. Click to preview in right pane. |
| **Job Package** | Project requirements & reference docs | AI-organized subfolders based on uploaded document types. Examples: PO/RFQ, Asset descriptions, Client specs, Codes & standards, Procedures. **Subfolder names are AI-suggested on upload and fully editable by users.** |
| **Uploads** | Field inspection data | Photos, measurements, raw data from UMA Capture |
| **Processed** | AI-generated outputs | Extracted data, analysis results, structured reports |
| **Development** | Debug/dev logs only | Console logs, processing logs (hidden in production) |

---

## Job Package: AI Folder Organization

### How It Works

1. **Upload:** User uploads documents to Job Package (drag-and-drop or file picker)
2. **Analysis:** AI analyzes document content (filename, text, metadata)
3. **Classification:** Documents are classified by type (spec, code, procedure, etc.)
4. **Folder Suggestion:** AI suggests appropriate folder names based on content
5. **Organization:** Files are automatically sorted into suggested folders
6. **User Control:** User can rename folders, move files, or create custom folders

### UI Behavior

**During Upload:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Organizing 6 files...                                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━░░░░░░░░░░░ 70%              │
│                                                                 │
│  📁 Codes & Standards (2 files)     ← AI suggested             │
│     └─ ASME_Section_V.pdf                                       │
│     └─ API_570_Piping.pdf                                       │
│                                                                 │
│  📁 Client Specs (1 file)           ← AI suggested             │
│     └─ ABC_Corp_Requirements.docx                               │
│                                                                 │
│  📁 Procedures (3 files)            ← AI suggested             │
│     └─ UT_Procedure_Rev3.pdf                                    │
│     └─ MT_Procedure.pdf                                         │
│     └─ Calibration_Method.pdf                                   │
│                                                                 │
│  [✏️ Edit Organization]  [✅ Accept & Upload]                   │
└─────────────────────────────────────────────────────────────────┘
```

**Edit Organization Modal:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Edit Folder Organization                              [✕]     │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  📁 Codes & Standards          [✏️ Rename] [🗑️ Delete Folder]  │
│     ☑️ ASME_Section_V.pdf      [Move to: ▼]                    │
│     ☑️ API_570_Piping.pdf      [Move to: ▼]                    │
│                                                                 │
│  📁 Client Specs               [✏️ Rename] [🗑️ Delete Folder]  │
│     ☑️ ABC_Corp_Requirements   [Move to: ▼]                    │
│                                                                 │
│  📁 Procedures                 [✏️ Rename] [🗑️ Delete Folder]  │
│     ☑️ UT_Procedure_Rev3.pdf   [Move to: ▼]                    │
│     ☐ MT_Procedure.pdf         [Move to: ▼]  ← Unchecked =     │
│     ☑️ Calibration_Method.pdf  [Move to: ▼]    exclude file    │
│                                                                 │
│  [➕ Create New Folder]                                         │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  [Cancel]                              [Save & Upload]          │
└─────────────────────────────────────────────────────────────────┘
```

### Folder Renaming (Post-Upload)

Users can rename any AI-generated folder at any time:

- **Right-click context menu:** Rename, Move, Delete
- **Inline edit:** Click folder name → editable text field
- **Bulk operations:** Select multiple folders for merge/reorganize

### AI Classification Confidence

For transparency, the system can optionally show classification confidence:

| Confidence Level | UI Indicator | Behavior |
|------------------|--------------|----------|
| High (>90%) | ✅ Green dot | Auto-sort, no prompt |
| Medium (70-90%) | 🟡 Yellow dot | Auto-sort, highlight for review |
| Low (<70%) | 🟠 Orange dot | Place in "Unsorted" folder, prompt user |

**Unsorted Folder:** Files with low classification confidence are placed in a temporary "Unsorted" folder within Job Package for manual organization.

---

## Tab Navigation

### Tab 1: Browse 📁

**Purpose:** Windows Explorer-style file navigation with folder tree and file grid.

**Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│  UMA_VIEWER                                      ● Connected    │
├─────────────────────────────────────────────────────────────────┤
│  [📁 Browse]    [🖼️ Gallery]    [📋 Reports]                    │
├─────────────┬───────────────────────────────────────────────────┤
│ LEFT PANE   │ RIGHT PANE                                        │
│ Folder Tree │ File Grid + Breadcrumbs                           │
│             │                                                   │
│ Collapsible │ 📍 Jobs / job123 / Uploads                        │
│ Tree View   │ ───────────────────────────────────               │
│             │                                                   │
│             │ ┌─────┐ ┌─────┐ ┌─────┐                          │
│             │ │ 🖼️  │ │ 📄  │ │ 📊  │                          │
│             │ │ img │ │ pdf │ │ csv │                          │
│             │ └─────┘ └─────┘ └─────┘                          │
│             │                                                   │
│ 💾 Storage  │ [🔍 Filter] [⬆️ Upload] [➕ New Folder]          │
│ Usage Bar   │                                                   │
└─────────────┴───────────────────────────────────────────────────┘
```

**Key Features:**
- **Left Sidebar:**
  - Collapsible folder tree
  - Recent folder at top (auto-refreshing)
  - Jobs folder with expandable hierarchy
  - Storage usage indicator at bottom
- **Right Panel:**
  - Breadcrumb navigation
  - File grid (medium icons, like Windows Explorer)
  - Actions: Filter, Upload, New Folder
  - Click folder → navigate into it
  - Click file → preview modal/panel
- **Recent Folder Behavior:**
  - Auto-refreshes (WebSocket or polling)
  - Flat list sorted by upload time (newest first)
  - Click file → preview in right pane (same as all other files)
  - Shows file thumbnail, name, source job/folder, timestamp
  - Files are references (links) to actual location in Jobs tree
- **Job Package Folder Indicators:**
  - AI-generated folders show subtle "✨ AI" badge (dismissible)
  - Renamed folders lose the AI badge
  - Tooltip: "This folder was suggested by AI based on document content"

---

### Tab 2: Gallery 🖼️

**Purpose:** Image-only view with large thumbnails for quick visual scanning of all inspection photos.

**Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│  UMA_VIEWER                                      ● Connected    │
├─────────────────────────────────────────────────────────────────┤
│  [📁 Browse]    [🖼️ Gallery]    [📋 Reports]                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Image Gallery         [All Jobs ▼] [Today ▼] [Grid ▼]        │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐                 │
│  │            │ │            │ │            │                 │
│  │  [Preview] │ │  [Preview] │ │  [Preview] │                 │
│  │            │ │            │ │            │                 │
│  ├────────────┤ ├────────────┤ ├────────────┤                 │
│  │ filename   │ │ filename   │ │ filename   │                 │
│  │ job/folder │ │ job/folder │ │ job/folder │                 │
│  │ size • time│ │ size • time│ │ size • time│                 │
│  │ [📂][👁️][⬇️]│ │ [📂][👁️][⬇️]│ │ [📂][👁️][⬇️]│                 │
│  └────────────┘ └────────────┘ └────────────┘                 │
│                                                                 │
│  Showing 47 images • 234 MB total        [Load More...]       │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- **Filters:**
  - By job (All Jobs, specific job)
  - By date (Today, This Week, This Month, All Time)
  - By folder type (All, Uploads only, Processed only, Job Package only)
- **View Modes:**
  - Grid (large thumbnails - default)
  - List (with metadata table)
  - Slideshow
- **Per-Image Actions:**
  - [📂 Go] - Navigate to file location in Browse tab
  - [👁️ View] - Open lightbox/full-size viewer
  - [⬇️ Download] - Direct download
- **Supported Formats:** 
  - .jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp
  - Excludes: PDFs, docs, spreadsheets
- **Performance:** Lazy loading, virtual scrolling for 100+ images

---

### Tab 3: Reports 📋

**Purpose:** Generate AI-assisted inspection reports from uploaded data.

**Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│  UMA_VIEWER                                      ● Connected    │
├─────────────────────────────────────────────────────────────────┤
│  [📁 Browse]    [🖼️ Gallery]    [📋 Reports]                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Generate Report                                                │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Source Folder   [job123 / Uploads                      ▼] [📁] │
│                                                                 │
│  Report Type     ○ UT Thickness Survey                          │
│                  ○ Weld Inspection (MT/PT)                      │
│                  ○ Visual Inspection                            │
│                  ● Custom / AI-Assisted                         │
│                                                                 │
│  Code/Standard   [API 570 - Piping Inspection          ▼]      │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Included Files (4)                      [Select All]      │ │
│  │ ☑️ gauge_reading.jpg   ☑️ setup_photo.jpg                 │ │
│  │ ☑️ thickness_data.csv  ☐ _metadata.json                   │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ [✨ Generate Report]                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  Previous Reports                                               │
│                                                                 │
│  📄 job123_doc456_report_2026-01-21.pdf    [View] [Download]   │
│  📄 job456_doc001_report_2026-01-20.pdf    [View] [Download]   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- Source folder selection (dropdown + file browser)
- Report type templates (UT, MT/PT, Visual, Custom)
- Code/Standard selection (for compliance requirements)
- File inclusion checklist
- Generate button triggers AI processing
- History of previous reports with view/download actions

**MVP Note:** This can start as a workflow placeholder. Full AI report generation can be implemented in later phases.

---

## Technical Considerations

### AI Folder Classification

**Document Analysis Pipeline:**
1. **Filename parsing:** Extract keywords from filename (e.g., "ASME", "procedure", "spec")
2. **Content extraction:** OCR for images, text extraction for PDFs/docs
3. **Classification model:** Categorize document type using:
   - Rule-based matching (keywords, patterns)
   - ML classifier (future enhancement)
4. **Folder mapping:** Map document type to suggested folder name

**Classification Rules (MVP):**
| Pattern/Keyword | Suggested Folder |
|-----------------|------------------|
| `PO`, `purchase`, `quote`, `RFQ`, `invoice` | PO & RFQ |
| `ASME`, `API`, `CSA`, `code`, `standard` | Codes & Standards |
| `spec`, `requirement`, `client`, `customer` | Client Specs |
| `procedure`, `method`, `instruction`, `SOP` | Procedures |
| `drawing`, `P&ID`, `isometric`, `asset` | Asset Descriptions |
| `calibration`, `certificate`, `cert` | Calibration Records |
| `safety`, `permit`, `JSA`, `hazard` | Safety & Permits |
| `report`, `historical`, `previous` | Historical Reports |

**Fallback Behavior:**
- Unclassified files → "Unsorted" folder
- User prompted to manually organize or confirm AI suggestion

### Performance Optimization
- **Gallery Tab:**
  - Virtual scrolling for 100+ images
  - Pre-generated thumbnails cached in R2
  - Lazy loading images as user scrolls
  - Pagination or infinite scroll for large datasets
- **Browse Tab:**
  - Lazy-load folder contents on expand
  - Debounced search/filter
- **Recent:**
  - WebSocket for real-time updates (preferred)
  - Polling fallback (30-60s interval)
- **AI Classification:**
  - Run classification asynchronously during upload
  - Show progress indicator while analyzing
  - Cache classification results in metadata

### Storage Strategy
- **Thumbnail Generation:**
  - Separate R2 bucket or prefix for thumbnails
  - Generated on upload or on-demand with caching
- **Metadata:**
  - `_metadata.json` files at each folder level
  - Include upload session info, notes, timestamps
  - **New:** Include `ai_generated: true/false` flag for folders
  - **New:** Include `original_ai_name` to track renames
- **Folder Structure:**
  - R2 object keys mirror UI folder hierarchy
  - Example: `jobs/job123/Uploads/gauge_setup.jpg`
  - Example: `jobs/job123/Job Package/Codes & Standards/ASME_V.pdf`

### Development Mode
- **Development Folder:**
  - Hidden in production builds (environment variable)
  - Grayed/collapsed by default in dev mode
  - Contains console logs, processing logs, debug data

### Security & Access
- **Future consideration:** Role-based folder permissions
  - Inspector: Read/write Uploads
  - Reviewer: Read all, write Processed
  - Client: Read-only access to specific reports

---

## API Integration Points

### Cloudflare R2 Operations
1. **List objects** - Populate folder tree and file grids
2. **Get object** - Download/preview files
3. **Put object** - Upload new files
4. **Delete object** - Remove files (with confirmation)
5. **Get object metadata** - File info without downloading

### AI Classification API (New)
1. **Classify document** - Analyze uploaded file, return suggested folder
   - Input: File content, filename, mime type
   - Output: `{ suggestedFolder: string, confidence: number, keywords: string[] }`
2. **Batch classify** - Classify multiple files in single request
3. **Reclassify** - Re-run classification on existing file (if rules updated)

### Future RAG Integration
- **Codes & Standards folder:**
  - Query external code databases (ASME, API, etc.)
  - Store retrieved requirements as markdown in folder
  - Link back to source for updates

### Report Generation API
- **Input:** Selected files + report type + code reference
- **Output:** Generated PDF report in Processed folder
- **Status:** Progress updates via WebSocket or polling

---

## User Experience Patterns

### Navigation Flow
1. **Typical workflow:**
   - Land on Browse tab
   - Check Recent folder for new field data
   - Navigate to specific job folder
   - Review Uploads
   - Switch to Gallery for visual inspection
   - Generate report from Reports tab

2. **Quick image review:**
   - Go directly to Gallery tab
   - Filter by job or date
   - Click [👁️ View] for lightbox
   - Click [📂 Go] to see context in Browse

3. **Job Package upload flow (New):**
   - Navigate to Job Package folder
   - Drag-and-drop documents
   - Review AI-suggested folder organization
   - Edit folder names or file placement as needed
   - Confirm upload

### Error Handling
- **Upload failures:** Retry button, clear error messages
- **Large files:** Progress bar, cancel option
- **Network issues:** Graceful degradation, offline indicators
- **Missing files:** Clear "File not found" states
- **Classification failures (New):** Place in "Unsorted", notify user

### Empty States
- **New job:** Show template creation option
- **No recent uploads:** "No files uploaded yet. Upload inspection data to see it here."
- **Empty gallery:** Guide to upload images
- **No reports:** Show "Generate your first report" CTA
- **Empty Job Package (New):** Show "Upload project documents to get started. AI will help organize them into folders."

---

## Open Questions for Implementation

1. **Recent folder cleanup:** Auto-remove entries after X days? Manual clear? Max item count?
2. **Gallery default filter:** Show all images or Uploads only by default?
3. **Job templates:** Auto-create folder structure for new jobs?
4. **Cross-job selection:** Support multi-job file selection for comparison?
5. **Archive strategy:** Separate archive folder/status for completed jobs?
6. **Mobile responsive:** Priority level for mobile/tablet layouts?
7. **AI folder naming (New):** Allow user to train/customize classification rules per account?
8. **Folder merge (New):** When AI suggests folder that already exists, auto-merge or prompt?
9. **Confidence threshold (New):** What confidence level triggers "Unsorted" placement?
10. **Bulk reclassification (New):** Allow re-running AI classification on existing Job Package?

---

## Version History

- **v1.1** (2026-01-22): Added AI folder organization for Job Package
  - AI-determined folder names based on document content
  - User-editable folder names post-classification
  - Classification confidence indicators
  - Edit Organization modal during upload
  - Classification rules and API specification
  - Simplified "Recent" folder (flat chronological list, standard preview behavior)
- **v1.0** (2026-01-22): Initial design specification
  - Three-tab structure: Browse, Gallery, Reports
  - Four-folder job structure: Job Package, Uploads, Processed, Development
  - Recent folder in Browse tab (flat chronological list)
  - Gallery tab for image-only viewing

---

## References

- **Storage Backend:** Cloudflare R2
- **Upload Source:** UMA Capture (Progressive Web App)
- **Target Industries:** Nuclear, maritime, petrochemical NDT/NDE
- **Compliance Codes:** ASME, API, CSA, client-specific standards
