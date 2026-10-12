// The regional evidence validator against the real library and hardened inputs.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const read = file => fs.readFileSync(new URL(`../../dist/${file}`, import.meta.url), 'utf8');
const context = vm.createContext({URL, window: {}, document: {baseURI: 'http://127.0.0.1:5173/'}, location: {origin: 'http://127.0.0.1:5173'}});
vm.runInContext(read('shared.js'), context);
vm.runInContext(read('evidence.js'), context);
const {validate} = context.window.RegionalEvidence;
const library = () => JSON.parse(read('evidence/ibo-regional-v1.json'));

test('every record in the shipped library validates', () => {
  const data = library();
  const result = validate(data);
  assert.equal(result.records.length, data.records.length);
  assert.ok(result.records.length >= 91, `expected at least 91 records, found ${result.records.length}`);
  // Clean text is unchanged by validation.
  assert.equal(JSON.stringify(result), JSON.stringify(data));
});

test('hidden characters are stripped from record text', () => {
  const data = library();
  const title = data.records[0].title;
  data.records[0].title = `\u202E${title}\u200B`;
  data.records[0].limitations = [...data.records[0].limitations, 'line\nbreak\u0000'];
  const result = validate(data);
  assert.equal(result.records[0].title, title);
  assert.equal(result.records[0].limitations.at(-1), 'line break');
});

test('text that is empty after cleaning is rejected', () => {
  const data = library();
  data.records[0].summary = '\u200B\u2066';
  assert.throws(() => validate(data), /records\[0\]\.summary/);
});

for (const [field, limit, set] of [
  ['title', 240, (r, v) => { r.title = v; }],
  ['summary', 1500, (r, v) => { r.summary = v; }],
  ['crop_context', 600, (r, v) => { r.crop_context = v; }],
  ['limitations', 600, (r, v) => { r.limitations = [v]; }],
  ['period', 200, (r, v) => { r.period.label = v; }],
  ['citations[0].locator', 300, (r, v) => { r.citations[0].locator = v; }],
]) {
  test(`${field} is limited to ${limit} characters`, () => {
    const ok = library();
    set(ok.records[0], 'é'.repeat(limit));
    assert.doesNotThrow(() => validate(ok));
    const long = library();
    set(long.records[0], 'é'.repeat(limit + 1));
    assert.throws(() => validate(long), new RegExp(`records\\[0\\]\\.${field.replace(/[[\].]/g, '\\$&')}`));
  });
}

test('unsafe source URLs are rejected', () => {
  const data = library();
  data.sources[0].url = 'javascript:alert(1)';
  assert.throws(() => validate(data), /sources\[0\]\.url/);
});
