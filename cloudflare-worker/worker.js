/**
 * Optional reVCDOS asset proxy for GitHub Pages.
 *
 * Routes:
 *   /vcsky/* -> https://cdn.dos.zone/vcsky/*
 *   /vcbr/*  -> https://br.cdn.dos.zone/vcsky/*
 *
 * Use this only if direct browser requests to the original CDNs fail because
 * of CORS/CORP restrictions. This proxy does not contain or store game files;
 * it forwards requests to the configured upstreams.
 */
const ROUTES = [
  { prefix: "/vcsky/", upstream: "https://cdn.dos.zone/vcsky/" },
  { prefix: "/vcbr/", upstream: "https://br.cdn.dos.zone/vcsky/" },
];

function corsHeaders(headers = new Headers()) {
  headers.set("Access-Control-Allow-Origin", "*");
  headers.set("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS");
  headers.set("Access-Control-Allow-Headers", "Range, Content-Type, Accept");
  headers.set("Access-Control-Expose-Headers", "Content-Length, Content-Range, Accept-Ranges, Content-Encoding");
  headers.set("Cross-Origin-Resource-Policy", "cross-origin");
  return headers;
}

export default {
  async fetch(request) {
    const incoming = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method not allowed", { status: 405, headers: corsHeaders() });
    }

    const route = ROUTES.find((entry) => incoming.pathname.startsWith(entry.prefix));
    if (!route) {
      return new Response("Use /vcsky/* or /vcbr/*", { status: 404, headers: corsHeaders() });
    }

    const suffix = incoming.pathname.slice(route.prefix.length);
    const target = new URL(suffix + incoming.search, route.upstream);

    const upstreamHeaders = new Headers();
    for (const name of ["range", "accept", "accept-encoding", "if-none-match", "if-modified-since"]) {
      const value = request.headers.get(name);
      if (value) upstreamHeaders.set(name, value);
    }

    const response = await fetch(target, {
      method: request.method,
      headers: upstreamHeaders,
      redirect: "follow",
    });

    const headers = corsHeaders(new Headers(response.headers));
    headers.delete("set-cookie");

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers,
    });
  },
};
