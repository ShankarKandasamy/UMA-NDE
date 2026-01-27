# UMA Viewer - Implementation Plan

## Overview

This document outlines the implementation plan for UMA Viewer, a web-based file management interface for NDT/NDE inspection data stored in Cloudflare R2. The viewer complements UMA Capture by providing browsing, gallery viewing, and (future) report generation capabilities.

**Design Reference:** `docs/viewer_design.md`

---

## Architecture Summary

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   UMA Capture   │────▶│   Cloudflare    │◀────│   UMA Viewer    │
│   (PWA)         │     │   Worker API    │     │   (PWA)         │
│   /capture/     │     │   /uma-api/     │     │   /viewer/      │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                        ┌────────▼────────┐
                        │  Cloudflare R2  │
                        │  (Object Store) │
                        └─────────────────┘
```

**Tech Stack:**
- Frontend: Vanilla HTML/CSS/JavaScript (no build step, single-file PWA)
- Backend: Cloudflare Workers
- Storage: Cloudflare R2
- Styling: CSS variables matching capture app design system

---

## Current R2 Storage Structure

```
uma-inspection-data/
├── 2026-01-20/
│   ├── m5abc123-x7y8z9/
│   │   ├── _metadata.json      ← Session info, notes, file list
│   │   ├── abc12345.jpg
│   │   └── def67890.csv
│   └── m5def456-a1b2c3/
│       ├── _metadata.json
│       └── ghi11111.pdf
└── 2026-01-21/
    └── ...
```

**Metadata JSON Structure:**
```json
{
  "sessionId": "m5abc123-x7y8z9",
  "timestamp": "2026-01-20T14:30:00.000Z",
  "notes": "Pipe weld inspection - Section A",
  "device": "Mozilla/5.0 ...",
  "files": [
    { "fileId": "abc12345", "originalName": "IMG_001.jpg", "type": "image/jpeg" },
    { "fileId": "def67890", "originalName": "readings.csv", "type": "text/csv" }
  ]
}
```

---

## Phase 1: Backend API Extensions

**Goal:** Add endpoints to list and retrieve files from R2.

### 1.1 New Routes in `uma-api/worker.js`

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/list` | List objects by prefix with pagination |
| GET | `/list-folders` | List top-level date folders |
| GET | `/file/*` | Stream a file by its full key |
| GET | `/thumbnail/*` | Return resized image (or original if not image) |

### 1.2 Implementation Details

#### `/list` Endpoint
```
GET /list?prefix=2026-01-20/&cursor=xxx&limit=100
```

**Response:**
```json
{
  "objects": [
    {
      "key": "2026-01-20/m5abc123/abc12345.jpg",
      "size": 245000,
      "uploaded": "2026-01-20T14:30:00.000Z",
      "httpMetadata": { "contentType": "image/jpeg" },
      "customMetadata": { "originalName": "IMG_001.jpg" }
    }
  ],
  "truncated": false,
  "cursor": null
}
```

**Implementation Notes:**
- Use `BUCKET.list({ prefix, cursor, limit })`
- Filter out `_metadata.json` from regular listings (fetch separately)
- Include custom metadata in response

#### `/list-folders` Endpoint
```
GET /list-folders
```

**Response:**
```json
{
  "folders": [
    { "name": "2026-01-22", "sessionCount": 3 },
    { "name": "2026-01-21", "sessionCount": 5 },
    { "name": "2026-01-20", "sessionCount": 2 }
  ]
}
```

**Implementation Notes:**
- Use `BUCKET.list({ delimiter: '/' })` to get top-level prefixes
- Sort descending (newest first)
- Count sessions per date folder

#### `/file/*` Endpoint
```
GET /file/2026-01-20/m5abc123/abc12345.jpg
```

**Response:** Raw file stream with appropriate Content-Type header.

**Implementation Notes:**
- Use `BUCKET.get(key)`
- Set `Content-Type` from stored metadata
- Set `Content-Disposition` for downloads
- Support `Range` header for video/large files (future)

