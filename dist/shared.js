'use strict';

// Pure helpers shared by app.js, cycle.js, places.js and evidence.js. No DOM access, so Node tests can load this file.
const Shared = (() => {
  const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);

  // External links must be https without embedded credentials; anything else renders as plain text.
  const safeURL = value => {
    if (typeof value !== 'string') return null;
    try {
      const url = new URL(value);
      return url.protocol === 'https:' && !url.username && !url.password ? url.href : null;
    } catch {
      return null;
    }
  };

  // Control, zero-width and bidirectional formatting characters can hide or reorder text. Whitespace controls become a
  // space; the others are removed.
  const INVISIBLE = /[\u0000-\u0008\u000E-\u001F\u007F-\u009F\u00AD\u061C\u180E\u200B-\u200F\u202A-\u202E\u2060-\u2064\u2066-\u206F\uFEFF\uFFF9-\uFFFB]/g;
  const cleanText = value => typeof value === 'string' ? value.replace(/[\t\n\v\f\r]+/g, ' ').replace(INVISIBLE, '') : value;

  // Managed-cycle start state. Cycle failure takes precedence over freeze exposure; old payloads have no cycle_failure.
  const scanState = (start, favourable) => {
    const loss = start.recurring_crop_loss ?? [];
    if (loss.includes('cycle_failure')) return 'failure';
    if (loss.length) return 'loss';
    if (!start.rankable) return 'unrankable';
    return favourable.has(start.budbreak) ? 'favourable' : 'other';
  };

  // Sums per-start outcomes; null for payloads that predate the four-outcome accounting.
  const scanOutcomes = starts => {
    if (!starts?.length || !starts.every(start => start.outcomes)) return null;
    const total = { complete: 0, stalled_slow: 0, stalled_horizon: 0, weather_incomplete: 0 };
    for (const start of starts) for (const key of Object.keys(total)) total[key] += Number(start.outcomes[key]) || 0;
    return total;
  };

  // SHA-256 as lowercase hex. Browsers offer WebCrypto only on HTTPS and localhost pages, so a plain-HTTP address such
  // as the UF server deployment uses this FIPS 180-4 implementation instead. Both give the same digest.
  const K = new Uint32Array([
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
  ]);
  const rotr = (x, n) => (x >>> n) | (x << (32 - n));
  const sha256Script = bytes => {
    // Padding: one 0x80 byte, zeros, then the message length in bits as a 64-bit big-endian number.
    const blocks = new Uint8Array(Math.ceil((bytes.length + 9) / 64) * 64);
    blocks.set(bytes);
    blocks[bytes.length] = 0x80;
    const view = new DataView(blocks.buffer);
    view.setUint32(blocks.length - 8, Math.floor(bytes.length / 0x20000000));
    view.setUint32(blocks.length - 4, (bytes.length << 3) >>> 0);
    const h = new Uint32Array([0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]);
    const w = new Uint32Array(64);
    for (let offset = 0; offset < blocks.length; offset += 64) {
      for (let i = 0; i < 16; i++) w[i] = view.getUint32(offset + i * 4);
      // Uint32Array stores wrap modulo 2^32, which is the addition the standard specifies.
      for (let i = 16; i < 64; i++) {
        w[i] = w[i - 16] + (rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >>> 3)) + w[i - 7]
          + (rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >>> 10));
      }
      let [a, b, c, d, e, f, g, hh] = h;
      for (let i = 0; i < 64; i++) {
        const t1 = hh + (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + w[i];
        const t2 = (rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c));
        hh = g; g = f; f = e; e = (d + t1) >>> 0; d = c; c = b; b = a; a = (t1 + t2) >>> 0;
      }
      h[0] += a; h[1] += b; h[2] += c; h[3] += d; h[4] += e; h[5] += f; h[6] += g; h[7] += hh;
    }
    return Array.from(h, word => word.toString(16).padStart(8, '0')).join('');
  };
  const sha256Hex = async bytes => {
    if (!globalThis.crypto?.subtle) return sha256Script(bytes);
    const digest = new Uint8Array(await globalThis.crypto.subtle.digest('SHA-256', bytes));
    return Array.from(digest, byte => byte.toString(16).padStart(2, '0')).join('');
  };

  return Object.freeze({ escapeHTML, safeURL, cleanText, scanState, scanOutcomes, sha256Hex });
})();
