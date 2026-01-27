const CACHE_NAME = 'uma-capture-v1';
const ASSETS = [
  '/capture/',
  '/capture/index.html',
  '/capture/manifest.json'
];

// Install - cache assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate - clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME)
            .map(key => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests (uploads should always go to network)
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request)
      .then(cached => cached || fetch(event.request))
      .catch(() => {
        // Offline fallback for navigation
        if (event.request.mode === 'navigate') {
          return caches.match('/capture/index.html');
        }
      })
  );
});

// Background sync for failed uploads (future enhancement)
self.addEventListener('sync', (event) => {
  if (event.tag === 'upload-retry') {
    event.waitUntil(retryFailedUploads());
  }
});

async function retryFailedUploads() {
  // TODO: Implement IndexedDB queue for failed uploads
  console.log('Retrying failed uploads...');
}
