/*
 * Minimal cross-origin-isolation service worker for static hosts such as
 * GitHub Pages. It adds COOP/COEP only to same-origin responses.
 *
 * Cross-origin game assets are intentionally NOT intercepted here. They must
 * already allow CORS/CORP themselves or be served through an authorized proxy.
 */
(() => {
  if (typeof window === "undefined") {
    self.addEventListener("install", () => self.skipWaiting());
    self.addEventListener("activate", (event) => {
      event.waitUntil(self.clients.claim());
    });

    self.addEventListener("fetch", (event) => {
      const requestUrl = new URL(event.request.url);

      // Let the browser handle third-party/CDN requests directly. Intercepting
      // them here does not bypass CORS and only creates an extra FetchEvent error.
      if (requestUrl.origin !== self.location.origin) {
        return;
      }

      if (event.request.cache === "only-if-cached" && event.request.mode !== "same-origin") {
        return;
      }

      event.respondWith((async () => {
        try {
          const response = await fetch(event.request);
          if (response.type === "opaque" || response.status === 0) {
            return response;
          }

          const headers = new Headers(response.headers);
          headers.set("Cross-Origin-Opener-Policy", "same-origin");
          headers.set("Cross-Origin-Embedder-Policy", "require-corp");

          return new Response(response.body, {
            status: response.status,
            statusText: response.statusText,
            headers
          });
        } catch (error) {
          console.error("Same-origin service worker fetch failed:", event.request.url, error);
          throw error;
        }
      })());
    });
    return;
  }

  if (!("serviceWorker" in navigator)) {
    console.warn("Service Worker is unavailable; cross-origin isolation may not work.");
    return;
  }

  const scriptUrl = document.currentScript && document.currentScript.src;
  if (!scriptUrl) return;

  navigator.serviceWorker.register(scriptUrl, { updateViaCache: "none" }).then((registration) => {
    registration.update().catch(() => {});

    if (!navigator.serviceWorker.controller) {
      const reloadedKey = "revcdos.coi.reloaded";
      if (sessionStorage.getItem(reloadedKey) !== "1") {
        sessionStorage.setItem(reloadedKey, "1");
        window.location.reload();
      }
      return;
    }

    sessionStorage.removeItem("revcdos.coi.reloaded");

    registration.addEventListener("updatefound", () => {
      const installing = registration.installing;
      if (!installing) return;
      installing.addEventListener("statechange", () => {
        if (installing.state === "activated") window.location.reload();
      });
    });
  }).catch((error) => {
    console.error("Failed to register COI service worker:", error);
  });
})();
