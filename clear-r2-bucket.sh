#!/bin/bash
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
# ============================================================

BUCKET_NAME="uma-inspection-data"

echo "=== R2 Bucket Cleanup: $BUCKET_NAME ==="
echo ""

# List all objects in the bucket
echo "Fetching object list..."
OBJECTS=$(wrangler r2 object list "$BUCKET_NAME" 2>/dev/null)

if [ $? -ne 0 ]; then
  echo "ERROR: Failed to list bucket objects."
  echo "Make sure wrangler is installed and you're logged in:"
  echo "  npm install -g wrangler"
  echo "  wrangler login"
  exit 1
fi

# Extract keys from JSON output
KEYS=$(echo "$OBJECTS" | node -e "
  let data = '';
  process.stdin.on('data', chunk => data += chunk);
  process.stdin.on('end', () => {
    try {
      const parsed = JSON.parse(data);
      const objects = parsed.objects || parsed || [];
      const arr = Array.isArray(objects) ? objects : [];
      arr.forEach(obj => {
        if (obj.key) console.log(obj.key);
      });
    } catch(e) {
      // Try line-by-line JSON parsing
      data.split('\n').forEach(line => {
        try {
          const obj = JSON.parse(line);
          if (obj.key) console.log(obj.key);
        } catch(e2) {}
      });
    }
  });
")

if [ -z "$KEYS" ]; then
  echo "Bucket is already empty. Nothing to delete."
  exit 0
fi

COUNT=$(echo "$KEYS" | wc -l | tr -d ' ')
echo "Found $COUNT object(s) in bucket."
echo ""

# Show first few objects as preview
echo "Sample objects:"
echo "$KEYS" | head -10
if [ "$COUNT" -gt 10 ]; then
  echo "  ... and $((COUNT - 10)) more"
fi
echo ""

# Confirm before deleting
read -p "Delete ALL $COUNT objects from $BUCKET_NAME? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Aborted."
  exit 0
fi

echo ""
echo "Deleting objects..."

DELETED=0
FAILED=0

while IFS= read -r key; do
  if [ -n "$key" ]; then
    wrangler r2 object delete "$BUCKET_NAME/$key" 2>/dev/null
    if [ $? -eq 0 ]; then
      DELETED=$((DELETED + 1))
      echo "  Deleted: $key"
    else
      FAILED=$((FAILED + 1))
      echo "  FAILED:  $key"
    fi
  fi
done <<< "$KEYS"

echo ""
echo "=== Done ==="
echo "Deleted: $DELETED"
if [ "$FAILED" -gt 0 ]; then
  echo "Failed:  $FAILED"
fi
echo ""
echo "The Viewer's Browse/Gallery tabs will now show empty."
echo "Development folder files (IndexedDB) are unaffected."
