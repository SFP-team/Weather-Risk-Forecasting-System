// Season ribbon and Every winter: season-frame dates, band counts, risk groups and published-calendar matching.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const read = file => fs.readFileSync(new URL(`../../dist/${file}`, import.meta.url), 'utf8');
const context = vm.createContext({URL});
vm.runInContext(read('shared.js'), context);
vm.runInContext(read('season-views.js'), context);
const {helpers} = vm.runInContext('SeasonViews', context);
// Values from the script's realm are copied into this realm before strict comparison.
const spans = list => Array.from(list, span => [...span]);
const north = {hemisphere: 'north'}, south = {hemisphere: 'south'};

test('published months and windows run forward across the new year in both hemispheres', () => {
  // Offsets count from 1 Nov (north) or 1 Apr (south); spans are half-open.
  assert.deepEqual(spans(helpers.monthSpans(south, [1, 12])), [[244, 306]]);
  assert.deepEqual(spans(helpers.monthSpans(north, [12, 1, 2])), [[30, 120]]);
  assert.deepEqual([...helpers.windowSpan(north, {start: '12-15', end: '02-15'})], [44, 107]);
  assert.equal(helpers.windowSpan(north, {start: 'December', end: '02-15'}), null);
});

test('published harvest months sit beside the model harvest even when they reach September in the north', () => {
  // A Michigan-like model harvest from 21 Jul to 27 Aug and a published July-to-September harvest: one span, not
  // September of the previous autumn.
  const p = {hemisphere: 'north', calendar: {harvest_start: {median: 262}, harvest_end: {median: 299}}};
  assert.deepEqual(spans(helpers.monthSpans(p, [7, 8, 9], helpers.centres(p).harvest)), [[242, 334]]);
});

test('the band accounts for every winter each day, with incomplete winters in their own layer', () => {
  const complete = {status: 'complete', offset_days: {chill: 10, budbreak: 20, flowering_start: 30, flowering_end: 40, harvest_start: 50, harvest_end: 60}};
  const p = {hemisphere: 'north', seasons: [complete, {status: 'chill_not_met', offset_days: {chill: null}}]};
  const {days} = helpers.bandCounts(p, 0, 70);
  assert.ok(days.every(day => Object.values(day).reduce((a, b) => a + b, 0) === 2));
  assert.ok(days.every(day => day.none === 1));
  const stageOf = day => Object.entries(days[day]).find(([layer, count]) => layer !== 'none' && count === 1)[0];
  assert.deepEqual([0, 10, 11, 20, 29, 30, 40, 41, 50, 60, 61].map(stageOf),
    ['chill', 'chill', 'warm', 'buds', 'buds', 'flower', 'flower', 'fruit', 'harvest', 'harvest', 'after']);
});

test('risk groups keep exposure-only measures out of both the counted and the unseen lists', () => {
  const p = {risks: {ranked: [{risk: 'harvest_heavy_rain'}], by_id: {
    fruit_frost: {risk: 'fruit_frost', years_with_event: 3, valid_years: 15},
    harvest_heavy_rain: {risk: 'harvest_heavy_rain', years_with_event: 15, valid_years: 15},
    bud_freeze: {risk: 'bud_freeze', years_with_event: 0, valid_years: 15},
    fruit_dry_spell: {risk: 'fruit_dry_spell', years_with_event: null, valid_years: 15},
    pollination_weather: {risk: 'pollination_weather', years_with_event: 0, valid_years: 0}}}};
  const groups = helpers.riskGroups(p);
  assert.deepEqual(Array.from(groups.shown, r => `${r.risk}:${r.ranked}`), ['harvest_heavy_rain:true', 'fruit_frost:false']);
  assert.deepEqual(Array.from(groups.unseen, r => r.risk), ['bud_freeze']);
  assert.deepEqual(Array.from(groups.exposureOnly, r => r.risk), ['fruit_dry_spell']);
});

test('a site uses its own benchmark calendar first, otherwise the nearest within 10 km', () => {
  const sites = [{id: 'a', lat: 31.54, lon: -82.46}, {id: 'b', lat: 31.60, lon: -82.46}];
  assert.equal(helpers.publishedCalendar(sites, {benchmark_id: 'b', lat: 31.54, lon: -82.46}).site.id, 'b');
  const near = helpers.publishedCalendar(sites, {lat: 31.55, lon: -82.46});
  assert.equal(near.site.id, 'a');
  assert.ok(near.km > 1.05 && near.km < 1.2, String(near.km));
  assert.equal(helpers.publishedCalendar(sites, {lat: 31.75, lon: -82.46}), null);
});

test('the published planting season takes precedence over benchmark planting months', () => {
  const official = {label: 'Mid-December to mid-February', window: {start: '12-15', end: '02-15'}};
  const published = {site: {planting_months: [12, 1, 2]}};
  const guide = helpers.plantingGuide(north, {published: official}, published);
  assert.deepEqual(spans(guide.spans), [[44, 107]]);
  assert.equal(guide.text, 'Guides: plant mid-December to mid-February');
  assert.deepEqual(spans(helpers.plantingGuide(north, {}, published).spans), [[30, 120]]);
  assert.equal(helpers.plantingGuide(north, {}, null), null);
});
