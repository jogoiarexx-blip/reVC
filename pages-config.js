// reVCDOS GitHub Pages configuration.
//
// Direct CDN mode (default):
//   vcskyBaseUrl -> streamed game assets
//   vcbrBaseUrl  -> Brotli-compressed WASM/data package
//
// If the original CDN blocks cross-origin browser requests from GitHub Pages,
// deploy the optional Cloudflare Worker included in cloudflare-worker/ and use:
//   vcskyBaseUrl: "https://YOUR-WORKER.workers.dev/vcsky/"
//   vcbrBaseUrl:  "https://YOUR-WORKER.workers.dev/vcbr/"
window.REVCDOS_PAGES_CONFIG = Object.freeze({
  vcskyBaseUrl: "https://cdn.dos.zone/vcsky/",
  vcbrBaseUrl: "https://br.cdn.dos.zone/vcsky/"
});
