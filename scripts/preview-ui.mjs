// Static UI server and fixed-destination proxy. Never accepts a target URL. Loopback-only unless configured.
// Run: node scripts/preview-ui.mjs   (PREVIEW_PORT overrides the default port 5173)
// Server deployment: PREVIEW_BIND=0.0.0.0 PREVIEW_HOSTS=fpt-server.ad.ufl.edu,10.248.22.167 lists the names users may reach it by.
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here = fileURLToPath(import.meta.url);
export const DIST = path.resolve(path.dirname(here), '..', 'dist');
// The Python API accepts only its own loopback Host, whatever port a test stub listens on.
const UPSTREAM_HOST_HEADER = '127.0.0.1:8787';
const MAP_HOST = 'https://tiles.openfreemap.org';
const types = {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.gz': 'application/gzip', '.png': 'image/png', '.svg': 'image/svg+xml', '.txt': 'text/plain; charset=utf-8'};
// MapLibre runs its worker from a blob URL and fetches tiles, glyphs and sprites from the OpenFreeMap host in
// dist/vendor/openfreemap-positron-en.json. Only benchmark.html keeps an inline <style> block.
const policy = inlineStyle => ["default-src 'self'", "script-src 'self'", "worker-src 'self' blob:", `connect-src 'self' ${MAP_HOST}`,
  `img-src 'self' data: blob: ${MAP_HOST}`, `style-src 'self'${inlineStyle ? " 'unsafe-inline'" : ''}`, "font-src 'self'",
  "object-src 'none'", "base-uri 'none'", "frame-ancestors 'none'", "form-action 'none'"].join('; ');
const CSP = policy(false), CSP_INLINE_STYLE = policy(true);
const json = (res, status, body) => {
  res.writeHead(status, {'Content-Type': 'application/json', 'Cache-Control': 'no-store'});
  res.end(JSON.stringify(body));
};

// Static root resolves from this file, so the working directory does not matter. Tests pass a short upstreamTimeoutMs.
export function createServer({root = DIST, upstreamPort = 8787, host = '127.0.0.1', upstreamTimeoutMs = 95000, hosts = []} = {}) {
  const base = path.resolve(root);
  return http.createServer(async (req, res) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('Referrer-Policy', 'no-referrer');
    res.setHeader('Content-Security-Policy', CSP);
    // Host and Origin must name this listener, so DNS rebinding and other sites cannot drive it. `hosts` adds names
    // beyond loopback, such as the server's DNS name.
    const port = req.socket.localPort;
    const names = ['127.0.0.1', 'localhost', ...hosts].map(name => `${name}:${port}`);
    if (!names.includes(req.headers.host)) { res.writeHead(403); return res.end('Forbidden host'); }
    if (req.method !== 'GET') { res.writeHead(405); return res.end(); }
    if (req.headers.origin && !names.map(name => `http://${name}`).includes(req.headers.origin)) { res.writeHead(403); return res.end(); }
    if (req.url.startsWith('/api/')) {
      const site = req.headers['sec-fetch-site'];
      if (site && site !== 'same-origin' && site !== 'none') return json(res, 403, {error: 'Cross-site API request refused', code: 'forbidden_origin'});
      // Only these headers go upstream: no Origin, cookies or client identity.
      let timedOut = false;
      const upstream = http.get({host, port: upstreamPort, path: req.url, timeout: upstreamTimeoutMs, agent: false,
        headers: {Host: UPSTREAM_HOST_HEADER, Accept: 'application/json'}}, response => {
        res.writeHead(response.statusCode, {'Content-Type': 'application/json', 'Cache-Control': 'no-store'});
        response.on('error', () => res.end());
        response.pipe(res);
      });
      upstream.on('timeout', () => { timedOut = true; upstream.destroy(); });
      // `code` separates a slow analysis and a missing archive connection from the archive's own 503 (another analysis is running).
      upstream.on('error', () => {
        if (res.headersSent) return res.end();
        if (timedOut) return json(res, 504, {error: 'The analysis took longer than the proxy limit; the server may still be working.', code: 'archive_timeout'});
        json(res, 503, {error: 'Private archive connection is unavailable', code: 'archive_unavailable'});
      });
      // A browser that gives up should not keep the upstream connection open.
      res.on('close', () => { if (!res.writableFinished) upstream.destroy(); });
      return;
    }
    let file;
    try {
      const pathname = req.url.split('?')[0];
      file = path.resolve(base, '.' + decodeURIComponent(pathname === '/' ? '/index.html' : pathname));
    } catch { res.writeHead(400); return res.end('Bad request'); }
    try {
      if (!file.startsWith(base + path.sep)) throw Error('outside root');
      const body = await fs.readFile(file);
      res.writeHead(200, {'Content-Type': types[path.extname(file)] ?? 'application/octet-stream', 'Cache-Control': 'no-store',
        ...(path.basename(file) === 'benchmark.html' ? {'Content-Security-Policy': CSP_INLINE_STYLE} : {})});
      res.end(body);
    } catch { res.writeHead(404); res.end('Not found'); }
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === here) {
  const port = Number(process.env.PREVIEW_PORT ?? 5173);
  const bind = process.env.PREVIEW_BIND ?? '127.0.0.1';
  const hosts = (process.env.PREVIEW_HOSTS ?? '').split(',').map(name => name.trim()).filter(Boolean);
  createServer({hosts}).listen(port, bind, () => console.log(`Listening on ${bind}:${port} for ${['127.0.0.1', 'localhost', ...hosts].join(', ')}`));
}