#### `/thumbnail/*` Endpoint (Optional - Phase 6)
For now, serve original images. Later, integrate Cloudflare Images for resizing.

### 1.3 Authentication

All endpoints require `X-API-Key` header (same as upload).

### 1.4 CORS

Update CORS headers to allow GET requests from viewer origin.

### 1.5 Testing Checklist

- [ ] `curl -H "X-API-Key: xxx" https://api.../list-folders` returns date folders
- [ ] `curl -H "X-API-Key: xxx" https://api.../list?prefix=2026-01-20/` returns files
- [ ] `curl -H "X-API-Key: xxx" https://api.../file/2026-01-20/session/file.jpg` returns image
- [ ] Invalid API key returns 401
- [ ] Non-existent file returns 404

---

## Phase 2: Viewer Shell & Navigation

**Goal:** Build the basic HTML structure with tab navigation and styling.

### 2.1 HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>UMA Viewer</title>
  <link rel="manifest" href="manifest.json">
  <!-- Design system CSS -->
</head>
<body>
  <!-- Header -->
  <header class="header">
    <div class="logo">UMA_VIEWER</div>
    <div class="status" id="status">● Connecting...</div>
  </header>

  <!-- Tab Bar -->
  <nav class="tabs">
    <button class="tab active" data-tab="browse">Browse</button>
    <button class="tab" data-tab="gallery">Gallery</button>
    <button class="tab" data-tab="reports">Reports</button>
  </nav>

  <!-- Tab Content -->
  <main class="content">
    <section id="browse-tab" class="tab-content active">...</section>
    <section id="gallery-tab" class="tab-content">...</section>
    <section id="reports-tab" class="tab-content">...</section>
  </main>

  <!-- Modal Container -->
  <div id="modal" class="modal hidden">...</div>

  <script>/* JavaScript */</script>
</body>
</html>
```

### 2.2 CSS Design System

Match capture app styling:

```css
:root {
  --bg-primary: #0a0a0f;
  --bg-secondary: #12121a;
  --bg-card: #1a1a24;
  --accent: #00d4aa;
  --accent-hover: #00e5bb;
  --text-primary: #ffffff;
  --text-secondary: #888;
  --border-color: #2a2a3a;
  --border-radius: 12px;
  --font-sans: 'Space Grotesk', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}
```

### 2.3 JavaScript Structure

```javascript
// State
const state = {
  currentTab: 'browse',
  currentPath: [],           // Breadcrumb path
  selectedFolder: null,
  files: [],
  folders: [],
  galleryImages: [],
  isLoading: false
};

// API Helper
async function api(endpoint, options = {}) { ... }

// Tab Navigation
function switchTab(tabName) { ... }

// Initialize
document.addEventListener('DOMContentLoaded', init);
```

### 2.4 Testing Checklist

- [ ] Page loads with header, tabs, and content area
- [ ] Clicking tabs switches visible content
- [ ] Status indicator shows "Connecting..." then "Connected" or "Offline"
- [ ] Styling matches capture app (dark theme, accent color)
- [ ] Responsive on mobile and desktop

---

## Phase 3: Browse Tab - Folder Tree (Left Sidebar)

**Goal:** Display collapsible folder hierarchy from R2 data.

### 3.1 Layout

```
┌─────────────┬─────────────────────────────────────┐
│ FOLDERS     │ (Right panel - Phase 4)             │
│             │                                     │
│ ▼ Recent    │                                     │
│   file1.jpg │                                     │
│   file2.pdf │                                     │
│             │                                     │
│ ▼ 2026-01-22│                                     │
│   ▶ session1│                                     │
│   ▶ session2│                                     │
│             │                                     │
│ ▶ 2026-01-21│                                     │
│ ▶ 2026-01-20│                                     │
│             │                                     │
│ ─────────── │                                     │
│ Storage: 2GB│                                     │
└─────────────┴─────────────────────────────────────┘
```

### 3.2 Data Fetching

```javascript
async function loadFolderTree() {
  // 1. Fetch date folders
  const { folders } = await api('/list-folders');

  // 2. Render tree
  renderFolderTree(folders);
}

