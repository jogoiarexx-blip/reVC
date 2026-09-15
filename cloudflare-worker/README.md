# Optional CORS proxy

Use this only if the browser console shows CORS/CORP errors when the GitHub Pages site accesses the DOS Zone CDNs directly.

## Cloudflare dashboard

1. Create a new Worker.
2. Replace its code with `worker.js` from this folder and deploy it.
3. Copy the Worker URL, for example `https://revcdos-assets-proxy.YOUR-SUBDOMAIN.workers.dev`.
4. In the repository root, edit `pages-config.js`:

```js
window.REVCDOS_PAGES_CONFIG = Object.freeze({
  vcskyBaseUrl: "https://revcdos-assets-proxy.YOUR-SUBDOMAIN.workers.dev/vcsky/",
  vcbrBaseUrl: "https://revcdos-assets-proxy.YOUR-SUBDOMAIN.workers.dev/vcbr/"
});
```

5. Commit the change. GitHub Actions will redeploy Pages automatically.

The Worker forwards requests to the same upstream URLs used by the original `server.py`; it does not bundle game assets.
