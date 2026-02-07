/**
 * RainForge Service Worker
 * Enables offline functionality for field installers
 * 
 * Features:
 * - Offline page caching
 * - Background sync for verifications
 * - Push notifications
 * - Photo queue for low connectivity
 */

const CACHE_VERSION = 'rainforge-v4.0.0';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;
const IMAGE_CACHE = `${CACHE_VERSION}-images`;
const API_CACHE = `${CACHE_VERSION}-api`;

// Assets to cache immediately on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/offline.html',
  '/assets/index.css',
  '/assets/index.js',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
];

// API endpoints to cache
const CACHEABLE_API_PATTERNS = [
  /\/api\/v1\/public\//,
  /\/api\/v1\/marketplace\/installers/,
  /\/api\/v1\/config/,
];

// ==================== INSTALL ====================
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// ==================== ACTIVATE ====================
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');
  
  event.waitUntil(
    caches.keys()
      .then((keys) => {
        return Promise.all(
          keys
            .filter((key) => !key.startsWith(CACHE_VERSION))
            .map((key) => {
              console.log('[SW] Deleting old cache:', key);
              return caches.delete(key);
            })
        );
      })
      .then(() => self.clients.claim())
  );
});

// ==================== FETCH ====================
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests for caching
  if (request.method !== 'GET') {
    return;
  }
  
  // API requests - Network first, cache fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstWithCache(request, API_CACHE));
    return;
  }
  
  // Images - Cache first
  if (request.destination === 'image') {
    event.respondWith(cacheFirst(request, IMAGE_CACHE));
    return;
  }
  
  // Static assets - Cache first with network fallback
  event.respondWith(cacheFirstWithRefresh(request, STATIC_CACHE));
});

// ==================== CACHING STRATEGIES ====================

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) {
    return cached;
  }
  
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.log('[SW] Fetch failed:', error);
    return new Response('Offline', { status: 503 });
  }
}

async function cacheFirstWithRefresh(request, cacheName) {
  const cached = await caches.match(request);
  
  // Return cached response immediately if available
  const fetchPromise = fetch(request)
    .then((response) => {
      if (response.ok) {
        const cache = caches.open(cacheName);
        cache.then((c) => c.put(request, response.clone()));
      }
      return response;
    })
    .catch(() => null);
  
  return cached || fetchPromise || caches.match('/offline.html');
}

async function networkFirstWithCache(request, cacheName) {
  try {
    const response = await fetch(request);
    
    // Only cache successful GET requests for cacheable endpoints
    if (response.ok && isCacheableAPI(request.url)) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('[SW] Network failed, trying cache:', error);
    const cached = await caches.match(request);
    return cached || new Response(
      JSON.stringify({ error: 'Offline', cached: false }),
      { 
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

function isCacheableAPI(url) {
  return CACHEABLE_API_PATTERNS.some((pattern) => pattern.test(url));
}

// ==================== BACKGROUND SYNC ====================

self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync:', event.tag);
  
  if (event.tag === 'sync-verifications') {
    event.waitUntil(syncVerifications());
  }
  
  if (event.tag === 'sync-photos') {
    event.waitUntil(syncPhotos());
  }
});

async function syncVerifications() {
  console.log('[SW] Syncing queued verifications...');
  
  try {
    const db = await openDB();
    const verifications = await db.getAll('verification-queue');
    
    for (const verification of verifications) {
      try {
        const response = await fetch('/api/v1/verify/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(verification)
        });
        
        if (response.ok) {
          await db.delete('verification-queue', verification.id);
          console.log('[SW] Synced verification:', verification.id);
          
          // Notify user
          await notifyClient('sync-complete', {
            type: 'verification',
            id: verification.id
          });
        }
      } catch (error) {
        console.error('[SW] Failed to sync verification:', error);
      }
    }
  } catch (error) {
    console.error('[SW] Sync failed:', error);
  }
}

async function syncPhotos() {
  console.log('[SW] Syncing queued photos...');
  
  try {
    const db = await openDB();
    const photos = await db.getAll('photo-queue');
    
    for (const photo of photos) {
      try {
        const formData = new FormData();
        formData.append('file', photo.blob);
        formData.append('job_id', photo.job_id);
        formData.append('type', photo.type);
        
        const response = await fetch('/api/v1/upload/photo', {
          method: 'POST',
          body: formData
        });
        
        if (response.ok) {
          await db.delete('photo-queue', photo.id);
          console.log('[SW] Synced photo:', photo.id);
        }
      } catch (error) {
        console.error('[SW] Failed to sync photo:', error);
      }
    }
  } catch (error) {
    console.error('[SW] Photo sync failed:', error);
  }
}

// ==================== PUSH NOTIFICATIONS ====================

self.addEventListener('push', (event) => {
  console.log('[SW] Push received:', event);
  
  let data = { title: 'RainForge', body: 'New notification' };
  
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data.body = event.data.text();
    }
  }
  
  const options = {
    body: data.body,
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: data.data || {},
    actions: data.actions || [
      { action: 'open', title: 'Open' },
      { action: 'dismiss', title: 'Dismiss' }
    ],
    tag: data.tag || 'rainforge-notification',
    renotify: true,
    requireInteraction: data.priority === 'high'
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked:', event.action);
  
  event.notification.close();
  
  if (event.action === 'dismiss') {
    return;
  }
  
  const urlToOpen = event.notification.data?.url || '/';
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // Focus existing window if available
        for (const client of clientList) {
          if (client.url === urlToOpen && 'focus' in client) {
            return client.focus();
          }
        }
        // Open new window
        return clients.openWindow(urlToOpen);
      })
  );
});

// ==================== INDEXED DB HELPERS ====================

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('rainforge-offline', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(new DBWrapper(request.result));
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      
      if (!db.objectStoreNames.contains('verification-queue')) {
        db.createObjectStore('verification-queue', { keyPath: 'id', autoIncrement: true });
      }
      
      if (!db.objectStoreNames.contains('photo-queue')) {
        db.createObjectStore('photo-queue', { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

class DBWrapper {
  constructor(db) {
    this.db = db;
  }
  
  getAll(storeName) {
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction(storeName, 'readonly');
      const store = tx.objectStore(storeName);
      const request = store.getAll();
      
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }
  
  delete(storeName, key) {
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction(storeName, 'readwrite');
      const store = tx.objectStore(storeName);
      const request = store.delete(key);
      
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }
}

// ==================== CLIENT COMMUNICATION ====================

async function notifyClient(type, data) {
  const clients = await self.clients.matchAll({ type: 'window' });
  
  for (const client of clients) {
    client.postMessage({ type, data });
  }
}

// ==================== MESSAGE HANDLING ====================

self.addEventListener('message', (event) => {
  console.log('[SW] Message received:', event.data);
  
  if (event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data.type === 'CLEAR_CACHE') {
    caches.keys().then((keys) => {
      keys.forEach((key) => caches.delete(key));
    });
  }
});

console.log('[SW] Service worker loaded');
