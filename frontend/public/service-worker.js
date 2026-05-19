/*
 * This is a fallback service worker file required for PWA support.
 * You can customize this later for offline functionality.
 */
 
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Cache hit - return response
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});