async function expandDateFolder(date) {
  // Fetch sessions within date folder
  const { objects } = await api(`/list?prefix=${date}/&delimiter=/`);
  // Extract unique session IDs
  // Render as children
}
```

### 3.3 Recent Folder

Special handling for "Recent":
- Fetches last 20 files across all dates (sorted by upload time)
- Uses metadata timestamps for sorting
- Shows flat list (no nesting)

```javascript
async function loadRecentFiles() {
  // Option A: Backend endpoint for recent files
  // Option B: Fetch all metadata.json files, sort client-side

  // For MVP, use Option B with caching
}
```

### 3.4 Tree Interactions

| Action | Behavior |
|--------|----------|
| Click folder | Expand/collapse + load files in right panel |
| Click file (in Recent) | Open preview modal |
| Hover folder | Show file count badge |

### 3.5 Testing Checklist

- [ ] Folder tree loads on page load
- [ ] Date folders appear in descending order (newest first)
- [ ] Clicking date folder expands to show sessions
- [ ] Clicking session loads files in right panel
- [ ] "Recent" folder shows latest files
- [ ] Loading states shown during fetch

---

## Phase 4: Browse Tab - File Grid (Right Panel)

**Goal:** Display files in selected folder with breadcrumb navigation.

### 4.1 Layout

```
┌─────────────────────────────────────────────────────┐
│ 📍 2026-01-22 / m5abc123                            │
├─────────────────────────────────────────────────────┤
│ [Filter ▼]                      [Upload] [+ Folder] │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│ │  IMG    │ │  PDF    │ │  CSV    │ │  XLSX   │   │
│ │ [thumb] │ │  icon   │ │  icon   │ │  icon   │   │
│ │         │ │         │ │         │ │         │   │
│ ├─────────┤ ├─────────┤ ├─────────┤ ├─────────┤   │
│ │IMG_001  │ │report   │ │readings │ │data     │   │
│ │.jpg     │ │.pdf     │ │.csv     │ │.xlsx    │   │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 4.2 Breadcrumb Navigation

```javascript
function renderBreadcrumbs(path) {
  // path = ['2026-01-22', 'm5abc123']
  // Render: Home > 2026-01-22 > m5abc123
  // Each segment is clickable
}
```

### 4.3 File Cards

```html
<div class="file-card" data-key="2026-01-22/m5abc123/abc12345.jpg">
  <div class="file-thumbnail">
    <!-- Image: actual thumbnail -->
    <!-- Other: file type icon -->
  </div>
  <div class="file-name">IMG_001.jpg</div>
  <div class="file-meta">245 KB</div>
</div>
```

**Thumbnail Logic:**
- Images: Load actual image (lazy loading with IntersectionObserver)
- PDF: Show PDF icon
- CSV/Excel: Show spreadsheet icon
- Other: Generic file icon

### 4.4 File Card Actions

| Action | Behavior |
|--------|----------|
| Single click | Select file (highlight) |
| Double click | Open preview modal |
| Right click | Context menu (Download, Delete, Info) |

### 4.5 Filter Bar

Filter options:
- File type: All, Images, Documents, Data
- Sort: Name, Date, Size

### 4.6 Testing Checklist

- [ ] Selecting folder in tree shows files in grid
- [ ] Breadcrumbs update and are clickable
- [ ] Image thumbnails load (with lazy loading)
- [ ] Non-image files show appropriate icons
- [ ] Filter dropdown works
- [ ] Empty folder shows appropriate message

---

## Phase 5: File Preview Modal

**Goal:** View files in a modal overlay without leaving the browse tab.

### 5.1 Modal Structure

```html
<div class="modal" id="preview-modal">
  <div class="modal-backdrop"></div>
  <div class="modal-content">
    <header class="modal-header">
      <h2 class="modal-title">IMG_001.jpg</h2>
      <button class="modal-close">&times;</button>
    </header>
    <div class="modal-body">
      <!-- Image viewer / PDF embed / File info -->
    </div>
    <footer class="modal-footer">
      <button class="btn">Download</button>
      <button class="btn">Open in New Tab</button>
    </footer>
  </div>
</div>
```

