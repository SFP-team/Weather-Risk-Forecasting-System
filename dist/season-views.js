'use strict';

// Season ribbon and Every winter tabs. Presentation only: dates, winters and risk counts come from the production
// result; published months come from benchmark-calendars.json, built from the benchmark registry.
const SeasonViews = (() => {
  const DAY = 86400000;
  const NEAR_KM = 10;
  const KEYS = ['chill', 'budbreak', 'flowering_start', 'flowering_end', 'harvest_start', 'harvest_end'];
  const STAGES = ['chill', 'warm', 'buds', 'flower', 'fruit', 'harvest'];
  // Colours follow the bush: grey-blue dormant, green buds, pink flowers, green berries, blue ripe berries.
  const COLOR = {chill: '#a9b8c8', warm: '#d6ddcc', buds: '#a5ca80', flower: '#eaa6c1', fruit: '#5d9c61', harvest: '#3d4b9b',
    after: '#eeece6', planting: '#a37b55', risk: '#b8352a'};
  const NAME = {chill: 'Collecting chill', warm: 'Warming up', buds: 'Buds opening', flower: 'Flowering', fruit: 'Berries growing', harvest: 'Harvest'};
  const LINES = {chill: ['Collecting', 'chill'], warm: ['Warming', 'up'], buds: ['Buds', 'opening'], flower: ['Flowering'],
    fruit: ['Berries', 'growing'], harvest: ['Harvest']};
  const EVENT = {chill: 'Chill met', budbreak: 'Budbreak', flowering_start: 'Bloom starts', flowering_end: 'Bloom ends',
    harvest_start: 'Harvest starts', harvest_end: 'Harvest ends'};
  const GLYPH = {chill_shortfall: 'thermo', warm_midwinter: 'thermo', bud_freeze: 'frost', flowering_freeze: 'frost', fruit_frost: 'frost',
    pollination_weather: 'bee', flowering_dry_spell: 'dry', fruit_dry_spell: 'dry', fruit_severe_heat: 'sun', harvest_heavy_rain: 'rain',
    disease_weather: 'spore'};
  const STATUS = {chill_not_met: 'chill requirement not met', incomplete_stage_dates: 'weather incomplete after budbreak'};
  const esc = Shared.escapeHTML;
  const fin = value => typeof value === 'number' && Number.isFinite(value);
  const lowerFirst = text => text.charAt(0).toLowerCase() + text.slice(1);
  const textWidth = (text, size = 12) => String(text).length * size * 0.56;
  const rowOrder = new WeakMap();

  // Short names for the charts; each record's own label and definition stay in its tooltip.
  function riskName(record, assumptions) {
    const heat = fin(assumptions?.severe_heat_threshold_c) ? `Heat of ${assumptions.severe_heat_threshold_c} °C or more` : null;
    return ({chill_shortfall: 'Too little chill', warm_midwinter: 'Warm spells in winter', bud_freeze: 'Frost on opening buds',
      flowering_freeze: 'Freeze in bloom', fruit_frost: 'Frost on young fruit', pollination_weather: 'Poor bee weather',
      flowering_dry_spell: 'Dry spell in bloom', fruit_dry_spell: 'Dry spell on fruit', fruit_severe_heat: heat,
      harvest_heavy_rain: 'Heavy rain in harvest', disease_weather: 'Disease weather'})[record.risk] ?? record.label ?? record.risk;
  }

  // Offsets count days from 1 Nov (north) or 1 Apr (south) with 29 February not counted, so a non-leap year carries them.
  const anchor = p => p.hemisphere === 'south' ? Date.UTC(2001, 3, 1) : Date.UTC(2000, 10, 1);
  const dateOf = (p, offset) => new Date(anchor(p) + Math.round(offset) * DAY);
  const dateText = (p, offset) => fin(offset) ? dateOf(p, offset).toLocaleDateString('en-GB', {day: 'numeric', month: 'short', timeZone: 'UTC'}) : 'Unavailable';
  const monthName = (p, offset) => dateOf(p, offset).toLocaleDateString('en-GB', {month: 'short', timeZone: 'UTC'});

  // Published months and month-days fall on their occurrence within half a year of `centre`, the midpoint of the matching
  // model window, so a late northern harvest and a southern December-to-January harvest both land beside the model.
  // The default centre starts that year two months before the season start.
  const DEFAULT_CENTRE = 121;
  function monthDay(p, month, day = 1, centre = DEFAULT_CENTRE) {
    const from = anchor(p) + (centre - 182) * DAY, year = new Date(from).getUTCFullYear();
    let time = Date.UTC(year, month - 1, day);
    if (time < from) time = Date.UTC(year + 1, month - 1, day);
    return (time - anchor(p)) / DAY;
  }
  // Consecutive months merge into half-open [start, end) offset spans.
  function monthSpans(p, months = [], centre = DEFAULT_CENTRE) {
    const spans = [];
    for (const start of months.map(month => monthDay(p, month, 1, centre)).sort((a, b) => a - b)) {
      const d = dateOf(p, start), end = (Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 1) - anchor(p)) / DAY;
      const last = spans[spans.length - 1];
      if (last && start <= last[1]) last[1] = Math.max(last[1], end); else spans.push([start, end]);
    }
    return spans;
  }
  const spanText = (p, [start, end]) => monthName(p, start) === monthName(p, end - 1) ? monthName(p, start) : `${monthName(p, start)}–${monthName(p, end - 1)}`;
  // A published 'MM-DD' to 'MM-DD' planting window as a half-open offset span.
  function windowSpan(p, window, centre = DEFAULT_CENTRE) {
    const parse = text => typeof text === 'string' && /^\d{2}-\d{2}$/.test(text) ? text.split('-').map(Number) : null;
    const from = parse(window?.start), to = parse(window?.end);
    if (!from || !to) return null;
    const start = monthDay(p, from[0], from[1], centre);
    let end = monthDay(p, to[0], to[1], centre) + 1;
    if (end <= start) end += 365;
    return [start, end];
  }

  const isComplete = w => w.status === 'complete' && KEYS.every(key => fin(w.offset_days?.[key]));
  function stageOn(o, day) {
    if (day <= o.chill) return 'chill';
    if (day < o.budbreak) return 'warm';
    if (day < o.flowering_start) return 'buds';
    if (day <= o.flowering_end) return 'flower';
    if (day < o.harvest_start) return 'fruit';
    if (day <= o.harvest_end) return 'harvest';
    return 'after';
  }
  const stageSpans = o => [['chill', 0, o.chill], ['warm', o.chill + 1, o.budbreak - 1], ['buds', o.budbreak, o.flowering_start - 1],
    ['flower', o.flowering_start, o.flowering_end], ['fruit', o.flowering_end + 1, o.harvest_start - 1], ['harvest', o.harvest_start, o.harvest_end]]
    .filter(([, start, end]) => fin(start) && fin(end) && end >= start);
  const medians = p => Object.fromEntries(KEYS.map(key => [key, p.calendar?.[key]?.median]));
  // Midpoints of the model's own bloom, harvest and planting windows, used to place published months beside them.
  function centres(p) {
    const c = p.calendar ?? {}, mid = (a, b) => fin(a) && fin(b) ? (a + b) / 2 : null, budbreak = c.budbreak?.median;
    return {
      bloom: mid(c.flowering_start?.median, c.flowering_end?.median) ?? DEFAULT_CENTRE,
      harvest: mid(c.harvest_start?.median, c.harvest_end?.median) ?? DEFAULT_CENTRE,
      planting: mid(c.planting_start?.median, c.planting_end?.median) ?? (fin(budbreak) ? budbreak - 67 : DEFAULT_CENTRE),
    };
  }

  // For each day in [first, end), how many winters are in each layer. Winters without a complete calendar form the
  // 'none' layer, so the band always stands for every winter.
  function bandCounts(p, first, end) {
    const layers = [...STAGES, 'after', 'none'], days = [];
    for (let day = first; day < end; day++) {
      const count = Object.fromEntries(layers.map(layer => [layer, 0]));
      for (const w of p.seasons) count[isComplete(w) ? stageOn(w.offset_days, day) : 'none']++;
      days.push(count);
    }
    return {layers, days};
  }

  // Counted risks with at least one event, risks never seen, and exposure-only measures without an event definition.
  function riskGroups(p) {
    const ranked = new Set((p.risks?.ranked ?? []).map(r => r.risk)), records = Object.values(p.risks?.by_id ?? {});
    const counted = records.filter(r => fin(r.years_with_event) && fin(r.valid_years) && r.valid_years > 0);
    return {
      shown: counted.filter(r => r.years_with_event > 0).map(r => ({...r, ranked: ranked.has(r.risk)}))
        .sort((a, b) => b.years_with_event / b.valid_years - a.years_with_event / a.valid_years),
      unseen: counted.filter(r => r.years_with_event === 0),
      exposureOnly: records.filter(r => !fin(r.years_with_event)),
    };
  }

  function distanceKm(a, b) {
    const rad = degrees => degrees * Math.PI / 180, dLat = rad(b.lat - a.lat), dLon = rad(b.lon - a.lon);
    const h = Math.sin(dLat / 2) ** 2 + Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(dLon / 2) ** 2;
    return 2 * 6371 * Math.asin(Math.sqrt(h));
  }
  // The site's own benchmark entry, otherwise the nearest benchmark site within 10 km.
  function publishedCalendar(sites, site) {
    if (!Array.isArray(sites) || !site) return null;
    const own = site.benchmark_id ? sites.find(s => s.id === site.benchmark_id) : null;
    if (own) return {site: own, km: 0};
    let best = null;
    for (const s of sites) {
      if (!fin(s.lat) || !fin(s.lon) || !fin(site.lat) || !fin(site.lon)) continue;
      const km = distanceKm(site, s);
      if (km <= NEAR_KM && (!best || km < best.km)) best = {site: s, km};
    }
    return best;
  }
  // The app's published planting season comes first; otherwise the benchmark registry's planting months.
  function plantingGuide(p, planting, published, centre = DEFAULT_CENTRE) {
    const official = planting?.published, span = official ? windowSpan(p, official.window, centre) : null;
    if (span) return {spans: [span], text: `Guides: plant ${lowerFirst(official.label ?? spanText(p, span))}`, official};
    const spans = monthSpans(p, published?.site?.planting_months ?? [], centre);
    return spans.length ? {spans, text: `Guides: plant ${spans.map(s => spanText(p, s)).join(', ')}`, official: null} : null;
  }

  function axis(p, extra = []) {
    const winterEnd = p.hemisphere === 'south' ? 183 : 181;
    const lo = Math.min(0, ...extra.map(s => s[0]));
    const hi = Math.max(winterEnd, ...p.seasons.filter(isComplete).map(w => w.offset_days.harvest_end + 1), ...extra.map(s => s[1]));
    const first = dateOf(p, lo), last = dateOf(p, hi - 1);
    const start = Date.UTC(first.getUTCFullYear(), first.getUTCMonth(), 1), end = Date.UTC(last.getUTCFullYear(), last.getUTCMonth() + 1, 1);
    const months = [];
    for (let time = start; time < end;) {
      const d = new Date(time);
      months.push({offset: (time - anchor(p)) / DAY, label: d.toLocaleDateString('en-GB', {month: 'short', timeZone: 'UTC'})});
      time = Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 1);
    }
    return {d0: (start - anchor(p)) / DAY, d1: (end - anchor(p)) / DAY, months, winterEnd};
  }

  // Greedy rows for labels: items {x0, x1}; returns each item's row in input order.
  function pack(items, gap, maxRows) {
    const ends = [];
    return items.map(item => {
      let row = ends.findIndex(end => item.x0 > end + gap);
      if (row < 0) row = ends.length < maxRows ? ends.length : ends.indexOf(Math.min(...ends));
      ends[row] = item.x1;
      return row;
    });
  }
  // One row of boxes {want, w} in order, each as close to its wanted x as possible; null when they do not fit.
  function line(items, xMin, xMax, gap) {
    const pos = [];
    let cursor = xMin;
    for (const item of items) { const x0 = Math.max(item.want, cursor); pos.push(x0); cursor = x0 + item.w + gap; }
    for (let i = pos.length - 1; i >= 0; i--) pos[i] = Math.min(pos[i], (i === pos.length - 1 ? xMax : pos[i + 1] - gap) - items[i].w);
    return pos.length && pos[0] < xMin ? null : pos;
  }

  const note = (text, x, y, anchorText = 'start', size = 11.5, fill = '#707070', weight = 400) =>
    `<text x="${x}" y="${y}" font-size="${size}" font-weight="${weight}" fill="${fill}" text-anchor="${anchorText}">${esc(text)}</text>`;
  const halo = (text, x, y, anchorText = 'start', size = 11, fill = '#1d1d1f', weight = 600) =>
    `<text x="${x}" y="${y}" font-size="${size}" font-weight="${weight}" fill="${fill}" text-anchor="${anchorText}" stroke="#fff" stroke-width="3.5" stroke-linejoin="round" paint-order="stroke">${esc(text)}</text>`;
  const laneTitle = (text, y) => note(text, 12, y, 'start', 12.5, '#1d1d1f', 600);
  const grid = (ax, x, y0, y1, labelY) => ax.months.map(m => `<line x1="${x(m.offset)}" x2="${x(m.offset)}" y1="${y0}" y2="${y1}" stroke="#e6e8ec"/>` +
    note(m.label, x(m.offset) + 4, labelY, 'start', 12)).join('');
  function defs(prefix) {
    const hatch = (id, color) => `<pattern id="${prefix}-${id}" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">` +
      `<rect width="6" height="6" fill="#fff"/><line x1="0" y1="0" x2="0" y2="6" stroke="${color}" stroke-width="2.4"/></pattern>`;
    return `<defs>${hatch('plant', '#b8916b')}${hatch('flower', '#e391b2')}${hatch('harvest', '#7d88c8')}${hatch('none', '#c4c4c4')}</defs>`;
  }

  function glyph(kind, x, y, r = 7, color = COLOR.risk) {
    const rad = degrees => degrees * Math.PI / 180;
    switch (kind) {
      case 'frost': return `<g stroke="${color}" stroke-width="1.7" stroke-linecap="round">${[0, 60, 120].map(a =>
        `<line x1="${x - Math.cos(rad(a)) * r}" y1="${y - Math.sin(rad(a)) * r}" x2="${x + Math.cos(rad(a)) * r}" y2="${y + Math.sin(rad(a)) * r}"/>`).join('')}</g>`;
      case 'sun': return `<g stroke="${color}" stroke-width="1.5" stroke-linecap="round"><circle cx="${x}" cy="${y}" r="${r * 0.42}" fill="${color}"/>${[0, 45, 90, 135, 180, 225, 270, 315].map(a =>
        `<line x1="${x + Math.cos(rad(a)) * r * 0.68}" y1="${y + Math.sin(rad(a)) * r * 0.68}" x2="${x + Math.cos(rad(a)) * r}" y2="${y + Math.sin(rad(a)) * r}"/>`).join('')}</g>`;
      case 'rain': return `<path d="M${x},${y - r} C${x + r * 0.95},${y} ${x + r * 0.7},${y + r} ${x},${y + r} C${x - r * 0.7},${y + r} ${x - r * 0.95},${y} ${x},${y - r}Z" fill="${color}"/>`;
      case 'spore': return `<g fill="${color}"><circle cx="${x - r * 0.45}" cy="${y - r * 0.3}" r="${r * 0.34}"/><circle cx="${x + r * 0.48}" cy="${y - r * 0.1}" r="${r * 0.27}"/><circle cx="${x - r * 0.02}" cy="${y + r * 0.48}" r="${r * 0.38}"/></g>`;
      case 'bee': return `<g><ellipse cx="${x}" cy="${y}" rx="${r * 0.8}" ry="${r * 0.52}" fill="#e7b737" stroke="${color}" stroke-width="1"/>` +
        `<line x1="${x - r * 0.15}" y1="${y - r * 0.5}" x2="${x - r * 0.15}" y2="${y + r * 0.5}" stroke="${color}" stroke-width="1.5"/><line x1="${x + r * 0.28}" y1="${y - r * 0.46}" x2="${x + r * 0.28}" y2="${y + r * 0.46}" stroke="${color}" stroke-width="1.5"/></g>`;
      case 'dry': return `<path d="M${x - r},${y + r * 0.6} L${x - r * 0.3},${y - r * 0.25} L${x + r * 0.2},${y + r * 0.35} L${x + r},${y - r * 0.55}" stroke="${color}" stroke-width="1.7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
      default: return `<g stroke="${color}" stroke-width="1.7" fill="none"><line x1="${x}" y1="${y - r}" x2="${x}" y2="${y + r * 0.35}"/><circle cx="${x}" cy="${y + r * 0.62}" r="${r * 0.36}" fill="${color}"/></g>`;
    }
  }

  function plantIcon(stage, x, y) {
    const twig = `<line x1="${x - 9}" y1="${y + 9}" x2="${x + 9}" y2="${y + 9}" stroke="#7a6a58" stroke-width="2" stroke-linecap="round"/>`;
    switch (stage) {
      case 'chill': return `<g>${twig}<path d="M${x},${y - 8} C${x + 5},${y - 1} ${x + 5},${y + 6} ${x},${y + 8} C${x - 5},${y + 6} ${x - 5},${y - 1} ${x},${y - 8}Z" fill="#7f7264"/></g>`;
      case 'warm': return `<g>${twig}<path d="M${x},${y - 10} C${x + 7},${y - 1} ${x + 7},${y + 6} ${x},${y + 8} C${x - 7},${y + 6} ${x - 7},${y - 1} ${x},${y - 10}Z" fill="#9c8a70"/>` +
        `<path d="M${x},${y - 10} C${x + 3},${y - 6} ${x + 3},${y - 3} ${x},${y - 2} C${x - 3},${y - 3} ${x - 3},${y - 6} ${x},${y - 10}Z" fill="#8fbf68"/></g>`;
      case 'buds': return `<g>${twig}<path d="M${x},${y - 3} C${x + 4},${y + 1} ${x + 4},${y + 6} ${x},${y + 8} C${x - 4},${y + 6} ${x - 4},${y + 1} ${x},${y - 3}Z" fill="#8fbf68"/>` +
        `<path d="M${x},${y - 1} C${x - 9},${y - 4} ${x - 11},${y - 11} ${x - 4},${y - 11} C${x - 2},${y - 8} ${x - 1},${y - 4} ${x},${y - 1}Z" fill="#5e9e44"/>` +
        `<path d="M${x},${y - 1} C${x + 9},${y - 4} ${x + 11},${y - 11} ${x + 4},${y - 11} C${x + 2},${y - 8} ${x + 1},${y - 4} ${x},${y - 1}Z" fill="#5e9e44"/></g>`;
      case 'flower': return `<g><path d="M${x},${y - 11} L${x},${y - 6}" stroke="#5e9e44" stroke-width="1.6"/>` +
        `<path d="M${x - 6},${y - 6} C${x - 8},${y + 2} ${x - 5},${y + 8} ${x},${y + 8} C${x + 5},${y + 8} ${x + 8},${y + 2} ${x + 6},${y - 6}Z" fill="#fdf1f5" stroke="#d27c9f" stroke-width="1.3"/>` +
        `<path d="M${x - 4},${y + 8} l1.4,2 l1.3,-2 l1.3,2 l1.3,-2 l1.3,2" fill="none" stroke="#d27c9f" stroke-width="1"/></g>`;
      case 'fruit': return `<g fill="#7db56d" stroke="#4b8743" stroke-width="1"><circle cx="${x - 5}" cy="${y + 3}" r="5"/><circle cx="${x + 5}" cy="${y + 4}" r="5"/><circle cx="${x}" cy="${y - 4}" r="5"/></g>`;
      default: return `<g><g fill="#3d4b9b" stroke="#283271" stroke-width="1"><circle cx="${x - 5}" cy="${y + 3}" r="5.5"/><circle cx="${x + 5}" cy="${y + 4}" r="5.5"/><circle cx="${x}" cy="${y - 4}" r="5.5"/></g>` +
        `<g fill="#a7b0e6"><circle cx="${x - 5}" cy="${y + 3}" r="1.3"/><circle cx="${x + 5}" cy="${y + 4}" r="1.3"/><circle cx="${x}" cy="${y - 4}" r="1.3"/></g></g>`;
    }
  }

  function riskTitle(record) {
    return [record.label, record.event_definition, record.reason].filter(Boolean).join('. ');
  }
  function badge(record, p, x0, y, w, h) {
    const color = record.stage === 'whole' ? '#9aa2ad' : COLOR[record.stage] ?? '#9aa2ad', n = record.valid_years, k = record.years_with_event;
    const pitch = Math.min(8, 120 / n);
    const squares = Array.from({length: n}, (_, j) => `<rect x="${x0 + 30 + j * pitch}" y="${y + 27}" width="${pitch - 1.5}" height="${pitch - 1.5}" rx="1.2" fill="${j < k ? COLOR.risk : '#fff'}" stroke="${j < k ? COLOR.risk : '#c9ced6'}"/>`).join('');
    return `<g><title>${esc(riskTitle(record))}</title><rect x="${x0}" y="${y}" width="${w}" height="${h}" rx="8" fill="#fff" stroke="${record.ranked ? COLOR.risk : '#d6d6d6'}" stroke-width="${record.ranked ? 1.8 : 1}"/>` +
      `<rect x="${x0}" y="${y}" width="6" height="${h}" rx="3" fill="${color}"/>${glyph(GLYPH[record.risk] ?? 'thermo', x0 + 18, y + 16)}` +
      note(riskName(record, p.assumptions), x0 + 30, y + 20, 'start', 12.5, '#1d1d1f', 600) + squares +
      note(`${k} of ${n}`, x0 + 34 + n * pitch, y + 34, 'start', 11.5) +
      (record.ranked ? `<rect x="${x0 + w - 64}" y="${y - 8}" width="58" height="15" rx="7.5" fill="${COLOR.risk}"/>${note('TOP RISK', x0 + w - 35, y + 3, 'middle', 9.5, '#fff', 700)}` : '') + '</g>';
  }
  function stageCentre(medianOffsets, stage) {
    if (stage === 'whole') return (medianOffsets.flowering_start + medianOffsets.harvest_end) / 2;
    const span = stageSpans(medianOffsets).find(([key]) => key === stage);
    return span ? (span[1] + span[2] + 1) / 2 : null;
  }

  function ribbonSvg(p, ctx, published, guide) {
    const n = p.seasons.length, a = p.assumptions ?? {}, c = p.calendar ?? {}, med = medians(p);
    const rule = p.seasons.filter(isComplete).map(w => [w.offset_days.planting_start, w.offset_days.planting_end]).filter(([s, e]) => fin(s) && fin(e) && e >= s);
    const pub = published?.site ?? null, around = centres(p);
    const bloom = monthSpans(p, pub?.bloom_months ?? [], around.bloom), harvest = monthSpans(p, pub?.harvest_months ?? [], around.harvest);
    const ax = axis(p, [...rule.map(([s, e]) => [s, e + 1]), ...(guide?.spans ?? []), ...bloom, ...harvest]);
    const L = 150, R = 22, width = 1060, inner = width - L - R, x = d => L + (d - ax.d0) / (ax.d1 - ax.d0) * inner, hRib = 66;
    const front = [];
    // Stage names sit above the band, in tiers where neighbours would collide.
    const labels = stageSpans(med).map(([k, s, e]) => {
      const cx = (x(s) + x(e + 1)) / 2, w = Math.max(28, ...LINES[k].map(t => textWidth(t, 11.5))) + 8;
      return {k, cx, x0: cx - w / 2, x1: cx + w / 2};
    });
    const tiers = pack(labels, 4, 3), tierCount = labels.length ? Math.max(...tiers) + 1 : 0;
    let y = 24;
    // A left-aligned label's start, kept between the lane-title column and the right edge.
    const inside = (x0, text) => Math.max(L, Math.min(x0, width - 4 - textWidth(text, 11)));
    if (guide || rule.length) {
      front.push(laneTitle('Planting', y + 13), note(guide && rule.length ? 'guides / model rule' : guide ? 'guides' : 'model rule', 12, y + 26, 'start', 10.5));
      if (guide) {
        for (const [s, e] of guide.spans) front.push(`<rect x="${x(s)}" y="${y}" width="${x(e) - x(s)}" height="13" fill="url(#sv-ribbon-plant)" stroke="#b8916b"/>`);
        front.push(halo(guide.text, inside(x(guide.spans[0][0]) + 4, guide.text), y + 10, 'start', 11, '#6b4f33'));
      }
      const ry = guide ? y + 17 : y;
      if (rule.length) {
        const lo = Math.min(...rule.map(r => r[0])), hi = Math.max(...rule.map(r => r[1]));
        for (let d = lo; d <= hi; d++) {
          const k = rule.filter(([s, e]) => s <= d && d <= e).length;
          if (k) front.push(`<rect x="${x(d)}" y="${ry}" width="${x(d + 1) - x(d) + 0.4}" height="13" fill="${COLOR.planting}" fill-opacity="${Math.round((0.12 + 0.88 * k / n) * 100) / 100}"/>`);
        }
        const offsets = fin(a.planting_end_before_budbreak_days) && fin(a.planting_window_length_days)
          ? ` (${a.planting_end_before_budbreak_days + a.planting_window_length_days} to ${a.planting_end_before_budbreak_days} days before budbreak)` : '';
        const text = `Model rule: ${dateText(p, c.planting_start?.median)} to ${dateText(p, c.planting_end?.median)}${offsets}`;
        // Right of the shading, else left of it, else over its start; never into the lane-title column or past the edge.
        const tw = textWidth(text, 11), right = x(hi + 1) + 6, left = x(lo) - 6;
        front.push(right + tw < width - 4 ? halo(text, right, ry + 10, 'start', 11, '#6b4f33')
          : left - tw > L ? halo(text, left, ry + 10, 'end', 11, '#6b4f33') : halo(text, inside(x(lo) + 4, text), ry + 10, 'start', 11, '#6b4f33'));
      }
      // The lane keeps room for its title and caption even with one row.
      y = Math.max(ry + 23, y + 38);
    }
    if (bloom.length || harvest.length) {
      front.push(laneTitle('Growers report', y + 11));
      for (const [word, spans, id, stroke] of [['Bloom', bloom, 'flower', '#e391b2'], ['Harvest', harvest, 'harvest', '#7d88c8']]) {
        for (const span of spans) front.push(`<rect x="${x(span[0])}" y="${y}" width="${x(span[1]) - x(span[0])}" height="13" fill="url(#sv-ribbon-${id})" stroke="${stroke}"/>` +
          halo(`${word} ${spanText(p, span)}`, inside(x(span[0]) + 4, `${word} ${spanText(p, span)}`), y + 10));
      }
      y += 24;
    }
    const yRib = y + 8 + tierCount * 50, yB = yRib + hRib;
    // The bush band: on each day, the share of winters in each stage.
    const first = Math.max(0, ax.d0), {layers, days} = bandCounts(p, first, ax.d1);
    let cum = days.map(() => 0);
    for (const layer of layers) {
      const next = cum.map((v, i) => v + days[i][layer]);
      if (next.some((v, i) => v !== cum[i])) {
        const top = cum.map(v => yRib + v / n * hRib), bottom = next.map(v => yRib + v / n * hRib);
        let path = `M${x(first)},${top[0]}`;
        for (let i = 0; i < top.length; i++) { path += `H${x(first + i + 1)}`; if (i + 1 < top.length) path += `V${top[i + 1]}`; }
        path += `V${bottom[bottom.length - 1]}`;
        for (let i = bottom.length - 1; i >= 0; i--) { path += `H${x(first + i)}`; if (i > 0) path += `V${bottom[i - 1]}`; }
        front.push(`<path d="${path}Z" fill="${layer === 'none' ? 'url(#sv-ribbon-none)' : COLOR[layer]}"/>`);
      }
      cum = next;
    }
    front.push(`<rect x="${x(first)}" y="${yRib}" width="${x(ax.d1) - x(first)}" height="${hRib}" fill="none" stroke="#c8ccd2"/>`);
    if (ax.d0 < 0 && x(0) - x(ax.d0) > 70) front.push(note(`Before ${dateText(p, 0)}:`, (x(ax.d0) + x(0)) / 2, yRib + hRib / 2 - 3, 'middle', 11) +
      note('not modelled', (x(ax.d0) + x(0)) / 2, yRib + hRib / 2 + 11, 'middle', 11));
    front.push(laneTitle('What the bush', yRib + 26), laneTitle('is doing', yRib + 42), note(`${n} winters`, 12, yRib + 58, 'start', 10.5));
    labels.forEach((label, i) => {
      const top = yRib - 6 - (tiers[i] + 1) * 50, lines = LINES[label.k];
      front.push(plantIcon(label.k, label.cx, top + 13) + lines.map((t, j) => note(t, label.cx, top + 37 + j * 12, 'middle', 11.5, '#1d1d1f', 600)).join('') +
        `<line x1="${label.cx}" x2="${label.cx}" y1="${top + 30 + lines.length * 12}" y2="${yRib}" stroke="#8b929c"/>`);
    });
    // Risk markers sit on the stage they threaten; the badges below give the counts.
    const shown = riskGroups(p).shown.filter(r => fin(stageCentre(med, r.stage)));
    let previous = -Infinity;
    shown.map(r => ({r, cx: x(stageCentre(med, r.stage))})).sort((m1, m2) => m1.cx - m2.cx).forEach(mark => {
      const mx = Math.max(mark.cx, previous + 23), my = yB - 15;
      previous = mx;
      front.push(`<g><title>${esc(riskTitle(mark.r))}</title><circle cx="${mx}" cy="${my}" r="10" fill="#fff" stroke="${COLOR.risk}" stroke-width="1.4"/>${glyph(GLYPH[mark.r.risk] ?? 'thermo', mx, my, 6)}</g>`);
    });
    // Transition ticks: the middle winter's date and the range for the middle 80% of winters.
    const ticks = KEYS.filter(k => fin(c[k]?.median)).map(k => {
      const cx = x(c[k].median), t1 = `${EVENT[k]} ${dateText(p, c[k].median)}`, t2 = fin(c[k].p10) && fin(c[k].p90) ? `${dateText(p, c[k].p10)} to ${dateText(p, c[k].p90)}` : '';
      // The tick stays on the date; its label shifts inward when it would cross the drawing's edge.
      const w = Math.max(textWidth(t1, 12), textWidth(t2, 11)) + 6, lx = Math.min(Math.max(cx, L + w / 2), width - 4 - w / 2);
      return {cx, lx, t1, t2, x0: lx - w / 2, x1: lx + w / 2};
    });
    const tickRows = pack(ticks, 6, 3);
    // Leaders first, then haloed labels, so a leader from a lower row passes behind any label in its way.
    const tickY = i => yB + 24 + tickRows[i] * 32;
    ticks.forEach((t, i) => front.push(`<path d="M${t.cx - 4},${yB + 8} L${t.cx},${yB + 2} L${t.cx + 4},${yB + 8}Z" fill="#2b2f36"/>` +
      (tickRows[i] ? `<line x1="${t.cx}" x2="${t.cx}" y1="${yB + 8}" y2="${tickY(i) - 12}" stroke="#2b2f36" stroke-dasharray="2 2"/>` : '')));
    ticks.forEach((t, i) => front.push(halo(t.t1, t.lx, tickY(i), 'middle', 12) + (t.t2 ? halo(t.t2, t.lx, tickY(i) + 13, 'middle', 11, '#707070', 400) : '')));
    let bottom = yB + 24 + (ticks.length ? Math.max(...tickRows) + 1 : 0) * 32;
    if (shown.length) {
      const yRisk = bottom + 6, w = 200, h = 46, gap = 12;
      front.push(laneTitle('Weather risks', yRisk + 32), note('each square is a winter', 12, yRisk + 46, 'start', 10.5));
      const items = shown.map(r => ({r, w, want: x(stageCentre(med, r.stage)) - w / 2})).sort((i1, i2) => i1.want - i2.want);
      const rows = line(items, L, L + inner, gap) ? [items] : [items.filter((_, i) => i % 2 === 0), items.filter((_, i) => i % 2 === 1)];
      rows.forEach((list, row) => {
        const pos = line(list, L, L + inner, gap) ?? list.map((_, i) => L + i * (w + gap));
        list.forEach((item, i) => front.push(badge(item.r, p, pos[i], yRisk + 10 + row * (h + 16), w, h)));
      });
      bottom = yRisk + 10 + rows.length * (h + 16);
    }
    const back = grid(ax, x, 22, yB, 14);
    const summary = `Share of ${n} winters in each modelled stage from ${dateText(p, ax.d0)} to ${dateText(p, ax.d1 - 1)}, with ${shown.length} counted weather risks.`;
    return `<svg viewBox="0 0 ${width} ${bottom + 6}" role="img" aria-labelledby="sv-ribbon-title sv-ribbon-desc"><title id="sv-ribbon-title">Season ribbon</title>` +
      `<desc id="sv-ribbon-desc">${esc(summary)}</desc>${defs('sv-ribbon')}${back}${front.join('')}</svg>`;
  }

  function story(p, ctx) {
    const n = p.seasons.length, complete = p.seasons.filter(isComplete).length, med = medians(p), shown = riskGroups(p).shown;
    const req = p.assumptions?.chill_requirement_hours;
    const named = shown.slice(0, 2).map(r => `${lowerFirst(riskName(r, p.assumptions))} (${r.years_with_event} of ${r.valid_years} winters)`);
    const risks = named.length ? ` The most frequent weather risk is ${named[0]}${named[1] ? `, then ${named[1]}` : ''}.` : ' None of the counted weather risks occurred in these winters.';
    const missing = {};
    for (const w of p.seasons) if (!isComplete(w)) missing[w.status] = (missing[w.status] ?? 0) + 1;
    const coverage = complete < n ? ` ${complete} of ${n} winters give a complete calendar; ${Object.entries(missing).map(([status, count]) => `${count} with ${STATUS[status] ?? status.replace(/_/g, ' ')}`).join(', ')}.` : '';
    return `<p class="season-story"><strong data-season-name>${esc(ctx.name)}</strong>, typical winter: the ${esc(req)}-hour chill requirement is met by ${dateText(p, med.chill)}, ` +
      `buds break around ${dateText(p, med.budbreak)}, flowers are open from ${dateText(p, med.flowering_start)} to ${dateText(p, med.flowering_end)}, ` +
      `and harvest runs from ${dateText(p, med.harvest_start)} to ${dateText(p, med.harvest_end)}.${esc(risks)}${esc(coverage)}</p>`;
  }

  function setupNote(ctx) {
    return ctx.system && ctx.system !== 'open_ground'
      ? '<div class="soil-note season-setup">Evaluated for open field + ground. Growing setup changes qualitative notes only; no tunnel or pot adjustment is applied.</div>' : '';
  }

  function unavailable(p) {
    if (!p || p.status !== 'available') return `<div class="soil-note"><h3>No season to draw here</h3><p>${esc(p?.reason ?? 'Production analysis is not part of this result.')} Daily climate history remains usable.</p><button class="text-button" type="button" data-open-view="climate">View climate history →</button></div>`;
    const why = (p.chill_clock?.reasons ?? []).join(' ') || 'Evergreen or unclassified locations need a management-defined crop calendar.';
    return `<div class="soil-note"><h3>No chill-triggered season to draw here</h3><p>${esc(why)} The managed-cycle scan in Season &amp; exposures shows when cycles started on the 1st and 15th of each month would flower and fruit.</p><button class="text-button" type="button" data-open-view="season">View Season &amp; exposures →</button></div>`;
  }

  function sourceLinks(sources) {
    return sources.map(s => {
      const url = Shared.safeURL(s.url), title = esc(s.title ?? s.url ?? 'Source');
      return `<li>${url ? `<a href="${esc(url)}" target="_blank" rel="noreferrer">${title}</a>` : title}</li>`;
    }).join('');
  }

  function ribbonNotes(p, published, guide, calendars) {
    const groups = riskGroups(p), notes = [];
    if (calendars?.status === 'unavailable') notes.push('Published grower calendars could not load. Reload the page to try again; the model results are unchanged.');
    else if (calendars?.status === 'available' && !published) notes.push(`No published bloom or harvest months are recorded within ${NEAR_KM} km of this point. The literature benchmark covers 53 sites.`);
    if (published) notes.push(`Growers report: months published for ${published.site.name}${published.km >= 0.5 ? `, ${Math.round(published.km * 10) / 10} km from this point` : ''}, compiled for the literature benchmark from ${published.site.sources?.length ?? 0} sources.`);
    if (guide?.official) notes.push(`Planting guides: ${guide.official.label}${guide.official.region ? ` (${guide.official.region})` : ''}, the published season also shown in the planting panel.`);
    if (groups.unseen.length) notes.push(`Not seen in these winters: ${groups.unseen.map(r => lowerFirst(riskName(r, p.assumptions))).join(', ')}.`);
    if (groups.exposureOnly.length) notes.push(`Measured but without an event threshold, so not counted as risks: ${groups.exposureOnly.map(r => lowerFirst(riskName(r, p.assumptions))).join(', ')}. Their values are in Season & exposures.`);
    const gate = p.assumptions ?? {};
    const sources = [...(published?.site?.sources ?? []), ...(guide?.official?.sources ?? [])];
    return `<div class="season-notes">${notes.map(text => `<p>${esc(text)}</p>`).join('')}</div>
      <div class="season-links"><button class="text-button" type="button" data-open-view="season">Stage exposures and every assumption: Season &amp; exposures →</button><button class="text-button" type="button" data-open-view="evidence">Risk definitions: Methods &amp; data →</button><a class="text-button" href="benchmark.html" target="_blank" rel="noreferrer">Literature benchmark →</a></div>
      <details class="season-details"><summary>How to read the ribbon</summary><ul>
        <li>The band stands for all ${esc(p.seasons.length)} winters. On each date it is split by how many winters were in each stage: a colour that fills the band means the timing hardly changes, and a slanted edge shows how far that date moves between winters.</li>
        <li>Ticks below the band give the middle winter's date. The dates under each tick cover the middle 80% of winters (10th to 90th percentile).</li>
        <li>Grey hatching in the band marks winters without a complete calendar, for example when the chill requirement was not met.</li>
        <li>Planting: the model rule is shaded by how many winters each day falls inside it; hatched months come from extension guides. Growers report: hatched bloom and harvest months published for this area.</li>
        <li>Weather risks sit under the stage they threaten. Each square is one winter, filled when the event happened. A red border marks a top risk: it occurred in at least ${esc(Math.round((gate.risk_min_frequency ?? 0.5) * 100))}% of at least ${esc(gate.risk_min_valid_years ?? 12)} complete winters.</li>
        <li>All dates are modelled from gridded weather with provisional constants. They are not observed dates.</li>
      </ul></details>${sources.length ? `<details class="season-details"><summary>Sources for the published months</summary><ul class="season-sources">${sourceLinks(sources)}</ul></details>` : ''}`;
  }

  function ribbon(root, p, ctx) {
    if (!root) return;
    if (!ctx.applies) { root.innerHTML = unavailable(p); return; }
    const calendars = ctx.calendars ?? {status: 'loading'};
    const published = calendars.status === 'available' ? publishedCalendar(calendars.sites, ctx.site) : null;
    const guide = plantingGuide(p, ctx.planting, published, centres(p).planting);
    root.innerHTML = `<div class="season-panel">${setupNote(ctx)}${story(p, ctx)}<div class="season-scroll" tabindex="0" role="region" aria-label="Season ribbon. Scroll horizontally on narrow screens.">${ribbonSvg(p, ctx, published, guide)}</div>${ribbonNotes(p, published, guide, calendars)}</div>`;
  }

  const winterLabel = (p, year) => p.hemisphere === 'south' ? String(year) : `${year - 1}–${String(year).slice(2)}`;

  function wintersSvg(p, order) {
    const ax = axis(p), L = 120, chillW = 150, width = 1060, inner = width - L - chillW - 30, x = d => L + (d - ax.d0) / (ax.d1 - ax.d0) * inner;
    const a = p.assumptions ?? {}, req = a.chill_requirement_hours, rowH = 24, top = 92;
    const rows = [...p.seasons].sort(order === 'budbreak'
      ? (w1, w2) => (isComplete(w1) ? w1.offset_days.budbreak : Infinity) - (isComplete(w2) ? w2.offset_days.budbreak : Infinity) || w1.winter_year - w2.winter_year
      : (w1, w2) => w1.winter_year - w2.winter_year);
    const maxChill = Math.max(...p.seasons.map(w => w.chill_hours).filter(fin), fin(req) ? req : 0, 1);
    const cx0 = L + inner + 30, chillX = v => cx0 + v / maxChill * (chillW - 46);
    const out = [];
    // Legend: stage colours, then the event marks.
    let lx = 12;
    for (const k of STAGES) { out.push(`<rect x="${lx}" y="6" width="14" height="10" rx="2" fill="${COLOR[k]}"/>` + note(NAME[k], lx + 20, 15, 'start', 12, '#1d1d1f')); lx += textWidth(NAME[k]) + 40; }
    lx = 12;
    for (const [mark, text] of [[glyph('frost', 0, 0, 6, '#0f2a4a'), 'frost or freeze on that stage'], [glyph('sun', 0, 0, 6, '#c98a00'), `heat of ${fin(a.severe_heat_threshold_c) ? a.severe_heat_threshold_c : '35'} °C or more on fruit`],
      [glyph('rain', 0, 0, 5.5, '#3d4b9b'), 'heavy-rain days in harvest (number)'], [`<rect x="-7" y="-5" width="14" height="10" fill="url(#sv-winters-none)" stroke="#c4c4c4"/>`, 'no complete calendar']]) {
      out.push(`<g transform="translate(${lx + 6},${33})">${mark}</g>` + note(text, lx + 18, 37, 'start', 12, '#1d1d1f'));
      lx += textWidth(text) + 52;
    }
    out.push(grid(ax, x, top - 14, top + (rows.length + 1) * rowH + 6, top - 20));
    out.push(note('Chill hours', cx0, top - 34, 'start', 12) + (fin(req) ? note(`model needs ${req}`, cx0, top - 20, 'start', 11, COLOR.risk) : ''));
    if (fin(req)) out.push(`<line x1="${chillX(req)}" x2="${chillX(req)}" y1="${top - 10}" y2="${top + (rows.length + 1) * rowH}" stroke="${COLOR.risk}" stroke-dasharray="3 2"/>`);
    const mid = (o, stage) => { const span = stageSpans(o).find(([k]) => k === stage); return span ? (x(span[1]) + x(span[2] + 1)) / 2 : null; };
    const drawRow = (w, y, label, typical) => {
      const parts = [note(label, L - 10, y + 13, 'end', 12, '#1d1d1f', typical ? 700 : 400)], o = typical ? medians(p) : w.offset_days ?? {}, m = w?.metrics ?? {};
      const complete = typical || isComplete(w);
      const spans = stageSpans(o);
      if (complete) {
        for (const [k, s, e] of spans) parts.push(`<rect x="${x(s)}" y="${y + 4}" width="${Math.max(1, x(e + 1) - x(s))}" height="${typical ? 14 : 12}" fill="${COLOR[k]}"${typical ? ' stroke="#2b2f36" stroke-width="0.8"' : ''}/>`);
      } else if (w.status === 'chill_not_met') {
        parts.push(`<rect x="${x(0)}" y="${y + 4}" width="${x(ax.winterEnd) - x(0)}" height="12" fill="url(#sv-winters-none)" stroke="#c4c4c4"/>` +
          halo(`Chill requirement not met${fin(w.chill_hours) ? `: ${Math.round(w.chill_hours)} h` : ''}`, x(0) + 6, y + 14, 'start', 11, '#4a4a4a', 600));
      } else {
        for (const [k, s, e] of spans) parts.push(`<rect x="${x(s)}" y="${y + 4}" width="${Math.max(1, x(e + 1) - x(s))}" height="12" fill="${COLOR[k]}" fill-opacity="0.55"/>`);
        const end = spans.length ? x(spans[spans.length - 1][2] + 1) : x(0);
        parts.push(halo(STATUS[w.status] ? `${STATUS[w.status].charAt(0).toUpperCase()}${STATUS[w.status].slice(1)}` : 'Stage timing unavailable', end + 6, y + 14, 'start', 11, '#4a4a4a', 600));
      }
      if (complete && !typical) {
        if (m.bud_freeze_days > 0 && fin(mid(o, 'buds'))) parts.push(glyph('frost', mid(o, 'buds'), y + 10, 6, '#0f2a4a'));
        if (m.flower_freeze_days > 0 && fin(mid(o, 'flower'))) parts.push(glyph('frost', mid(o, 'flower'), y + 10, 6, '#0f2a4a'));
        if (m.fruit_frost_days > 0 && fin(mid(o, 'fruit'))) parts.push(glyph('frost', mid(o, 'fruit') - (m.fruit_severe_heat_days > 0 ? 8 : 0), y + 10, 6, '#ffffff'));
        if (m.fruit_severe_heat_days > 0 && fin(mid(o, 'fruit'))) parts.push(glyph('sun', mid(o, 'fruit') + 8, y + 10, 6, '#ffd166'));
        if (m.harvest_heavy_rain_days > 0 && fin(mid(o, 'harvest'))) parts.push(glyph('rain', mid(o, 'harvest') - 6, y + 10, 5.5, '#ffffff') + note(m.harvest_heavy_rain_days, mid(o, 'harvest') + 2, y + 14.5, 'start', 10.5, '#ffffff', 700));
      }
      const chill = typical ? p.chill_hours?.mean : w.chill_hours;
      if (fin(chill)) parts.push(`<rect x="${cx0}" y="${y + 5}" width="${chillX(chill) - cx0}" height="10" fill="${COLOR.chill}"/>` + note(Math.round(chill), chillX(chill) + 4, y + 14, 'start', 11, '#1d1d1f'));
      const detail = complete ? `chill met ${dateText(p, o.chill)}, budbreak ${dateText(p, o.budbreak)}, bloom ${dateText(p, o.flowering_start)} to ${dateText(p, o.flowering_end)}, harvest ${dateText(p, o.harvest_start)} to ${dateText(p, o.harvest_end)}`
        : STATUS[w.status] ?? 'stage timing unavailable';
      const events = typical ? '' : [['bud_freeze_days', 'frost days on buds'], ['flower_freeze_days', 'freeze days in bloom'], ['fruit_frost_days', 'frost days on young fruit'],
        ['fruit_severe_heat_days', 'heat days on fruit'], ['harvest_heavy_rain_days', 'heavy-rain days in harvest']].filter(([key]) => m[key] > 0).map(([key, text]) => `${m[key]} ${text}`).join(', ');
      return `<g><title>${esc(`${typical ? 'Typical winter (median dates)' : label}: ${detail}${events ? `; ${events}` : ''}`)}</title>${parts.join('')}</g>`;
    };
    rows.forEach((w, i) => out.push(drawRow(w, top + i * rowH, winterLabel(p, w.winter_year), false)));
    const yTypical = top + rows.length * rowH + 4;
    out.push(`<line x1="${L}" x2="${L + inner}" y1="${yTypical - 2}" y2="${yTypical - 2}" stroke="#2b2f36" stroke-width="0.8"/>`);
    out.push(drawRow(null, yTypical + 2, 'Typical', true));
    const height = yTypical + rowH + 12;
    return `<svg viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="sv-winters-title sv-winters-desc"><title id="sv-winters-title">Every winter</title>` +
      `<desc id="sv-winters-desc">${esc(`One row per winter, ${p.seasons.length} winters, with modelled stages, weather events by stage and total chill hours.`)}</desc>${defs('sv-winters')}${out.join('')}</svg>`;
  }

  function wintersNotes(p) {
    const a = p.assumptions ?? {};
    const thresholds = [fin(a.damaging_flower_freeze_c) ? `freeze in bloom ${a.damaging_flower_freeze_c} °C` : '', fin(a.frost_threshold_c) ? `frost on young fruit ${a.frost_threshold_c} °C` : '',
      fin(a.severe_heat_threshold_c) ? `heat ${a.severe_heat_threshold_c} °C` : '', fin(a.heavy_rain_mm) ? `heavy rain ${a.heavy_rain_mm} mm in a day` : ''].filter(Boolean).join(', ');
    return `<div class="season-notes"><p>Marks show that at least one frost, heat or heavy-rain day fell in that stage that winter, with the same thresholds as the risk counts: bud-stage freeze thresholds for buds${thresholds ? `, ${esc(thresholds)}` : ''}. The exact days are not part of the saved results.</p>` +
      `${p.hemisphere === 'south' ? '' : '<p>Northern rows are labelled by the two calendar years each season spans; the Season &amp; exposures tables list the second year.</p>'}` +
      `<p>The typical row joins the median date of each stage; it is not a real winter. Chill hours count from ${p.hemisphere === 'south' ? '1 April to 30 September' : '1 November to 30 April'}.</p></div>` +
      '<div class="season-links"><button class="text-button" type="button" data-open-view="season">Every exposure value by winter: Season &amp; exposures →</button></div>';
  }

  function drawWinters(root, p) {
    const order = rowOrder.get(root)?.order ?? 'year';
    root.innerHTML = `<div class="season-panel"><div class="season-controls" role="group" aria-label="Order the winters"><span>Order rows by</span>` +
      `<button type="button" data-winter-order="year" aria-pressed="${order === 'year'}">Winter</button><button type="button" data-winter-order="budbreak" aria-pressed="${order === 'budbreak'}">Budbreak date</button></div>` +
      `<div class="season-scroll" tabindex="0" role="region" aria-label="Every winter. Scroll horizontally on narrow screens.">${wintersSvg(p, order)}</div>${wintersNotes(p)}</div>`;
  }

  function winters(root, p, ctx) {
    if (!root) return;
    if (!ctx.applies) { root.innerHTML = unavailable(p); rowOrder.set(root, {p: null, order: rowOrder.get(root)?.order ?? 'year'}); return; }
    rowOrder.set(root, {p, order: rowOrder.get(root)?.order ?? 'year'});
    if (!root.dataset.seasonBound) {
      root.addEventListener('click', event => {
        const button = event.target.closest('[data-winter-order]'), state = rowOrder.get(root);
        if (!button || !state?.p) return;
        rowOrder.set(root, {...state, order: button.dataset.winterOrder});
        drawWinters(root, state.p);
        root.querySelector(`[data-winter-order="${button.dataset.winterOrder}"]`)?.focus();
      });
      root.dataset.seasonBound = 'true';
    }
    drawWinters(root, p);
  }

  async function loadCalendars(url = 'benchmark-calendars.json') {
    const response = await fetch(url, {credentials: 'same-origin'});
    if (!response.ok) throw Error('Published calendars could not load.');
    const data = await response.json();
    if (!Array.isArray(data?.sites)) throw Error('Published calendars have an unexpected format.');
    return data.sites;
  }

  return Object.freeze({ribbon, winters, loadCalendars,
    helpers: Object.freeze({monthDay, monthSpans, windowSpan, centres, bandCounts, riskGroups, publishedCalendar, plantingGuide, isComplete})});
})();
