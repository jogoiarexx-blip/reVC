// reVCDOS GitHub Pages configuration.
//
// The original Brotli CDN currently blocks browser requests from GitHub Pages
// because it does not return Access-Control-Allow-Origin. A CORS-enabled proxy
// can be supplied either below or temporarily with ?proxy=https://host.example.
// The proxy must expose /vcsky/ and /vcbr/ routes like cloudflare-worker/worker.js.
(() => {
  const params = new URLSearchParams(window.location.search);
  const proxy = (params.get("proxy") || localStorage.getItem("revcdos.proxy") || "").replace(/\/$/, "");

  if (params.get("proxy")) {
    localStorage.setItem("revcdos.proxy", proxy);
  }
  if (params.get("clear_proxy") === "1") {
    localStorage.removeItem("revcdos.proxy");
  }

  window.REVCDOS_PAGES_CONFIG = Object.freeze({
    vcskyBaseUrl: proxy ? `${proxy}/vcsky/` : "https://cdn.dos.zone/vcsky/",
    vcbrBaseUrl: proxy ? `${proxy}/vcbr/` : "https://br.cdn.dos.zone/vcsky/"
  });
})();
