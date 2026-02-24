# Plan: Folder Management (Rename, Move, Create, Delete)

## Context

Files uploaded to UMA are auto-categorized by LLM into Development subfolders in IndexedDB (`DevDB`). Users currently cannot override this — they can't rename folders, move files between folders, create new folders, or delete empty ones. This plan adds all four operations with a simple right-click context menu UI.

**Only `viewer/index.html` needs to be modified.** No backend/worker changes required — everything is client-side IndexedDB key manipulation.

---

## Key File

- **`viewer/index.html`** — single file containing all CSS, HTML, and JS

## Key Existing Code to Reuse

- `DevDB.putFile(key, blob, originalName)` (line 1376) — write a file record
- `DevDB.getFile(key)` (line 1394) — read a file record
- `DevDB.deleteFile(key)` (line 1405) — delete a file record
- `DevDB.listFiles(subfolder)` (line 1358) — list files in a subfolder
- `DevDB.listSubfolders()` (line 1340) — list all subfolder names
- `loadDevFolders()` (line 1630) — refresh `state.devFolders`
- `renderFolderTree(folders)` (line 1820) — re-render the sidebar
- `showToast(message, type)` (line 2756) — show success/error notification
- `state.devFolders` (line 1290) — array of subfolder name strings
- `state.expandedDevFolders` (line 1294) — cache of expanded subfolder file lists

---

## Implementation Steps

### Step 1: Add Context Menu CSS (~30 lines, after line ~302)

Add styles for a `.context-menu` positioned absolute div with menu items. Simple dark-themed dropdown matching existing `var(--bg-card)`, `var(--border)`, `var(--text-primary)` tokens.

### Step 2: Add Context Menu HTML (after toast div, ~line 1272)

```html
<div class="context-menu" id="contextMenu" style="display:none">
  <div class="context-menu-item" data-action="rename">Rename Folder</div>
  <div class="context-menu-item" data-action="move">Move to...</div>
  <div class="context-menu-item" data-action="new-folder">New Folder</div>
  <div class="context-menu-item" data-action="delete">Delete Folder</div>
</div>
```

Menu items will be shown/hidden dynamically based on what was right-clicked (folder vs file).

### Step 3: Add Context Menu JS (~40 lines)

- `showContextMenu(e, targetType, targetData)` — positions menu at cursor, shows relevant items
- `hideContextMenu()` — hides menu
- Global `click` and `contextmenu` listeners to dismiss menu
- Wire into `renderFolderTree()`: add `contextmenu` event listeners on `.folder-item[data-dev-sub]` (for folder operations) and `.file-tree-item[data-local]` (for file move)

### Step 4: Rename Folder (~30 lines)

**Trigger**: Right-click dev subfolder → "Rename Folder"

**Logic** (`renameDevFolder(oldName)`):

1. `prompt('Rename folder:', oldName)` → get `newName`
2. Validate: non-empty, no `/`, not duplicate of existing folder
3. `DevDB.listFiles(oldName)` → get all files
4. For each file: `DevDB.getFile(key)` → `DevDB.putFile(newName + '/' + filename, blob, originalName)` → `DevDB.deleteFile(oldKey)`
5. Also move companion `_extraction.json` files (they're already in the same folder, handled by the loop)
6. Update `state.expandedDevFolders`: copy cache entry from old to new name, delete old
7. `await loadDevFolders()` → `renderFolderTree(state.folders)`
8. `showToast('Renamed to ' + newName)`

### Step 5: Move File to Different Folder (~40 lines)

**Trigger**: Right-click a local file in sidebar → "Move to..."

**Logic** (`moveDevFile(fileKey)`):

1. Build list of target folders from `state.devFolders` (exclude current folder)
2. Show a simple `prompt()` or small modal listing folder options — for simplicity, use `prompt()` with numbered list: `"Move to:\n1. Inspection Data\n2. Calibration Records\n..."`
3. Parse selection → `targetFolder`
4. `DevDB.getFile(fileKey)` → `DevDB.putFile(targetFolder + '/' + filename, blob, originalName)` → `DevDB.deleteFile(fileKey)`
5. If companion `_extraction.json` exists, move it too
6. Refresh expanded folder caches for both source and target
7. `renderFolderTree(state.folders)`
8. `showToast('Moved to ' + targetFolder)`

### Step 6: Create New Folder (~15 lines)

**Trigger**: Right-click on "Development" row → "New Folder", or a `+` button on the Development row

**Logic** (`createDevFolder()`):

1. `prompt('New folder name:')` → get `folderName`
2. Validate: non-empty, no `/`, not duplicate
3. Add to `state.devFolders` if not already present
4. To persist the empty folder, store a sentinel: `DevDB.putFile(folderName + '/.folder', new Blob(['']), '.folder')`
5. `renderFolderTree(state.folders)`
6. `showToast('Created folder: ' + folderName)`

**Note**: Using a `.folder` sentinel file ensures `DevDB.listSubfolders()` discovers the folder on next load. The sentinel is hidden from file listings (filter out `.folder` in display).

### Step 7: Delete Empty Folder (~15 lines)

**Trigger**: Right-click dev subfolder → "Delete Folder"

**Logic** (`deleteDevFolder(folderName)`):

1. `DevDB.listFiles(folderName)` → check count (excluding `.folder` sentinel)
2. If non-empty: `showToast('Folder is not empty', 'error')` → return
3. If has `.folder` sentinel: `DevDB.deleteFile(folderName + '/.folder')`
4. Remove from `state.expandedDevFolders`
5. `await loadDevFolders()` → `renderFolderTree(state.folders)`
6. `showToast('Deleted folder: ' + folderName)`

### Step 8: Filter `.folder` Sentinel from Display (~3 lines)

In `renderFolderTree()` where dev subfolder files are rendered (around line 1901), filter out files named `.folder` so the sentinel doesn't appear in the sidebar file list. Same filter in `toggleDevSubfolder()` (line 2131).

---

## Verification

1. Upload a file and let LLM categorize it into a folder
2. **Rename**: Right-click the folder → Rename → verify file appears under new name, old folder gone
3. **Move**: Right-click a file → Move to → pick another folder → verify file moved, extraction JSON moved too
4. **Create**: Right-click Development → New Folder → verify empty folder appears in sidebar
5. **Delete**: Right-click the empty folder → Delete → verify it disappears. Try deleting a non-empty folder → verify error toast
6. Refresh the page → verify all changes persisted (IndexedDB)
