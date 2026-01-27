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
| A New one if none of the above apply | `AI Decides` |

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



### Folder Renaming (Post-Upload)

Users can rename any AI-generated folder at any time:

- **Right-click context menu:** Rename, Move, Delete
- **Inline edit:** Click folder name → editable text field
- **Bulk operations:** Select multiple folders for merge/reorganize



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
│             │ [🔍 Filter] [⬆️ Upload] [➕ New Folder]          │
│             │                                                   │
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
  - Auto-refreshes (polling - every 10s)
  - Flat list sorted by upload time (newest first)
  - Click file → preview in right pane (same as all other files)
  - Shows file thumbnail, name, source job/folder, timestamp
  - Files are references (links) to actual location in Jobs tree
- **Job Package Folder Indicators:**
  - AI-generated folders 
  - folder name can be changed by user

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
│  Image Gallery         [All Jobs ▼]                             │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐                 │
│  │            │ │            │ │            │                 │
│  │  [Preview] │ │  [Preview] │ │  [Preview] │     ....        │
│  │            │ │            │ │            │                 │
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
│    <COMING SOON - THIS IS JUST A PLACEHOLDER>
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

## References

- **Storage Backend:** Cloudflare R2
- **Upload Source:** UMA Capture (Progressive Web App)

