# ============================================================
# Clear all objects from the uma-inspection-data R2 bucket
#
# This removes all files/folders visible in the Viewer app.
# Files in the Viewer's "development" folder are stored in
# IndexedDB (browser-local) and are NOT affected by this script.
#
# Prerequisites: wrangler CLI installed and authenticated
#   npm install -g wrangler
#   wrangler login
#
# Run with: powershell -ExecutionPolicy Bypass -File .\clear-r2-bucket.ps1
# ============================================================

$BUCKET_NAME = "uma-inspection-data"

Write-Host "=== R2 Bucket Cleanup: $BUCKET_NAME ===" -ForegroundColor Cyan
Write-Host ""

# List all objects in the bucket
Write-Host "Fetching object list..."
$rawOutput = npx wrangler r2 object list $BUCKET_NAME 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to list bucket objects." -ForegroundColor Red
    Write-Host "Make sure wrangler is installed and you're logged in:"
    Write-Host "  npm install -g wrangler"
    Write-Host "  wrangler login"
    exit 1
}

# Parse JSON output to extract keys
$keys = ($rawOutput | Out-String | ConvertFrom-Json) | ForEach-Object {
    if ($_.objects) { $_.objects } elseif ($_.key) { $_ } else { $_ }
} | ForEach-Object { $_.key } | Where-Object { $_ }

if (-not $keys -or $keys.Count -eq 0) {
    Write-Host "Bucket is already empty. Nothing to delete." -ForegroundColor Green
    exit 0
}

$count = @($keys).Count
Write-Host "Found $count object(s) in bucket." -ForegroundColor Yellow
Write-Host ""

# Show preview
Write-Host "Sample objects:"
@($keys) | Select-Object -First 10 | ForEach-Object { Write-Host "  $_" }
if ($count -gt 10) {
    Write-Host "  ... and $($count - 10) more"
}
Write-Host ""

# Confirm
$confirm = Read-Host "Delete ALL $count objects from $BUCKET_NAME? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Aborted."
    exit 0
}

Write-Host ""
Write-Host "Deleting objects..."

$deleted = 0
$failed = 0

foreach ($key in @($keys)) {
    if ($key) {
        npx wrangler r2 object delete "$BUCKET_NAME/$key" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $deleted++
            Write-Host "  Deleted: $key" -ForegroundColor Green
        } else {
            $failed++
            Write-Host "  FAILED:  $key" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Cyan
Write-Host "Deleted: $deleted" -ForegroundColor Green
if ($failed -gt 0) {
    Write-Host "Failed:  $failed" -ForegroundColor Red
}
Write-Host ""
Write-Host "The Viewer's Browse/Gallery tabs will now show empty."
Write-Host "Development folder files (IndexedDB) are unaffected."
