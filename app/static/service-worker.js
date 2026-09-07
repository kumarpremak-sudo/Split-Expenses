const CACHE_NAME = 'splitexp-v2';
const STATIC_ASSETS = [
    '/',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/manifest.json',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png',
];

/* --- Install: Pre-cache static assets --- */
self.addEventListener('install', function (event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function (cache) {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

/* --- Activate: Clean old caches --- */
self.addEventListener('activate', function (event) {
    event.waitUntil(
        caches.keys().then(function (cacheNames) {
            return Promise.all(
                cacheNames
                    .filter(function (name) { return name !== CACHE_NAME; })
                    .map(function (name) { return caches.delete(name); })
            );
        })
    );
    self.clients.claim();
});

/* --- Fetch: Strategy per resource type --- */
self.addEventListener('fetch', function (event) {
    const url = new URL(event.request.url);

    // Dynamic routes & APIs: Bypass SW cache completely to enforce session security & fresh server validation
    if (url.pathname.startsWith('/group/') ||
        url.pathname.startsWith('/join') ||
        url.pathname.startsWith('/create') ||
        url.pathname.startsWith('/api/')) {
        return;
    }

    if (url.pathname.startsWith('/static/')) {
        event.respondWith(cacheFirst(event.request));
        return;
    }

    event.respondWith(networkFirst(event.request));
});

/**
 * Cache First: serve from cache, fall back to network.
 * Used for static assets (CSS, JS, fonts, images).
 */
function cacheFirst(request) {
    return caches.match(request).then(function (cachedResponse) {
        if (cachedResponse) {
            return cachedResponse;
        }
        return fetch(request).then(function (networkResponse) {
            return caches.open(CACHE_NAME).then(function (cache) {
                cache.put(request, networkResponse.clone());
                return networkResponse;
            });
        });
    });
}

/**
 * Network First: try network, fall back to cache.
 * Used for HTML pages to ensure fresh content.
 */
function networkFirst(request) {
    return fetch(request)
        .then(function (networkResponse) {
            return caches.open(CACHE_NAME).then(function (cache) {
                if (request.method === 'GET') {
                    cache.put(request, networkResponse.clone());
                }
                return networkResponse;
            });
        })
        .catch(function () {
            return caches.match(request).then(function (cachedResponse) {
                return cachedResponse || new Response('Offline', {
                    status: 503,
                    headers: { 'Content-Type': 'text/plain' },
                });
            });
        });
}
