// Year-round planner: start-relative month placement, median dates across the new year, market ranking, anomalies.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const read = file => fs.readFileSync(new URL(`../../dist/${file}`, import.meta.url), 'utf8');
const context = vm.createContext({URL});
vm.runInContext(read('shared.js'), context);
vm.runInContext(read('yearround.js'), context);
const {helpers} = vm.runInContext('YearRound', context);
const plain = value => JSON.parse(JSON.stringify(value));

test('months are placed forward from the start date and wrap into the next year', () => {
  assert.equal(helpers.monthOffset('06-15', 7), 16);    // 15 Jun to 1 Jul
  assert.equal(helpers.monthOffset('06-15', 6), 351);   // June comes round again next year
  assert.equal(helpers.monthOffset('03-01', 3), 0);
  assert.equal(helpers.dateAt('11-15', 60), '14 Jan');
});

test('median dates that pass 31 December stay after the start', () => {
  const o = plain(helpers.typicalOffsets('11-01', {flowering_start: '12-10', flowering_end: '01-05', harvest_start: '02-20', harvest_end: '03-30'}));
  assert.deepEqual(o, {flowering_start: 39, flowering_end: 65, harvest_start: 111, harvest_end: 149});
  assert.equal(helpers.typicalOffsets('11-01', {flowering_start: '12-10'}), null);
});

const year = (y, harvestStart) => ({year: y, outcome: 'complete', offset_days: {flowering_start: 10, flowering_end: 30, harvest_start: harvestStart, harvest_end: harvestStart + 30}});
const start = (budbreak, harvestStarts, extra = {}) => ({budbreak, rankable: true, recurring_crop_loss: [], recurring: [],
  years: harvestStarts.map((h, i) => year(2011 + i, h)), ...extra});

test('market ranking puts crop-loss-free starts first, then the share of years picking in the wanted months', () => {
  const mc = {favourable: {budbreak: ['01-01']}, starts: [
    start('01-01', [40, 40, 40]),                                        // first pick 10 Feb every year
    start('02-01', [40, 40, 40]),                                        // first pick 13 Mar every year
    start('03-01', [40, 40, 40], {recurring_crop_loss: ['flowering_freeze']}),  // 10 Apr, but recurring freeze
    start('04-01', [40, 40, 40], {rankable: false})]};                   // 11 May: outside the wanted months
  const ranked = helpers.plan(mc, [3, 4]).map(r => [r.start.budbreak, r.hits, r.n, r.usable]);
  assert.deepEqual(plain(ranked), [['02-01', 3, 3, true], ['01-01', 0, 3, true], ['03-01', 3, 3, false], ['04-01', 0, 3, false]]);
});

test('stalled and incomplete years do not count toward the market share', () => {
  const s = start('01-01', [40, 40]);
  s.years.push({year: 2013, outcome: 'stalled_slow'}, {year: 2014, outcome: 'weather_incomplete'});
  const [row] = helpers.plan({favourable: {budbreak: []}, starts: [s]}, [2]);
  assert.deepEqual([row.hits, row.n], [2, 2]);
});

test('warm flowering years need every chosen month and report El Nino months', () => {
  const monthly = [{year: 2015, month: 4, tmean: 22}, {year: 2015, month: 5, tmean: 21}, {year: 2016, month: 4, tmean: 20},
    {year: 2016, month: 5, tmean: 19}, {year: 2017, month: 4, tmean: 21}];
  const enso = {months: [{year: 2015, month: 4, phase: 'el_nino'}, {year: 2015, month: 5, phase: 'el_nino'}]};
  const rows = plain(helpers.warmFlowering(monthly, enso, [4, 5]));
  assert.deepEqual(rows.map(r => [r.year, r.elNino]), [[2015, 2], [2016, 0]]);
  assert.ok(Math.abs(rows[0].anomaly - 1) < 1e-9);
});
