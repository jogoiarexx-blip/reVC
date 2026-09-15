/*
 * Minimal cross-origin-isolation service worker for static hosts such as
 * GitHub Pages. It makes the controlled page response carry COOP/COEP,
 * which replaces the headers normally added by reVCDOS' Python server.
 *
 * This file does not bypass CORS. Cross-origin game assets still need to be
 * served with suitable CORS/CORP headers, or through the optional proxy.
 */
(() => {
  if (typeof window === "undefined") {
    self.addEventListener("install", () => self.skipWaiting());
    self.addEventListener("activate", (event) => {
      event.waitUntil(self.clients.claim());
    });

    self.addEventListener("fetch", (event) => {
      if (event.request.cache === "only-if-cached" && event.request.mode !== "same-origin") {
        return;
      }

      event.respondWith((async () => {
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

  navigator.serviceWorker.register(scriptUrl).then((registration) => {
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
