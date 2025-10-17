// Minimal Service Worker for PWA Installation
// This service worker only handles installation and activation
// No caching is implemented as per requirements

const CACHE_NAME = 'django-ecommerce-v1';
const urlsToCache = [
  // Only cache essential files for installation
  '/',
  '/static/css/',
  '/static/js/',
  '/static/images/'
];

// Install event - minimal setup
self.addEventListener('install', function(event) {
  console.log('Service Worker: Install event');
  
  // Skip waiting to activate immediately
  self.skipWaiting();
  
  event.waitUntil(
    // Just resolve immediately - no caching
    Promise.resolve()
  );
});

// Activate event - cleanup old caches
self.addEventListener('activate', function(event) {
  console.log('Service Worker: Activate event');
  
  event.waitUntil(
    // Clean up old caches
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(function() {
      // Take control of all pages immediately
      return self.clients.claim();
    })
  );
});

// Fetch event - minimal handling
self.addEventListener('fetch', function(event) {
  // For PWA installation, we just let requests pass through
  // No caching or offline functionality implemented
  event.respondWith(
    fetch(event.request).catch(function() {
      // If fetch fails, just let it fail naturally
      // This ensures the app works normally without offline caching
      return new Response('Network error', { status: 408 });
    })
  );
});

// Handle background sync (if needed in future)
self.addEventListener('sync', function(event) {
  console.log('Service Worker: Background sync event');
  // No background sync implemented
});

// Handle push notifications (if needed in future)
self.addEventListener('push', function(event) {
  console.log('Service Worker: Push event');
  // No push notifications implemented
});

// Handle notification clicks (if needed in future)
self.addEventListener('notificationclick', function(event) {
  console.log('Service Worker: Notification click event');
  // No notification handling implemented
});

// Message handling for communication with main thread
self.addEventListener('message', function(event) {
  console.log('Service Worker: Message received:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
