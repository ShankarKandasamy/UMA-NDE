/**
 * UMA Capture - Cloudflare Worker
 * 
 * Receives file uploads from PWA and stores them in R2 bucket
 * 
 * SETUP:
 * 1. Create a Cloudflare account (free tier works)
 * 2. Create an R2 bucket called 'uma-inspection-data' (or use existing)
 * 3. Create a Worker and paste this code
 * 4. Bind R2 bucket to worker with variable name 'BUCKET'
 * 5. Add environment variable 'API_KEY' with your secret key
 * 6. Deploy
 *
 * wrangler.toml example:
 *
 * name = "uma-capture-api"
 * main = "worker.js"
 * compatibility_date = "2024-01-01"
 *
 * [[r2_buckets]]
 * binding = "BUCKET"
 * bucket_name = "uma-inspection-data"
 *
 * [vars]
 * API_KEY = "your-secret-api-key-here"
 */

export default {
  async fetch(request, env, ctx) {
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, X-API-Key',
    };

    // Handle preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    // Validate API key for all requests
    const apiKey = request.headers.get('X-API-Key');
    if (!apiKey || apiKey !== env.API_KEY) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // Route: GET /list - List files and folders from R2
    if (request.method === 'GET' && path === '/list') {
      return handleList(request, env, corsHeaders);
    }

    // Route: GET /file/* - Get a specific file
    if (request.method === 'GET' && path.startsWith('/file/')) {
      return handleGetFile(request, env, corsHeaders);
    }

    // Route: POST /upload or POST / - Upload files
    if (request.method === 'POST') {
      return handleUpload(request, env, corsHeaders);
    }

    // Method not allowed
    return new Response(JSON.stringify({ error: 'Not found' }), {
      status: 404,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
};

/**
 * GET /list - List objects from R2 bucket
 * Query params:
 *   - prefix: Filter by path prefix (e.g., "2026-01-20/")
 *   - delimiter: Use "/" to get folder-like listing
 *   - cursor: Pagination cursor for large results
 *   - limit: Max items to return (default 100, max 1000)
 */
async function handleList(request, env, corsHeaders) {
  try {
    const url = new URL(request.url);
    const prefix = url.searchParams.get('prefix') || '';
    const delimiter = url.searchParams.get('delimiter') || '';
    const cursor = url.searchParams.get('cursor') || undefined;
    const limit = Math.min(parseInt(url.searchParams.get('limit') || '100'), 1000);

    const listOptions = { prefix, limit, cursor };
    if (delimiter) {
      listOptions.delimiter = delimiter;
    }

    const listed = await env.BUCKET.list(listOptions);

    // Process objects to include metadata
    const objects = listed.objects.map(obj => ({
      key: obj.key,
      size: obj.size,
      uploaded: obj.uploaded,
      httpMetadata: obj.httpMetadata,
      customMetadata: obj.customMetadata,
    }));

    // Get common prefixes (folders) when using delimiter
    const folders = listed.delimitedPrefixes || [];

    return new Response(JSON.stringify({
      objects,
      folders,
      truncated: listed.truncated,
      cursor: listed.truncated ? listed.cursor : null,
    }), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('List error:', error);
    return new Response(JSON.stringify({
      error: 'Failed to list files',
      details: error.message
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}

/**
 * GET /file/* - Retrieve a file from R2
 * Path: /file/{key} where key is the full R2 object path
 * Example: /file/2026-01-20/m5abc123/image.jpg
 */
async function handleGetFile(request, env, corsHeaders) {
  try {
    const url = new URL(request.url);
    // Extract file key from path (remove "/file/" prefix)
    const fileKey = decodeURIComponent(url.pathname.slice(6));

    if (!fileKey) {
      return new Response(JSON.stringify({ error: 'File path required' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    const object = await env.BUCKET.get(fileKey);

    if (!object) {
      return new Response(JSON.stringify({ error: 'File not found' }), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // Determine content type
    const contentType = object.httpMetadata?.contentType || 'application/octet-stream';

    // Get original filename for Content-Disposition
    const originalName = object.customMetadata?.originalName || fileKey.split('/').pop();

    const headers = {
      ...corsHeaders,
      'Content-Type': contentType,
      'Content-Length': object.size,
      'Cache-Control': 'public, max-age=31536000', // Cache for 1 year (immutable files)
      'Content-Disposition': `inline; filename="${originalName}"`,
    };

    // Include custom metadata in headers for client use
    if (object.customMetadata) {
      headers['X-Custom-Metadata'] = JSON.stringify(object.customMetadata);
    }

    return new Response(object.body, { headers });

  } catch (error) {
    console.error('Get file error:', error);
    return new Response(JSON.stringify({
      error: 'Failed to retrieve file',
      details: error.message
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}

/**
 * POST /upload - Handle file uploads
 */
async function handleUpload(request, env, corsHeaders) {
    try {
      const formData = await request.formData();
      const uploadedFiles = [];
      const timestamp = formData.get('timestamp') || new Date().toISOString();
      const notes = formData.get('notes') || '';
      const device = formData.get('device') || 'unknown';
      
      // Generate session ID for grouping files
      const sessionId = generateSessionId();
      const dateFolder = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
      
      // Process each file
      for (const [key, value] of formData.entries()) {
        if (key.startsWith('file_') && value instanceof File) {
          const file = value;
          const ext = file.name.split('.').pop().toLowerCase();
          const fileId = generateFileId();
          const storagePath = `${dateFolder}/${sessionId}/${fileId}.${ext}`;
          
          // Store file in R2
          await env.BUCKET.put(storagePath, file.stream(), {
            httpMetadata: {
              contentType: file.type || 'application/octet-stream',
            },
            customMetadata: {
              originalName: file.name,
              uploadTimestamp: timestamp,
              notes: notes,
              device: device,
              sessionId: sessionId,
            }
          });
          
          uploadedFiles.push({
            id: fileId,
            originalName: file.name,
            storagePath: storagePath,
            size: file.size,
            type: file.type,
          });
        }
      }
      
      // Create metadata file for the session
      const metadata = {
        sessionId,
        timestamp,
        notes,
        device,
        files: uploadedFiles,
        uploadedAt: new Date().toISOString(),
      };
      
      await env.BUCKET.put(
        `${dateFolder}/${sessionId}/_metadata.json`,
        JSON.stringify(metadata, null, 2),
        {
          httpMetadata: { contentType: 'application/json' }
        }
      );
      
      return new Response(JSON.stringify({
        success: true,
        sessionId,
        filesUploaded: uploadedFiles.length,
        files: uploadedFiles,
      }), {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
      
    } catch (error) {
      console.error('Upload error:', error);
      return new Response(JSON.stringify({ 
        error: 'Upload failed', 
        details: error.message 
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
}

function generateSessionId() {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 8);
  return `${timestamp}-${random}`;
}

function generateFileId() {
  return Math.random().toString(36).substring(2, 10);
}
