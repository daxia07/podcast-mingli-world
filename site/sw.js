var CACHE_V = "podcast-app-v24-chapters";
var SHELL = [
  "/",
  "/style.css?v=24",
  "/app.js?v=24",
  "/js/vtt.js?v=24",
  "/js/chapters.js?v=24",
  "/js/player-ui.js?v=24",
  "/solutions.json",
  "/manifest.webmanifest"
];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(CACHE_V).then(function (c) {
      return c.addAll(SHELL).catch(function () {});
    }).then(function () {
      return self.skipWaiting();
    })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (ks) {
      return Promise.all(
        ks
          .filter(function (k) {
            return k !== CACHE_V;
          })
          .map(function (k) {
            return caches.delete(k);
          })
      );
    }).then(function () {
      return self.clients.claim();
    })
  );
});

self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") return;
  var url = new URL(e.request.url);

  // Audio is never touched by the service worker. Episode requests carry a
  // Range header and come back 206; caching partial responses would poison the
  // cache and break seeking. Let the browser handle it directly.
  if (url.pathname.endsWith(".mp3") || e.request.headers.get("range")) {
    return;
  }

  // Transcripts and chapters are immutable per episode and small — cache them
  // after the first fetch so a downloaded episode reads offline too.
  if (url.pathname.indexOf("/transcripts/") === 0 || url.pathname.indexOf("/chapters/") === 0) {
    e.respondWith(
      caches.match(e.request).then(function (hit) {
        if (hit) return hit;
        return fetch(e.request).then(function (resp) {
          if (resp && resp.ok) {
            var copy = resp.clone();
            caches.open(CACHE_V).then(function (c) { c.put(e.request, copy); });
          }
          return resp;
        });
      })
    );
    return;
  }

  // Always network-first for data and app code so new episodes and new builds
  // show up without waiting for a service-worker update.
  if (
    url.pathname === "/manifest.json" ||
    url.pathname === "/solutions.json" ||
    url.pathname.indexOf("/app.js") === 0 ||
    url.pathname.indexOf("/js/") === 0 ||
    url.pathname.indexOf("/style.css") === 0
  ) {
    e.respondWith(
      fetch(e.request).catch(function () {
        return caches.match(e.request);
      })
    );
    return;
  }

  e.respondWith(
    fetch(e.request)
      .then(function (resp) {
        return resp;
      })
      .catch(function () {
        return caches.match(e.request);
      })
  );
});