### 5.2 Preview Types

| File Type | Preview Method |
|-----------|----------------|
| Images (jpg, png, gif, webp) | `<img>` with zoom/pan |
| PDF | `<iframe>` or `<embed>` |
| Text (txt, json, csv) | `<pre>` with syntax highlighting |
| Office docs | Link to open externally |
| Other | File info + download button |

### 5.3 Image Viewer Features

- Fit to modal by default
- Zoom in/out buttons
- Pan when zoomed
- Keyboard: Arrow keys for next/prev, Escape to close

### 5.4 Metadata Panel

Show alongside preview:
```
Original Name: IMG_001.jpg
Size: 245 KB
Uploaded: Jan 20, 2026 2:30 PM
Session Notes: "Pipe weld inspection - Section A"
```

### 5.5 Testing Checklist

- [ ] Clicking file opens modal
- [ ] Images display correctly with zoom
- [ ] PDFs render in iframe
- [ ] Text files show formatted content
- [ ] Download button works
- [ ] Escape key closes modal
- [ ] Clicking backdrop closes modal

---

## Phase 6: Gallery Tab

**Goal:** Image-only masonry grid with filtering and lightbox.

### 6.1 Layout

```
┌─────────────────────────────────────────────────────┐
│ Image Gallery                                        │
│ [All Dates ▼] [All Sessions ▼]           47 images  │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│ │          │ │          │ │          │            │
│ │  IMAGE   │ │  IMAGE   │ │  IMAGE   │  ...       │
│ │          │ │          │ │          │            │
│ └──────────┘ └──────────┘ └──────────┘            │
│                                                     │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│ │          │ │          │ │          │            │
│ │  IMAGE   │ │  IMAGE   │ │  IMAGE   │  ...       │
│ │          │ │          │ │          │            │
│ └──────────┘ └──────────┘ └──────────┘            │
│                                                     │
│                    [Load More]                      │
└─────────────────────────────────────────────────────┘
```

### 6.2 Data Loading

```javascript
async function loadGalleryImages(filters = {}) {
  const { date, session } = filters;

  // Fetch all image files
  let prefix = '';
  if (date) prefix = `${date}/`;
  if (session) prefix = `${date}/${session}/`;

  const { objects } = await api(`/list?prefix=${prefix}`);

  // Filter to images only
  const images = objects.filter(obj =>
    /\.(jpg|jpeg|png|gif|webp)$/i.test(obj.key)
  );

  return images;
}
```

### 6.3 Lazy Loading

Use IntersectionObserver for performance:

```javascript
const imageObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      imageObserver.unobserve(img);
    }
  });
}, { rootMargin: '100px' });
```

### 6.4 Lightbox

Full-screen image viewer with:
- Previous/Next navigation
- Swipe gestures on mobile
- Keyboard navigation (arrows, escape)
- Image counter (3 of 47)

### 6.5 Testing Checklist

- [ ] Gallery loads all images across sessions
- [ ] Filters work (by date, by session)
- [ ] Lazy loading works (images load as scrolled into view)
- [ ] Clicking image opens lightbox
- [ ] Lightbox navigation works (arrows, swipe)
- [ ] "Load More" pagination works for large galleries

---

## Phase 7: Recent Folder Auto-Refresh

**Goal:** Recent folder updates automatically via polling.

### 7.1 Polling Implementation

```javascript
let pollInterval = null;

function startRecentPolling() {
  // Poll every 10 seconds
  pollInterval = setInterval(async () => {
    if (state.currentTab === 'browse' && isRecentSelected()) {
      await refreshRecentFiles();
    }
  }, 10000);
}

function stopRecentPolling() {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
}
```

### 7.2 Change Detection

