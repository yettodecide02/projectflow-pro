// ProjectFlow Pro — Service Worker
// Provides offline support, caching, and background sync

const CACHE_NAME = 'projectflow-pro-v1';
const RUNTIME_CACHE = 'projectflow-runtime-v1';

// Assets to cache on install (App Shell)
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  'https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap',
];

// ── INSTALL ──────────────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[SW] Pre-caching app shell');
        // Cache what we can; ignore failures for external fonts
        return Promise.allSettled(
          PRECACHE_ASSETS.map(url => cache.add(url).catch(() => console.warn('[SW] Failed to cache:', url)))
        );
      })
      .then(() => self.skipWaiting())
  );
});

// ── ACTIVATE ─────────────────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames =>
      Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME && name !== RUNTIME_CACHE)
          .map(name => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      )
    ).then(() => self.clients.claim())
  );
});

// ── FETCH — Network-first for API, Cache-first for assets ─────
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET and chrome-extension requests
  if (request.method !== 'GET' || url.protocol === 'chrome-extension:') return;

  // For navigation requests (HTML pages) — Network first, fallback to cache
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then(response => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
          return response;
        })
        .catch(() => caches.match('/index.html'))
    );
    return;
  }

  // For Google Fonts — Cache first, then network
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    event.respondWith(
      caches.match(request).then(cached => {
        if (cached) return cached;
        return fetch(request).then(response => {
          const clone = response.clone();
          caches.open(RUNTIME_CACHE).then(cache => cache.put(request, clone));
          return response;
        }).catch(() => new Response('', { status: 408 }));
      })
    );
    return;
  }

  // For all other assets — Cache first, fallback network
  event.respondWith(
    caches.match(request).then(cached => {
      if (cached) return cached;
      return fetch(request).then(response => {
        if (!response || response.status !== 200 || response.type === 'opaque') return response;
        const clone = response.clone();
        caches.open(RUNTIME_CACHE).then(cache => cache.put(request, clone));
        return response;
      });
    })
  );
});

// ── BACKGROUND SYNC ──────────────────────────────────────────
self.addEventListener('sync', event => {
  if (event.tag === 'sync-tasks') {
    event.waitUntil(syncPendingData());
  }
});

async function syncPendingData() {
  // When connected to a real backend, push queued offline changes here
  console.log('[SW] Background sync triggered — sync pending task changes');
}

// ── PUSH NOTIFICATIONS ───────────────────────────────────────
self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || 'ProjectFlow Pro';
  const options = {
    body: data.body || 'You have a new notification',
    icon: '/icons/icon-192.png',
    badge: '/icons/icon-96.png',
    tag: data.tag || 'projectflow-notification',
    renotify: true,
    data: { url: data.url || '/' },
    actions: [
      { action: 'view', title: 'View' },
      { action: 'dismiss', title: 'Dismiss' },
    ],
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  if (event.action === 'dismiss') return;
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(clientList => {
      for (const client of clientList) {
        if (client.url === '/' && 'focus' in client) return client.focus();
      }
      if (clients.openWindow) return clients.openWindow(event.notification.data.url || '/');
    })
  );
});

// ── PERIODIC BACKGROUND SYNC ─────────────────────────────────
self.addEventListener('periodicsync', event => {
  if (event.tag === 'check-deadlines') {
    event.waitUntil(checkUpcomingDeadlines());
  }
});

async function checkUpcomingDeadlines() {
  console.log('[SW] Periodic sync: checking upcoming task deadlines');
  // In production: fetch tasks from API, compare due dates, fire notifications
}
