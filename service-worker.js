const CACHE_NAME = "explora-maipo-v3-map";
const APP_SHELL = [
  "./",
  "index.html",
  "styles.css",
  "app.js",
  "manifest.webmanifest",
  "assets/icon.svg",
  "data/places.json",
  "data/routes.json",
  "visitor-guide.css",
  "visitor-guide.js",
  "territory-map.css",
  "territory-map.js",
  "assets/vendor/maplibre-gl.js",
  "assets/vendor/maplibre-gl.css",
  "data/map/localities.geojson",
  "data/map/boundary.geojson",
  "data/map/protected.geojson",
  "data/map/manifest.json"
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((key) => key.startsWith("explora-maipo-") && key !== CACHE_NAME).map((key) => caches.delete(key))))
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  // External map tiles use the browser's normal HTTP cache, never a PWA cache.
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;
  const shellUrls = APP_SHELL.map((path) => new URL(path, self.registration.scope).href);
  if (!shellUrls.includes(url.href) && event.request.mode !== "navigate") return;
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response.ok) {
          const clone = response.clone();
          event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone)));
        }
        return response;
      })
      .catch(async () => (await caches.match(event.request)) ||
        (event.request.mode === "navigate" ? await caches.match("index.html") : Response.error()))
  );
});
