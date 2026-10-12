// Preview proxy: static path safety, Host/Origin checks, API forwarding and security headers.
import {test, before, after} from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createServer, DIST} from '../../scripts/preview-ui.mjs';

const listen = server => new Promise(resolve => server.listen(0, '127.0.0.1', () => resolve(server.address().port)));
const close = server => new Promise(resolve => { server.closeAllConnections?.(); server.close(() => resolve()); });
function request(port, target, headers = {}, method = 'GET') {
  return new Promise((resolve, reject) => {
    const req = http.request({host: '127.0.0.1', port, path: target, method, agent: false, headers: {Host: `127.0.0.1:${port}`, ...headers}}, res => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', chunk => { body += chunk; });
      res.on('end', () => resolve({status: res.statusCode, headers: res.headers, body}));
      res.on('error', reject);
    });
    req.on('error', reject);
    req.end();
  });
}

let tmp, root, upstream, upstreamPort, seen, proxy, port, deadPort, deadProxy, deadProxyPort;
before(async () => {
  tmp = await fs.mkdtemp(path.join(os.tmpdir(), 'preview-ui-'));
  root = path.join(tmp, 'dist');
  await fs.mkdir(root);
  await fs.writeFile(path.join(root, 'index.html'), '<!doctype html><title>ok</title>');
  await fs.writeFile(path.join(root, 'benchmark.html'), '<!doctype html><style>b{}</style>');
  await fs.writeFile(path.join(tmp, 'secret.txt'), 'SECRET');
  seen = [];
  upstream = http.createServer((req, res) => {
    seen.push({url: req.url, headers: req.headers});
    if (req.url.startsWith('/api/slow')) return; // never answers
    if (req.url.startsWith('/api/partial')) {
      res.writeHead(200, {'Content-Type': 'application/json'});
      res.write('{"partial":');
      setTimeout(() => res.socket.destroy(), 20);
      return;
    }
    res.writeHead(200, {'Content-Type': 'application/json'});
    res.end(JSON.stringify({status: 'ready'}));
  });
  upstreamPort = await listen(upstream);
  proxy = createServer({root, upstreamPort, upstreamTimeoutMs: 200});
  port = await listen(proxy);
  // A port that refuses connections: bind, read the port, release it.
  const probe = http.createServer();
  deadPort = await listen(probe);
  await close(probe);
  deadProxy = createServer({root, upstreamPort: deadPort});
  deadProxyPort = await listen(deadProxy);
});
after(async () => {
  await Promise.all([close(proxy), close(deadProxy), close(upstream)]);
  await fs.rm(tmp, {recursive: true, force: true});
});

test('static root comes from the script location, not the working directory', () => {
  const expected = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', 'dist');
  assert.equal(DIST, expected);
});

test('serves files inside the root', async () => {
  const res = await request(port, '/');
  assert.equal(res.status, 200);
  assert.match(res.body, /<title>ok<\/title>/);
});

for (const target of ['/../secret.txt', '/%2e%2e/secret.txt', '/%2E%2E%2Fsecret.txt', '/..%2fsecret.txt', '/x/../../secret.txt', '/%00index.html']) {
  test(`refuses path traversal: ${target}`, async () => {
    const res = await request(port, target);
    assert.equal(res.status, 404);
    assert.doesNotMatch(res.body, /SECRET/);
  });
}

for (const target of ['/%E0%A4%A', '/%', '/%zz']) {
  test(`answers 400 for a malformed escape: ${target}`, async () => {
    const res = await request(port, target);
    assert.equal(res.status, 400);
  });
}

test('refuses a foreign Host header', async () => {
  assert.equal((await request(port, '/', {Host: 'evil.example'})).status, 403);
  assert.equal((await request(port, '/', {Host: `127.0.0.1:${port + 1}`})).status, 403);
  assert.equal((await request(port, '/', {Host: `localhost:${port}`})).status, 200);
});

test('refuses a foreign Origin and non-GET methods', async () => {
  assert.equal((await request(port, '/', {Origin: 'http://evil.example'})).status, 403);
  assert.equal((await request(port, '/', {}, 'POST')).status, 405);
});

test('refuses cross-site API requests before contacting upstream', async () => {
  const before = seen.length;
  for (const site of ['cross-site', 'same-site']) {
    const res = await request(port, '/api/health', {'Sec-Fetch-Site': site});
    assert.equal(res.status, 403);
    assert.deepEqual(JSON.parse(res.body), {error: 'Cross-site API request refused', code: 'forbidden_origin'});
  }
  assert.equal(seen.length, before);
  for (const site of ['same-origin', 'none']) assert.equal((await request(port, '/api/health', {'Sec-Fetch-Site': site})).status, 200);
});

test('forwards with the fixed upstream Host and drops Origin and cookies', async () => {
  const res = await request(port, '/api/health?x=1', {Origin: `http://127.0.0.1:${port}`, Cookie: 'session=abc', 'Sec-Fetch-Site': 'same-origin'});
  assert.equal(res.status, 200);
  assert.deepEqual(JSON.parse(res.body), {status: 'ready'});
  const forwarded = seen.at(-1);
  assert.equal(forwarded.url, '/api/health?x=1');
  assert.equal(forwarded.headers.host, '127.0.0.1:8787');
  assert.equal(forwarded.headers.origin, undefined);
  assert.equal(forwarded.headers.cookie, undefined);
  assert.equal(forwarded.headers['sec-fetch-site'], undefined);
});

test('answers 504 archive_timeout when upstream is too slow', async () => {
  const res = await request(port, '/api/slow');
  assert.equal(res.status, 504);
  assert.equal(JSON.parse(res.body).code, 'archive_timeout');
});

test('answers 503 archive_unavailable when the connection is refused', async () => {
  const res = await request(deadProxyPort, '/api/health');
  assert.equal(res.status, 503);
  assert.equal(JSON.parse(res.body).code, 'archive_unavailable');
});

test('only ends the response when upstream fails after headers were sent', async () => {
  const res = await request(port, '/api/partial');
  assert.equal(res.status, 200);
  assert.equal(res.body, '{"partial":');
});

test('sends nosniff, Referrer-Policy and a CSP that allows MapLibre', async () => {
  for (const target of ['/', '/missing.js', '/api/health']) {
    const res = await request(port, target);
    assert.equal(res.headers['x-content-type-options'], 'nosniff', target);
    assert.equal(res.headers['referrer-policy'], 'no-referrer', target);
    assert.ok(res.headers['content-security-policy'], target);
  }
  const csp = (await request(port, '/')).headers['content-security-policy'];
  for (const part of ["script-src 'self'", "worker-src 'self' blob:", "connect-src 'self' https://tiles.openfreemap.org",
    "img-src 'self' data: blob: https://tiles.openfreemap.org", "object-src 'none'", "base-uri 'none'", "frame-ancestors 'none'"]) {
    assert.ok(csp.split('; ').includes(part), part);
  }
  assert.ok(csp.split('; ').includes("style-src 'self'"));
  // The generated benchmark page keeps one inline <style> block.
  assert.match((await request(port, '/benchmark.html')).headers['content-security-policy'], /style-src 'self' 'unsafe-inline'/);
});
