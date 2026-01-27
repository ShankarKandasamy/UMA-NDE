# UMA Capture - MVP Data Collection PWA

A minimal Progressive Web App for capturing NDT inspection data (photos, documents, notes) and uploading to cloud storage.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   PWA (Phone)   │────▶│ Cloudflare Worker│────▶│  Cloudflare R2  │
│                 │     │                 │     │                 │
│ • Camera        │     │ • Auth (API Key)│     │ • File Storage  │
│ • File Upload   │     │ • File Receive  │     │ • Organized by  │
│ • Notes         │     │ • Store to R2   │     │   date/session  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Files

- `index.html` - The PWA (single file, no build step)
- `manifest.json` - PWA manifest for "Add to Home Screen"
- `sw.js` - Service worker for offline support
- `worker.js` - Cloudflare Worker backend

## Deployment

### Step 1: Deploy the Backend (Cloudflare Worker + R2)

**Prerequisites:**
- Cloudflare account (free tier works)
- Node.js installed (for Wrangler CLI)

```bash
# Install Wrangler CLI
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Create R2 bucket
wrangler r2 bucket create uma-uploads

# Create project directory
mkdir uma-api && cd uma-api

# Create wrangler.toml
cat > wrangler.toml << 'EOF'
name = "uma-capture-api"
main = "worker.js"
compatibility_date = "2024-01-01"

[[r2_buckets]]
binding = "BUCKET"
bucket_name = "uma-uploads"
EOF

# Copy worker.js to this directory
cp ../worker.js .

# Set your API key (generate a random one)
wrangler secret put API_KEY
# Enter a strong random key when prompted, e.g.: uma_sk_a1b2c3d4e5f6g7h8

# Deploy
wrangler deploy
```

You'll get a URL like: `https://uma-capture-api.your-subdomain.workers.dev`

### Step 2: Deploy the PWA (Cloudflare Pages or any static host)

**Option A: Cloudflare Pages (Recommended)**

```bash
# From the uma-capture directory
wrangler pages project create uma-capture
wrangler pages deploy . --project-name=uma-capture
```

**Option B: GitHub Pages**

1. Create a GitHub repo
2. Push the files (index.html, manifest.json, sw.js)
3. Enable GitHub Pages in repo settings

**Option C: Any Static Host**

Just upload the 3 files (index.html, manifest.json, sw.js) to any web server.

### Step 3: Configure the PWA

1. Open the PWA URL on your phone
2. Triple-tap the "UMA_CAPTURE" logo (or long-press on mobile)
3. Enter your Worker URL and API key
4. Save settings

### Step 4: Install as App

**iOS:**
1. Open in Safari
2. Tap Share → "Add to Home Screen"

**Android:**
1. Open in Chrome
2. Tap menu → "Install app" or "Add to Home Screen"

## Usage

1. Open the app
2. Tap "Camera" to take a photo of:
   - Instrument screens (UT gauge readings)
   - Handwritten field notes
   - Document pages
   - Test setup
3. Or tap "Files" to upload CSV/Excel/PDF
4. Add optional notes (location, context)
5. Tap "Upload to UMA"

## File Organization in R2

Files are organized automatically:

```
uma-uploads/
├── 2026-01-20/
│   ├── m5abc123-x7y8z9/
│   │   ├── _metadata.json
│   │   ├── abc12345.jpg
│   │   ├── def67890.jpg
│   │   └── ghi11111.csv
│   └── m5def456-a1b2c3/
│       ├── _metadata.json
│       └── xyz99999.pdf
└── 2026-01-21/
    └── ...
```

Each upload session gets:
- Unique session ID
- Metadata file with notes, timestamp, device info
- All files grouped together

## Accessing Uploaded Files

**Via Cloudflare Dashboard:**
1. Go to R2 in Cloudflare dashboard
2. Browse the uma-uploads bucket

**Via API (add to worker.js for future):**
```javascript
// GET /list - List recent uploads
// GET /download/:path - Download specific file
```

**Via rclone (for bulk access):**
```bash
# Configure rclone with R2 credentials
rclone config
# Then sync to local
rclone sync r2:uma-uploads ./local-uploads
```

## Cost Estimate (Cloudflare Free Tier)

| Resource | Free Tier | Your MVP Usage |
|----------|-----------|----------------|
| Workers Requests | 100K/day | ~100/day |
| R2 Storage | 10 GB | < 1 GB initially |
| R2 Operations | 1M reads, 1M writes/month | ~1000/month |

**Total Cost: $0/month** for MVP scale

## Security Notes

- API key is stored in browser localStorage (acceptable for MVP)
- For production: consider device-based auth, token refresh
- R2 bucket is private by default (no public access)
- HTTPS enforced by Cloudflare

## Future Enhancements

1. **Offline queue** - Store uploads in IndexedDB when offline, sync when online
2. **Upload progress** - Real progress bar using XMLHttpRequest
3. **Compression** - Resize images before upload to save bandwidth
4. **OCR preview** - Show extracted text before upload
5. **Folder selection** - Let user pick project/job folder
6. **Webhook** - Trigger processing pipeline on upload

## Troubleshooting

**"Upload failed" error:**
- Check API endpoint and key in settings
- Verify Worker is deployed and accessible
- Check browser console for detailed error

**App not installing:**
- Must be served over HTTPS
- manifest.json must be valid
- Service worker must be at root

**Camera not working:**
- Grant camera permission when prompted
- iOS: Must use Safari for camera access
- Check HTTPS (camera requires secure context)
