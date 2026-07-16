var CACHE_V = "podcast-app-v23-studio";
var SHELL = ["/", "/style.css?v=23", "/app.js?v=23", "/solutions.json", "/manifest.webmanifest"];

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
  // Always network for manifest + solutions + audio so new eps show up
  if (
    url.pathname === "/manifest.json" ||
    url.pathname === "/solutions.json" ||
    url.pathname.endsWith(".mp3") ||
    url.pathname.indexOf("/app.js") === 0 ||
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
