// reVCDOS GitHub Pages configuration.
//
// GitHub Pages is a static host. The original Brotli CDN may reject browser
// requests from this origin when it does not return Access-Control-Allow-Origin.
// When needed, provide an authorized HTTPS proxy exposing /vcsky/ and /vcbr/.
(() => {
  const params = new URLSearchParams(window.location.search);
  const storageKey = "revcdos.proxy";

  const normalizeProxy = (value) => {
    if (!value) return "";
    try {
      const url = new URL(value);
      if (url.protocol !== "https:" && url.protocol !== "http:") return "";
      return url.toString().replace(/\/$/, "");
    } catch {
      return "";
    }
  };

  // clear_proxy takes effect immediately on the current page load.
  if (params.get("clear_proxy") === "1") {
    localStorage.removeItem(storageKey);
  }

  const requestedProxy = normalizeProxy(params.get("proxy"));
  if (params.has("proxy")) {
    if (requestedProxy) localStorage.setItem(storageKey, requestedProxy);
    else localStorage.removeItem(storageKey);
  }

  const proxy = params.get("clear_proxy") === "1"
    ? ""
    : (requestedProxy || normalizeProxy(localStorage.getItem(storageKey)));

  const config = {
    proxyBaseUrl: proxy,
    vcskyBaseUrl: proxy ? `${proxy}/vcsky/` : "https://cdn.dos.zone/vcsky/",
    vcbrBaseUrl: proxy ? `${proxy}/vcbr/` : "https://br.cdn.dos.zone/vcsky/"
  };

  window.REVCDOS_PAGES_CONFIG = Object.freeze(config);

  if (proxy) {
    console.info("[reVCDOS Pages] Using configured asset proxy:", proxy);
  } else {
    console.info("[reVCDOS Pages] Using original asset hosts. If CORS blocks vcbr, configure an authorized proxy with ?proxy=https://YOUR-HOST");
  }
})();
