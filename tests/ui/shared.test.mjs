// DOM-free checks for dist/shared.js, loaded the way the browser loads a classic script.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const code = fs.readFileSync(new URL('../../dist/shared.js', import.meta.url), 'utf8');
const Shared = vm.runInNewContext(`${code}\n;Shared`, {URL});

test('safeURL accepts only https without credentials', () => {
  assert.equal(Shared.safeURL('https://ask.ifas.ufl.edu/publication/HS216'), 'https://ask.ifas.ufl.edu/publication/HS216');
  for (const value of ['http://example.org/', 'javascript:alert(1)', 'data:text/html,x', 'https://user:pw@example.org/',
    'https://user@example.org/', '//example.org/x', 'not a url', '', null, undefined, 42, {href: 'https://x.org'}]) {
    assert.equal(Shared.safeURL(value), null, String(value));
  }
});

test('escapeHTML escapes markup characters and tolerates non-strings', () => {
  assert.equal(Shared.escapeHTML(`<a href="x">'&'</a>`), '&lt;a href=&quot;x&quot;&gt;&#39;&amp;&#39;&lt;/a&gt;');
  assert.equal(Shared.escapeHTML(null), '');
  assert.equal(Shared.escapeHTML(15), '15');
});

test('cleanText removes control, zero-width and bidi characters', () => {
  assert.equal(Shared.cleanText('safe\u202Etxt.exe'), 'safetxt.exe');
  assert.equal(Shared.cleanText('a\u200Bb\u200Dc\uFEFFd\u2066e\u2069'), 'abcde');
  assert.equal(Shared.cleanText('bell\u0007 and del\u007F'), 'bell and del');
  assert.equal(Shared.cleanText('line one\nline two\t\tend'), 'line one line two end');
  assert.equal(Shared.cleanText('Ñuble · arándano 🫐 – 2026'), 'Ñuble · arándano 🫐 – 2026');
  assert.equal(Shared.cleanText(7), 7);
});

test('scanState gives cycle failure precedence over freeze exposure', () => {
  const favourable = new Set(['01-01']);
  const start = (extra = {}) => ({budbreak: '01-01', rankable: true, recurring_crop_loss: [], ...extra});
  assert.equal(Shared.scanState(start({recurring_crop_loss: ['bud_freeze', 'cycle_failure']}), favourable), 'failure');
  assert.equal(Shared.scanState(start({recurring_crop_loss: ['fruit_frost']}), favourable), 'loss');
  assert.equal(Shared.scanState(start({rankable: false}), favourable), 'unrankable');
  assert.equal(Shared.scanState(start(), favourable), 'favourable');
  assert.equal(Shared.scanState(start({budbreak: '02-01'}), favourable), 'other');
  assert.equal(Shared.scanState({budbreak: '01-01', rankable: true}, favourable), 'favourable');
});

test('scanOutcomes sums outcomes and is null for older payloads', () => {
  const o = (complete, slow, horizon, missing = 0) => ({outcomes: {complete, stalled_slow: slow, stalled_horizon: horizon, weather_incomplete: missing}});
  assert.deepEqual({...Shared.scanOutcomes([o(10, 2, 3), o(5, 0, 7, 1)])}, {complete: 15, stalled_slow: 2, stalled_horizon: 10, weather_incomplete: 1});
  assert.equal(Shared.scanOutcomes([o(1, 0, 0), {cycles: 3}]), null);
  assert.equal(Shared.scanOutcomes([]), null);
  assert.equal(Shared.scanOutcomes(undefined), null);
});
