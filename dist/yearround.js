'use strict';

// Year-round planner tab, for sites where a grower, not winter, starts the season (evergreen and tropical systems).
// Presentation only: start-date cycles come from production.managed_cycle, weekly hazards from hazard_calendar,
// monthly temperatures from the analysis, El Nino months from enso.json (NOAA ONI), grower months from
// benchmark-calendars.json.
const YearRound = (() => {
  const DAY = 86400000, REF = 2001;  // the server's median dates are leap-corrected, so a non-leap year places them
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const COLOR = {buds: '#a5ca80', flower: '#eaa6c1', fruit: '#5d9c61', harvest: '#3d4b9b', hazard: '#b8352a', grid: '#e4e2dc'};
  const NAME = {buds: 'Buds opening', flower: 'Flowering', fruit: 'Berries growing', harvest: 'Harvest'};
  const OUTCOME = {stalled_slow: 'Stalled: too slow', stalled_horizon: 'Stalled: heat never reached', weather_incomplete: 'Weather incomplete'};
  const LOSS = {bud_freeze: 'frost on buds', flowering_freeze: 'freeze in bloom', fruit_frost: 'frost on young fruit', cycle_failure: 'cycle stalls'};
  const OTHER = {fruit_severe_heat: 'heat on fruit', harvest_heavy_rain: 'heavy rain in harvest', disease_weather: 'disease weather', pollination_weather: 'poor bee weather'};
  const esc = Shared.escapeHTML;
  const fin = v => typeof v === 'number' && Number.isFinite(v);
  const state = new WeakMap();

  const parse = md => { const [m, d] = String(md).split('-').map(Number); return new Date(Date.UTC(REF, m - 1, d)); };
  // Days from a MM-DD start to the next 1st of `month` (the start's own month counts when the start is the 1st).
  function monthOffset(start, month) {
    const s = parse(start), first = Date.UTC(REF, month - 1, 1);
    return ((first - s) / DAY + 365) % 365;
  }
  function dateAt(start, offset) {
    const d = new Date(parse(start).getTime() + offset * DAY);
    return `${d.getUTCDate()} ${MONTHS[d.getUTCMonth()]}`;
  }
  const monthOf = (start, offset) => new Date(parse(start).getTime() + offset * DAY).getUTCMonth() + 1;
  const startLabel = md => dateAt(md, 0);
  const offsetOf = (start, md) => md ? ((parse(md) - parse(start)) / DAY + 365) % 365 : null;

  // Stage spans as [stage, first, last] day offsets (inclusive) from budbreak at 0.
  function spans(o) {
    if (![o?.flowering_start, o?.flowering_end, o?.harvest_start, o?.harvest_end].every(fin)) return [];
    return [['buds', 0, o.flowering_start - 1], ['flower', o.flowering_start, o.flowering_end],
      ['fruit', o.flowering_end + 1, o.harvest_start - 1], ['harvest', o.harvest_start, o.harvest_end]].filter(([, a, b]) => b >= a);
  }
  function typicalOffsets(start, dates) {
    const keys = ['flowering_start', 'flowering_end', 'harvest_start', 'harvest_end'];
    if (!keys.every(k => dates?.[k])) return null;
    const o = Object.fromEntries(keys.map(k => [k, offsetOf(start, dates[k])]));
    // A median date that wraps past the start belongs to the next year.
    let last = 0;
    for (const k of keys) { while (o[k] < last) o[k] += 365; last = o[k]; }
    return o;
  }

  function defaultStart(mc) {
    return mc.favourable?.budbreak?.[0] ?? mc.starts.find(s => s.rankable)?.budbreak ?? mc.starts[0]?.budbreak;
  }

  // Rank starts for a set of target harvest months: crop-loss-free and rankable first, then the share of complete
  // years whose first pick falls in a target month, then fewer recurring weather families.
  function plan(mc, targets) {
    const wanted = new Set(targets);
    const rows = mc.starts.map(s => {
      const done = (s.years ?? []).filter(y => y.outcome === 'complete' && fin(y.offset_days?.harvest_start));
      const hits = done.filter(y => wanted.has(monthOf(s.budbreak, y.offset_days.harvest_start))).length;
      return {start: s, hits, n: done.length, share: done.length ? hits / done.length : null,
        favourable: (mc.favourable?.budbreak ?? []).includes(s.budbreak),
        usable: s.rankable && !s.recurring_crop_loss.length};
    });
    return rows.sort((a, b) => (b.usable - a.usable) || ((b.share ?? -1) - (a.share ?? -1)) ||
      (a.start.recurring.length - b.start.recurring.length) || (b.favourable - a.favourable));
  }

  // Monthly mean-temperature anomaly against the same month over all years with data.
  function anomalies(monthly) {
    const byMonth = {};
    for (const r of monthly ?? []) if (fin(r.tmean)) (byMonth[r.month] ??= []).push(r.tmean);
    const mean = Object.fromEntries(Object.entries(byMonth).map(([m, v]) => [m, v.reduce((a, b) => a + b, 0) / v.length]));
    return (monthly ?? []).filter(r => fin(r.tmean)).map(r => ({year: r.year, month: r.month, anomaly: r.tmean - mean[r.month]}));
  }

  const note = (text, x, y, anchor = 'start', size = 12, fill = '#4a4a4a', weight = 400) =>
    `<text x="${x}" y="${y}" text-anchor="${anchor}" font-size="${size}" font-weight="${weight}" fill="${fill}">${esc(text)}</text>`;
  const hatch = id => `<defs><pattern id="${id}" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="#f3f2ee"/><line x1="0" y1="0" x2="0" y2="6" stroke="#c4c4c4" stroke-width="2"/></pattern></defs>`;

  function startSvg(mc, start, published) {
    const s = mc.starts.find(x => x.budbreak === start), years = s.years ?? [];
    const L = 120, width = 1060, inner = width - L - 20, span = 365, x = d => L + d / span * inner;
    const top = published ? 108 : 64, rowH = 24, out = [];
    let lx = 12;
    for (const k of Object.keys(NAME)) { out.push(`<rect x="${lx}" y="6" width="14" height="10" rx="2" fill="${COLOR[k]}"/>` + note(NAME[k], lx + 20, 15, 'start', 12, '#1d1d1f')); lx += NAME[k].length * 7 + 40; }
    out.push(note('✱ frost or freeze in that stage   ☀ severe heat on fruit   ● heavy-rain days in harvest (number)', 12, 36, 'start', 12, '#1d1d1f'));
    const bottom = top + (years.length + 1) * rowH + 6;
    for (let m = 1; m <= 12; m++) {
      const d = monthOffset(start, m);
      out.push(`<line x1="${x(d)}" x2="${x(d)}" y1="${top - 14}" y2="${bottom}" stroke="${COLOR.grid}"/>` + note(MONTHS[m - 1], x(d) + 4, top - 18, 'start', 11));
    }
    if (published) {
      const band = (months, y, fill, label) => {
        out.push(note(label, L - 10, y + 9, 'end', 11, '#1d1d1f'));
        for (const m of months) { const d = monthOffset(start, m), e = Math.min(span, d + new Date(Date.UTC(REF, m, 0)).getUTCDate()); out.push(`<rect x="${x(d)}" y="${y}" width="${x(e) - x(d)}" height="10" fill="${fill}" fill-opacity="0.75"/>`); }
      };
      band(published.bloom_months ?? [], top - 60, COLOR.flower, 'Growers: bloom');
      band(published.harvest_months ?? [], top - 44, COLOR.harvest, 'Growers: harvest');
    }
    const row = (o, y, label, outcome, marks, typical) => {
      const parts = [note(label, L - 10, y + 13, 'end', 12, '#1d1d1f', typical ? 700 : 400)], sp = spans(o);
      if (outcome && outcome !== 'complete') {
        parts.push(`<rect x="${x(0)}" y="${y + 4}" width="${x(150) - x(0)}" height="12" fill="url(#yr-none)" stroke="#c4c4c4"/>` + note(OUTCOME[outcome] ?? outcome, x(0) + 6, y + 14, 'start', 11, '#4a4a4a', 600));
        return `<g><title>${esc(`${label}: ${OUTCOME[outcome] ?? outcome}`)}</title>${parts.join('')}</g>`;
      }
      for (const [k, a, b] of sp) parts.push(`<rect x="${x(Math.min(a, span))}" y="${y + 4}" width="${Math.max(1, x(Math.min(b + 1, span)) - x(Math.min(a, span)))}" height="${typical ? 14 : 12}" fill="${COLOR[k]}"${typical ? ' stroke="#2b2f36" stroke-width="0.8"' : ''}/>`);
      const mid = k => { const z = sp.find(([n]) => n === k); return z ? x(Math.min((z[1] + z[2] + 1) / 2, span)) : null; };
      const m = marks ?? {};
      if (m.bud_freeze_days > 0 && mid('buds')) parts.push(note('✱', mid('buds'), y + 15, 'middle', 13, '#0f2a4a', 700));
      if (m.flower_freeze_days > 0 && mid('flower')) parts.push(note('✱', mid('flower'), y + 15, 'middle', 13, '#0f2a4a', 700));
      if (m.fruit_frost_days > 0 && mid('fruit')) parts.push(note('✱', mid('fruit') - 8, y + 15, 'middle', 13, '#ffffff', 700));
      if (m.fruit_severe_heat_days > 0 && mid('fruit')) parts.push(note('☀', mid('fruit') + 8, y + 15, 'middle', 13, '#ffd166', 700));
      if (m.harvest_heavy_rain_days > 0 && mid('harvest')) parts.push(note(`● ${m.harvest_heavy_rain_days}`, mid('harvest'), y + 15, 'middle', 11, '#ffffff', 700));
      const text = sp.length ? `bloom ${dateAt(start, o.flowering_start)} to ${dateAt(start, o.flowering_end)}, harvest ${dateAt(start, o.harvest_start)} to ${dateAt(start, o.harvest_end)}` : 'dates unavailable';
      return `<g><title>${esc(`${label}: ${text}`)}</title>${parts.join('')}</g>`;
    };
    years.forEach((y, i) => out.push(row(y.offset_days, top + i * rowH, String(y.year), y.outcome, y.marks, false)));
    const yT = top + years.length * rowH + 4;
    out.push(`<line x1="${L}" x2="${L + inner}" y1="${yT - 2}" y2="${yT - 2}" stroke="#2b2f36" stroke-width="0.8"/>`);
    out.push(row(typicalOffsets(start, s.dates), yT + 2, 'Typical', 'complete', null, true));
    return `<svg viewBox="0 0 ${width} ${yT + rowH + 12}" role="img" aria-label="${esc(`Cycles started on ${startLabel(start)}, one row per year`)}">${hatch('yr-none')}${out.join('')}</svg>`;
  }

  function hazardSvg(hc, minValid) {
    const L = 170, width = 1060, inner = width - L - 20, cw = inner / hc.weeks, rowH = 26, top = 30, out = [];
    for (let m = 0; m < 12; m++) {
      const d = (Date.UTC(REF, m, 1) - Date.UTC(REF, 0, 1)) / DAY;
      out.push(`<line x1="${L + d / 7 * cw}" x2="${L + d / 7 * cw}" y1="${top - 14}" y2="${top + hc.hazards.length * rowH}" stroke="${COLOR.grid}"/>` + note(MONTHS[m], L + d / 7 * cw + 4, top - 18, 'start', 11));
    }
    hc.hazards.forEach((h, i) => {
      const y = top + i * rowH;
      out.push(`<g><title>${esc(h.definition)}</title>${note(h.label, L - 10, y + 16, 'end', 12, '#1d1d1f')}</g>`);
      for (let w = 0; w < hc.weeks; w++) {
        const k = h.years_with_event[w], n = h.valid_years[w], ok = n >= minValid;
        const fill = ok ? `fill="${COLOR.hazard}" fill-opacity="${(0.06 + 0.94 * k / n).toFixed(3)}"` : 'fill="url(#yr-gap)"';
        out.push(`<rect x="${L + w * cw + 0.5}" y="${y + 3}" width="${cw - 1}" height="${rowH - 6}" ${fill}><title>${esc(`${h.label}, week ${w + 1} (from ${dateAt('01-01', w * 7)}): ${ok ? `${k} of ${n} years` : `only ${n} years with complete data`}`)}</title></rect>`);
      }
    });
    const y = top + hc.hazards.length * rowH + 22;
    for (const [i, share] of [0, 0.25, 0.5, 0.75, 1].entries()) out.push(`<rect x="${L + i * 120}" y="${y - 10}" width="14" height="12" fill="${COLOR.hazard}" fill-opacity="${0.06 + 0.94 * share}"/>` + note(`${share * 100}% of years`, L + i * 120 + 18, y, 'start', 11));
    return `<svg viewBox="0 0 ${width} ${y + 10}" role="img" aria-label="Weekly weather hazards, share of years">${hatch('yr-gap')}${out.join('')}</svg>`;
  }

  function warmSvg(monthly, enso) {
    const rows = anomalies(monthly), years = [...new Set(rows.map(r => r.year))].sort((a, b) => a - b);
    if (!years.length) return '';
    const phase = new Map((enso?.months ?? []).map(m => [`${m.year}-${m.month}`, m.phase]));
    const L = 70, width = 1060, inner = width - L - 20, cw = inner / 12, rowH = 22, top = 24, out = [];
    MONTHS.forEach((m, i) => out.push(note(m, L + i * cw + cw / 2, top - 8, 'middle', 11)));
    years.forEach((year, j) => {
      const y = top + j * rowH;
      out.push(note(year, L - 10, y + 15, 'end', 12, '#1d1d1f'));
      for (const r of rows.filter(r => r.year === year)) {
        const a = Math.max(-2, Math.min(2, r.anomaly)), fill = a >= 0 ? `rgba(184,53,42,${(a / 2).toFixed(3)})` : `rgba(61,75,155,${(-a / 2).toFixed(3)})`;
        const p = phase.get(`${year}-${r.month}`), cx = L + (r.month - 1) * cw;
        const outline = p === 'el_nino' ? 'stroke="#1d1d1f" stroke-width="2"' : p === 'la_nina' ? 'stroke="#3d4b9b" stroke-width="1.5" stroke-dasharray="3 2"' : 'stroke="none"';
        out.push(`<rect x="${cx + 1}" y="${y + 2}" width="${cw - 2}" height="${rowH - 4}" fill="${fill}" ${outline}><title>${esc(`${MONTHS[r.month - 1]} ${year}: ${r.anomaly >= 0 ? '+' : ''}${r.anomaly.toFixed(1)} °C against this month's average${p === 'el_nino' ? ', El Niño' : p === 'la_nina' ? ', La Niña' : ''}`)}</title></rect>` +
          note(`${r.anomaly >= 0 ? '+' : ''}${r.anomaly.toFixed(1)}`, cx + cw / 2, y + 15, 'middle', 10.5, Math.abs(a) > 1.2 ? '#ffffff' : '#1d1d1f'));
      }
    });
    const y = top + years.length * rowH + 22;
    out.push(`<rect x="${L}" y="${y - 11}" width="22" height="14" fill="none" stroke="#1d1d1f" stroke-width="2"/>` + note('El Niño month (NOAA ONI)', L + 28, y, 'start', 11) +
      `<rect x="${L + 210}" y="${y - 11}" width="22" height="14" fill="none" stroke="#3d4b9b" stroke-width="1.5" stroke-dasharray="3 2"/>` + note('La Niña month', L + 238, y, 'start', 11) +
      `<rect x="${L + 360}" y="${y - 11}" width="22" height="14" fill="rgba(184,53,42,1)"/>` + note('2 °C or more warmer than usual', L + 388, y, 'start', 11) +
      `<rect x="${L + 600}" y="${y - 11}" width="22" height="14" fill="rgba(61,75,155,1)"/>` + note('2 °C or more cooler', L + 628, y, 'start', 11));
    return `<svg viewBox="0 0 ${width} ${y + 10}" role="img" aria-label="Monthly temperature anomaly by year with El Niño months">${out.join('')}</svg>`;
  }

  // Years whose favourable-flowering months ran warmest, with the El Nino share of those months.
  function warmFlowering(monthly, enso, months) {
    if (!months?.length) return [];
    const phase = new Map((enso?.months ?? []).map(m => [`${m.year}-${m.month}`, m.phase]));
    const by = {};
    for (const r of anomalies(monthly)) if (months.includes(r.month)) (by[r.year] ??= []).push(r);
    return Object.entries(by).filter(([, v]) => v.length === months.length)
      .map(([year, v]) => ({year: Number(year), anomaly: v.reduce((a, r) => a + r.anomaly, 0) / v.length,
        elNino: v.filter(r => phase.get(`${year}-${r.month}`) === 'el_nino').length, months: v.length}))
      .sort((a, b) => b.anomaly - a.anomaly);
  }

  const monthList = months => months.length ? months.map(m => MONTHS[m - 1]).join(', ') : 'none';

  function plannerTable(mc, targets) {
    if (!targets.length) return '<p class="season-notes">Choose one or more months above to rank start dates.</p>';
    const rows = plan(mc, targets);
    return `<div class="table-scroll" tabindex="0" role="region" aria-label="Start dates ranked for the chosen harvest months"><table><thead><tr><th>Start (budbreak)</th><th>First pick in your months</th><th>Typical bloom</th><th>Typical harvest</th><th>Crop-loss risks that recur</th><th>Other recurring weather</th></tr></thead><tbody>${rows.map(r => {
      const s = r.start, d = s.dates ?? {};
      return `<tr${r.usable ? '' : ' class="yr-muted"'}><th scope="row">${esc(startLabel(s.budbreak))}${r.favourable ? ' <span class="badge">Favourable</span>' : ''}</th>` +
        `<td>${r.n ? `${r.hits} of ${r.n} years` : 'no complete cycles'}</td><td>${d.flowering_start ? `${esc(startLabel(d.flowering_start))} to ${esc(startLabel(d.flowering_end))}` : '–'}</td>` +
        `<td>${d.harvest_start ? `${esc(startLabel(d.harvest_start))} to ${esc(startLabel(d.harvest_end))}` : '–'}</td>` +
        `<td>${s.recurring_crop_loss.length ? esc(s.recurring_crop_loss.map(k => LOSS[k] ?? k).join(', ')) : s.rankable ? 'none' : 'too few complete cycles'}</td>` +
        `<td>${esc(s.recurring.filter(k => !LOSS[k]).map(k => OTHER[k] ?? k).join(', ') || 'none')}</td></tr>`;
    }).join('')}</tbody></table></div>`;
  }

  function draw(root) {
    const st = state.get(root), {result, p, published, enso} = st, mc = p?.managed_cycle, parts = [];
    const pub = published?.site;
    parts.push(`<p class="season-story">In evergreen and tropical systems the grower starts each crop by pruning, and sometimes by cutting water or nitrogen. These views ask: if a cycle starts on a given date, what weather does each stage meet, and does the harvest land in the months you want to sell? ${mc ? '' : 'The start-date scan is not available for this location, so only the weather views are shown.'}</p>`);
    if (mc?.starts?.length && mc.starts[0].years) {
      const opts = mc.starts.map(s => `<option value="${esc(s.budbreak)}"${s.budbreak === st.start ? ' selected' : ''}>${esc(startLabel(s.budbreak))}${(mc.favourable?.budbreak ?? []).includes(s.budbreak) ? ' (favourable)' : ''}</option>`).join('');
      const s = mc.starts.find(x => x.budbreak === st.start);
      parts.push(`<h3>1. Start a cycle on a chosen date</h3><div class="season-controls"><label for="yr-start">Budbreak on</label><select id="yr-start" data-yr-start>${opts}</select><span>${esc(`${s.cycles} complete and ${s.stalled_cycles} stalled cycles; ${s.outcomes.weather_incomplete} years with incomplete weather.`)}</span></div>` +
        `<div class="season-scroll" tabindex="0" role="region" aria-label="Cycles for the chosen start date. Scroll horizontally on narrow screens.">${startSvg(mc, st.start, pub)}</div>` +
        `<div class="season-notes"><p>Each row is one year's cycle if budbreak happened on ${esc(startLabel(st.start))}; stages follow the model's heat clock. The time from pruning to budbreak is not modelled, so prune earlier than this date.${pub ? ` Grower months: ${esc(pub.name)}${published.km ? `, ${published.km.toFixed(1)} km away` : ''}.` : ''}</p><p>Marks use the stage-risk thresholds. "Stalled" means flowering ran longer than 66 days or the first harvest came more than 150 days after flowering began.</p></div>`);
    }
    const hc = result.hazard_calendar;
    if (hc?.hazards?.length) {
      const minValid = p?.managed_cycle?.policy?.min_valid_years ?? 12;
      parts.push(`<h3>2. Weather hazards through the year</h3><div class="season-scroll" tabindex="0" role="region" aria-label="Weekly hazards. Scroll horizontally on narrow screens.">${hazardSvg(hc, minValid)}</div>` +
        `<div class="season-notes"><p>Each cell is one week, shaded by the share of years ${esc(hc.years.join(' to '))} with at least one such day that week. Hatched weeks have fewer than ${minValid} years with complete data. Use it to choose weeks for flowers and ripe fruit when there is no fixed season. Hover a row name for its threshold.</p></div>`);
    }
    if (mc?.starts?.[0]?.years) {
      const buttons = MONTHS.map((m, i) => `<button type="button" data-yr-month="${i + 1}" aria-pressed="${st.targets.includes(i + 1)}">${m}</button>`).join('');
      parts.push(`<h3>3. Plan for a market window</h3><div class="season-controls" role="group" aria-label="Months you want to harvest"><span>Harvest wanted in</span>${buttons}</div>` +
        `${plannerTable(mc, st.targets)}<div class="season-notes"><p>Starts are ranked by: no recurring crop-loss risk, then the share of years whose first pick falls in your months, then fewer recurring weather problems. Greyed rows have a recurring crop-loss risk or too few complete cycles. ${pub?.harvest_months?.length && st.defaulted ? `Months start from the growers' harvest months at ${esc(pub.name)}.` : ''} Prices, labour and water are not included.</p></div>`);
    }
    if (result.monthly?.length) {
      const fav = mc?.favourable?.flowering_months ?? [], ranked = warmFlowering(result.monthly, enso, fav);
      const lines = ranked.slice(0, 3).map(r => `${r.year}: ${r.anomaly >= 0 ? '+' : ''}${r.anomaly.toFixed(1)} °C${r.elNino ? `, El Niño in ${r.elNino} of ${r.months} months` : ''}`);
      parts.push(`<h3>4. Warm years and El Niño</h3><div class="season-scroll" tabindex="0" role="region" aria-label="Monthly temperature anomaly. Scroll horizontally on narrow screens.">${warmSvg(result.monthly, enso)}</div>` +
        `<div class="season-notes">${lines.length ? `<p>Warmest years in the favourable flowering months (${esc(monthList(fav))}): ${esc(lines.join('; '))}.</p>` : ''}<p>Each cell is that month's mean temperature minus the same month's average over all years shown. A warm winter can upset flowering of low-chill cultivars in evergreen systems, as reported in northern Peru in 2023. ${enso ? `El Niño months follow ${esc(enso.source.rule)} The latest seasons can change label once later values arrive.` : 'El Niño months could not load.'}</p></div>`);
    }
    parts.push('<div class="season-notes"><p>All dates are scenarios from the weather archive, not forecasts. The heat clock was set for low-chill bushes after winter and has not been checked against evergreen farm records.</p></div>');
    root.innerHTML = `<div class="season-panel yr-panel">${parts.join('')}</div>`;
  }

  function render(root, result, ctx) {
    if (!root) return;
    if (!result) { root.innerHTML = ''; return; }
    const p = result.production?.status === 'available' ? result.production : null, mc = p?.managed_cycle;
    const old = state.get(root), same = old?.result === result;
    const published = ctx.published, pubMonths = published?.site?.harvest_months ?? [];
    state.set(root, {result, p, published, enso: ctx.enso,
      start: same ? old.start : mc ? defaultStart(mc) : null,
      targets: same ? old.targets : [...pubMonths], defaulted: same ? old.defaulted : pubMonths.length > 0});
    if (!root.dataset.yrBound) {
      root.addEventListener('change', e => {
        if (!e.target.matches('[data-yr-start]')) return;
        state.get(root).start = e.target.value; draw(root); root.querySelector('[data-yr-start]')?.focus();
      });
      root.addEventListener('click', e => {
        const b = e.target.closest('[data-yr-month]'); if (!b) return;
        const st = state.get(root), m = Number(b.dataset.yrMonth);
        st.targets = st.targets.includes(m) ? st.targets.filter(x => x !== m) : [...st.targets, m].sort((a, c) => a - c);
        st.defaulted = false; draw(root); root.querySelector(`[data-yr-month="${m}"]`)?.focus();
      });
      root.dataset.yrBound = 'true';
    }
    draw(root);
  }

  async function loadEnso(url = 'enso.json') {
    const response = await fetch(url, {credentials: 'same-origin'});
    if (!response.ok) throw Error('El Niño table could not load.');
    const data = await response.json();
    if (!Array.isArray(data?.months)) throw Error('El Niño table has an unexpected format.');
    return data;
  }

  return Object.freeze({render, loadEnso, helpers: Object.freeze({monthOffset, dateAt, spans, typicalOffsets, defaultStart, plan, anomalies, warmFlowering})});
})();