```javascript
async function refreshRecentFiles() {
  const newFiles = await fetchRecentFiles();
  const currentKeys = new Set(state.recentFiles.map(f => f.key));

  const addedFiles = newFiles.filter(f => !currentKeys.has(f.key));

  if (addedFiles.length > 0) {
    // Update state
    state.recentFiles = newFiles;

    // Re-render with highlight animation
    renderRecentFiles(addedFiles);

    // Optional: Show toast notification
    showToast(`${addedFiles.length} new file(s) uploaded`);
  }
}
```

### 7.3 Visual Indicator

New files get a brief highlight animation:

```css
.file-card.new {
  animation: highlight 2s ease-out;
}

@keyframes highlight {
  0% { background-color: var(--accent); }
  100% { background-color: var(--bg-card); }
}
```

### 7.4 Testing Checklist

- [ ] Recent folder updates within 10 seconds of new upload
- [ ] New files appear at top of list
- [ ] New files have highlight animation
- [ ] Polling stops when not viewing Recent folder
- [ ] Polling stops when page is hidden (visibility API)

---

## Phase 8: Reports Tab (Placeholder)

**Goal:** Placeholder UI for future AI report generation.

### 8.1 Layout

```
┌─────────────────────────────────────────────────────┐
│ Generate Report                                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  This feature is coming soon.                       │
│                                                     │
│  AI-assisted report generation will allow you to:   │
│  • Select inspection images and data                │
│  • Choose report templates (UT, MT/PT, Visual)      │
│  • Generate formatted inspection reports            │
│  • Export to PDF or Word format                     │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │                                             │   │
│  │         [Report Preview Mockup]             │   │
│  │                                             │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 8.2 Disabled Form Elements

Show the intended UI but disabled:

```html
<div class="form-group">
  <label>Source Folder</label>
  <select disabled>
    <option>Select a folder...</option>
  </select>
</div>

<div class="form-group">
  <label>Report Type</label>
  <select disabled>
    <option>UT Inspection Report</option>
    <option>MT/PT Report</option>
    <option>Visual Inspection Report</option>
  </select>
</div>

<button class="btn btn-primary" disabled>Generate Report</button>
```

### 8.3 Testing Checklist

- [ ] Reports tab shows placeholder content
- [ ] Form elements are visible but disabled
- [ ] "Coming Soon" message is clear

---

## File Summary

| File | Changes |
|------|---------|
| `uma-api/worker.js` | Add `/list`, `/list-folders`, `/file/*` endpoints |
| `viewer/index.html` | Complete rewrite with full UI |
| `viewer/sw.js` | Update cached files list |
| `viewer/manifest.json` | Update if needed |

---

## Testing Strategy

### Unit Testing (Manual)
Each phase includes a testing checklist. Complete all items before moving to next phase.

### Integration Testing
After each phase, verify:
1. Capture app still works (no regressions)
2. Viewer connects to API successfully
3. Data flows correctly from R2 to UI

### Cross-Browser Testing
Test in:
- Chrome (desktop + mobile)
- Safari (desktop + iOS)
- Firefox
- Edge

### Performance Testing (Phase 6+)
- Load 100+ images in gallery
- Verify lazy loading works
- Check memory usage doesn't grow unbounded

---

## Future Enhancements (Post-MVP)

1. **Job-based organization** - Group sessions into jobs
2. **AI folder classification** - Auto-organize Job Package uploads
3. **Search** - Full-text search across filenames and notes
4. **Thumbnails API** - Server-side image resizing via Cloudflare Images
5. **WebSocket updates** - Replace polling with real-time notifications
6. **Offline support** - Cache recently viewed files
7. **Batch operations** - Multi-select for download/delete
8. **Report generation** - Full AI report builder

---

## Development Order

```
Phase 1 ──▶ Phase 2 ──▶ Phase 3 ──▶ Phase 4 ──▶ Phase 5
(Backend)   (Shell)     (Tree)      (Grid)      (Modal)
                                        │
                                        ▼
Phase 8 ◀── Phase 7 ◀── Phase 6 ◀───────┘
(Reports)   (Polling)   (Gallery)
```

Start with Phase 1 (backend) as it unblocks all frontend work.
