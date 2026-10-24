// Network first, saved copy when offline, so the app always opens.
const CACHE = 'tims-yields-v5';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'icons/logo.png', 'icons/icon-180.png', 'icons/icon-64.png',
  'https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  // skip the browser's 10-minute page cache for our own files so updates show on the next open
  const own = new URL(e.request.url).origin === self.location.origin;
  e.respondWith(
    (own ? fetch(e.request.url, { cache: 'no-cache' }) : fetch(e.request))
      .then((res) => {
        if (res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(e.request, copy)); }
        return res;
      })
      .catch(() => caches.match(e.request, { ignoreSearch: true }))
  );
});
