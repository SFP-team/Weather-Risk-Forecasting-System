'use strict';

// Presentation only. All dates, assumptions and exposures come from the production result.
// Stage colours identify analysis windows, not severity.
const CycleView = (() => {
  const DAY = 86400000;
  const stages = [
    { id: 'chill', title: 'Winter chill', subtitle: 'Cold-hour requirement' },
    { id: 'buds', title: 'Bud development', subtitle: 'Warmth after chill' },
    { id: 'flower', title: 'Flowering', subtitle: 'Flower-stage exposures' },
    { id: 'fruit', title: 'Fruit development', subtitle: 'Fruit-stage exposures' },
    { id: 'harvest', title: 'Harvest', subtitle: 'Harvest-stage exposures' },
    { id: 'whole', title: 'Production window', subtitle: 'Dry spells, light & warmth' },
  ];
  const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
  const finite = value => typeof value === 'number' && Number.isFinite(value);
  const number = (value, digits = 2) => finite(value) ? value.toLocaleString('en-US', { maximumFractionDigits: digits }) : 'Unavailable';
  const exact = value => finite(value) ? String(value) : 'Unavailable';
  const date = (anchor, offset, year = false) => finite(offset)
    ? new Date(anchor + Math.round(offset) * DAY).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', ...(year ? { year: 'numeric' } : {}), timeZone: 'UTC' })
    : 'Unavailable';
  const parse = value => typeof value === 'string' ? Date.parse(`${value}T00:00:00Z`) : NaN;
  const shift = (value, delta) => finite(value) ? value + delta : null;
  const reason = status => ({ chill_not_met: 'Chill requirement not met', incomplete_chill: 'Incomplete hourly winter',
    incomplete_gdd: 'Incomplete temperature history', gdd_not_met_within_horizon: 'Heat requirement not reached',
    stage_gdd_not_met: 'Stage heat requirement not reached', incomplete_stage_dates: 'Incomplete temperature history after budbreak',
    incomplete_metrics: 'Some stage exposures are unavailable' })[status] || 'Stage timing unavailable';
  const share = value => finite(value) ? `${number(value * 100, 1)}%` : 'Unavailable';
  const measureNames = { bud_freeze: 'Bud freeze', flowering_freeze: 'Flowering freeze', fruit_frost: 'Fruit frost', fruit_heat: 'Fruit heat',
    harvest_heavy_rain: 'Harvest heavy rain', disease_weather: 'Disease weather', pollination: 'Days without bee flight' };

  function model(p, winter) {
    const season = winter === 'typical' ? null : p.seasons.find(row => String(row.winter_year) === winter);
    const anchor = season ? parse(season.season_start) : Date.UTC(p.hemisphere === 'south' ? 2001 : 2000, p.hemisphere === 'south' ? 3 : 10, 1);
    const winterEnd = season ? (parse(season.season_end_exclusive) - anchor) / DAY
      : (Date.UTC(2001, p.hemisphere === 'south' ? 9 : 4, 1) - anchor) / DAY;
    const offset = (key, quantile = 'median') => season ? season.offset_days?.[key] : p.calendar?.[key]?.[quantile];
    const interval = (id, qStart = 'median', qEnd = 'median') => {
      switch (id) {
        case 'chill': return [0, winterEnd - 1];
        case 'buds': return [offset('chill', qStart), shift(offset('flowering_start', qEnd), -1)];
        case 'flower': return [offset('flowering_start', qStart), offset('flowering_end', qEnd)];
        case 'fruit': return [shift(offset('flowering_end', qStart), 1), shift(offset('harvest_start', qEnd), -1)];
        case 'harvest': return [offset('harvest_start', qStart), offset('harvest_end', qEnd)];
        // Profiles that require an applicable calendar measure the production window from budbreak.
        case 'whole': return [p.assumptions?.require_applicable_calendar ? offset('budbreak', qStart) : 0, offset('harvest_end', qEnd)];
      }
    };
    const rows = stages.map(stage => ({ ...stage, span: interval(stage.id), spread: season ? null : interval(stage.id, 'p10', 'p90') }));
    // Keep the same horizon when switching winters. Do not clip a late season.
    const ends = p.seasons.map(row => row.offset_days?.harvest_end).filter(finite);
    const latest = Math.max(winterEnd, ...ends.map(value => value + 1));
    const lastDate = new Date(anchor + latest * DAY);
    const end = Date.UTC(lastDate.getUTCFullYear(), lastDate.getUTCMonth() + 1, 1);
    const chill = season ? [season.chill_hours, season.chill_portions] : [p.chill_hours?.mean, p.chill_portions?.mean];
    const chillNote = [finite(chill[0]) ? `${number(chill[0], 0)} chill hours` : '', finite(chill[1]) ? `${number(chill[1], 1)} chill portions` : '']
      .filter(Boolean).join(' · ');
    return { season, anchor, rows, offset, days: (end - anchor) / DAY, chillNote: chillNote && (season ? chillNote : `Mean ${chillNote}`) };
  }

  function diagram(view, selected) {
    const left = 180, width = 750, right = left + width, top = 62, pitch = 46, height = top + stages.length * pitch + 4;
    const x = offset => left + offset / view.days * width;
    const months = [];
    let cursor = new Date(view.anchor);
    while ((cursor.getTime() - view.anchor) / DAY < view.days) {
      const offset = (cursor.getTime() - view.anchor) / DAY;
      const month = cursor.toLocaleDateString('en-GB', { month: 'short', timeZone: 'UTC' });
      const year = view.season && (offset === 0 || cursor.getUTCMonth() === 0) ? ` ${cursor.getUTCFullYear()}` : '';
      months.push(`<line x1="${x(offset)}" x2="${x(offset)}" y1="42" y2="${height - 12}" class="cycle-gridline"/>
        <text x="${x(offset) + 4}" y="25" class="cycle-month">${month}${year}</text>`);
      cursor = new Date(Date.UTC(cursor.getUTCFullYear(), cursor.getUTCMonth() + 1, 1));
    }
    return `<svg viewBox="0 0 ${right + 16} ${height}" role="img" aria-labelledby="cycle-svg-title cycle-svg-desc">
      <title id="cycle-svg-title">Modelled seasonal analysis windows</title><desc id="cycle-svg-desc">${view.season ? `Winter ${view.season.winter_year}` : 'Median dates across historical winters'}. Colour identifies a stage, not severity. Bar lengths show analysis windows, not dates of weather events. Use the stage buttons to read dates and exposures.</desc>
      <text x="12" y="25" class="cycle-axis-title">ANALYSIS WINDOW</text>${months.join('')}
      ${view.rows.map((row, index) => {
        const y = top + index * pitch, on = selected === row.id;
        const available = row.span.every(finite) && row.span[1] >= row.span[0];
        const broad = row.spread?.every(finite) && row.spread[1] >= row.spread[0];
        const track = available ? `<rect x="${x(row.span[0])}" y="${y + 3}" width="${Math.max(2, x(row.span[1] + 1) - x(row.span[0]))}" height="16" rx="4" class="cycle-bar"/>` : `<text x="${left + 10}" y="${y + 16}" class="cycle-missing">${escape(reason(view.season?.status))}</text>`;
        const markerKey = row.id === 'chill' ? 'chill' : row.id === 'buds' ? 'budbreak' : null;
        const marker = markerKey ? view.offset(markerKey) : null;
        return `<g class="cycle-lane${on ? ' is-selected' : ''}" data-cycle-lane="${row.id}" data-stage="${row.id}">
          <title>${row.title}: ${available ? `${date(view.anchor, row.span[0])} to ${date(view.anchor, row.span[1])}` : 'Unavailable'}${row.id === 'chill' && view.chillNote ? ` · ${view.chillNote}` : ''}</title>
          <rect x="0" y="${y - 10}" width="${right + 12}" height="42" rx="6" class="cycle-row-highlight"/>
          <text x="12" y="${y + 6}" class="cycle-row-title">${row.title}</text><text x="12" y="${y + 23}" class="cycle-row-subtitle">${available ? `${date(view.anchor, row.span[0])} to ${date(view.anchor, row.span[1])}` : 'Window unavailable'}</text>
          ${broad && row.id !== 'chill' ? `<rect x="${x(row.spread[0])}" y="${y - 2}" width="${Math.max(2, x(row.spread[1] + 1) - x(row.spread[0]))}" height="26" rx="5" class="cycle-spread"/>` : ''}${track}
          ${row.id === 'chill' && available && view.chillNote && x(row.span[1] + 1) - x(row.span[0]) > 260 ? `<text x="${x(row.span[1] + 1) - 10}" y="${y + 15}" text-anchor="end" class="cycle-bar-text">${escape(view.chillNote)}</text>` : ''}
          ${finite(marker) ? `<path d="M ${x(marker)} ${y - 6} v 33" class="cycle-marker"/><circle cx="${x(marker)}" cy="${y - 6}" r="3" class="cycle-marker-dot"><title>${markerKey === 'chill' ? 'Requirement reached' : 'Budbreak'}: ${date(view.anchor, marker)}</title></circle>` : ''}
        </g>`;
      }).join('')}</svg>`;
  }

  function metricSummary(p, key) {
    return p.risks.exposures[key] ?? p[key];
  }

  function metricValue(view, key) {
    return key in view.season ? view.season[key] : view.season.metrics?.[key];
  }

  function metricCard(p, view, metric) {
    const { key, label, unit, note } = metric;
    const s = metricSummary(p, key);
    const value = view.season ? metricValue(view, key) : s?.mean;
    const issue = view.season?.issues?.[key];
    const withUnit = value => `${number(value)}${finite(value) ? ` <span>${escape(unit)}</span>` : ''}`;
    return `<article class="cycle-metric" data-metric="${escape(key)}">
      <h4>${escape(label)}</h4><dl class="cycle-value-pair"><div><dt>${view.season ? `Winter ${view.season.winter_year}` : 'Historical mean'}</dt><dd title="${escape(exact(value))} ${escape(unit)}">${withUnit(value)}</dd></div>
      ${view.season ? `<div class="cycle-comparison"><dt>Historical mean</dt><dd title="${escape(exact(s?.mean))} ${escape(unit)}">${withUnit(s?.mean)}</dd></div>` : ''}</dl>
      <p class="cycle-coverage">${finite(s?.n) ? `${s.n} / ${p.seasons.length} valid winters` : 'Historical coverage unavailable'}${view.season && !finite(value) ? ' · Selected winter unavailable' : ''}</p>
      <details class="cycle-metric-details"><summary>Definition & exact values</summary><p>${escape(note)}</p>
        ${view.season ? `<p>${escape(issue || (finite(value) ? 'Selected winter, within its own analysis window.' : 'No usable value for this winter.'))}</p>` : ''}
        <dl class="cycle-exact-values">${view.season ? `<div><dt>Selected winter · ${escape(unit)}</dt><dd>${escape(exact(value))}</dd></div>` : ''}
        ${[['mean', 'Historical mean'], ['median', 'Historical median'], ['p10', 'Historical p10'], ['p90', 'Historical p90']].map(([stat, name]) => `<div><dt>${name} · ${escape(unit)}</dt><dd>${escape(exact(s?.[stat]))}</dd></div>`).join('')}</dl>
        <p>Missing values are not zero. Historical summaries use valid winters for this metric.</p>
      </details></article>`;
  }

  function assessmentDetail(event, selectedWinter) {
    return `<article class="cycle-frequency"><h4>${escape(event.label)}</h4><p>${escape(event.event_definition ?? 'No event threshold is assigned.')}</p>
      ${finite(event.years_with_event) && finite(event.frequency) ? `<p><strong>${event.years_with_event} / ${event.valid_years} valid winters</strong> · ${number(event.frequency * 100)}% historical frequency${event.ci95 ? ` · 95% Wilson CI ${number(event.ci95[0] * 100)}% to ${number(event.ci95[1] * 100)}%` : ''}.</p><p>${event.total_years} total winters. Exact frequency proportion ${escape(exact(event.frequency))}${event.ci95 ? `; exact 95% CI ${escape(exact(event.ci95[0]))} to ${escape(exact(event.ci95[1]))}` : ''}.</p>` : `<p>Event frequency not assigned. ${event.valid_years} valid exposure winters out of ${event.total_years}.</p>`}
      <p><strong>${escape(eligibilityLabel[event.eligibility] ?? event.eligibility)}</strong>. ${escape(event.reason)}</p><p class="evidence-sources">${sourceLinks(event.evidence)}</p>${selectedWinter ? '<p>Frequency and eligibility describe the historical record, not the selected winter alone.</p>' : ''}</article>`;
  }

  function winterContext(p, view) {
    const metric = p.metric_catalog.find(item => item.key === 'warm_midwinter_hours');
    if (!metric) return '';
    const window = view.season?.warm_midwinter_window;
    const assessment = p.risks.by_id.warm_midwinter;
    return `<section class="winter-context" aria-labelledby="winter-context-title"><header><span class="stamp">Independent winter context</span><h3 id="winter-context-title">Warm midwinter hours</h3><p>Fixed winter dates, independent of chill fulfilment and crop stages. This proxy does not measure chill negation.</p></header>
      <div>${metricCard(p, view, metric)}<details class="cycle-context-evidence"><summary>Window, interpretation & sources</summary><p>${window ? `${escape(window[0])} to ${escape(window[1])}, inclusive UTC dates.` : 'Exact UTC windows are listed in the full per-winter record below.'}</p>${assessment ? assessmentDetail(assessment, !!view.season) : '<p>No assessment is available.</p>'}</details></div></section>`;
  }

  function detail(p, view, selected, hypothetical) {
    const stage = view.rows.find(row => row.id === selected), a = p.assumptions;
    const available = stage.span.every(finite) && stage.span[1] >= stage.span[0];
    const metrics = p.metric_catalog.filter(metric => metric.stage === selected && metric.key !== 'warm_midwinter_hours');
    const events = Object.values(p.risks.by_id).filter(event => event.risk !== 'warm_midwinter' && (event.stage === selected || metrics.some(metric => metric.key in (event.exposure ?? {}))));
    const budNote = selected === 'buds' ? `<div class="cycle-explanation"><p>Assumed budbreak <strong>${date(view.anchor, view.offset('budbreak'), !!view.season)}</strong>.${metrics.length ? ' Bud-stage freeze uses NC State critical temperatures for the bud stage.' : ' No separate bud-stage exposure metric is available.'}</p><details><summary>Timing assumptions · ${escape(stageClockLabel(a))}</summary><p>${escape(stageTiming(a))}</p><p>These are timing assumptions, not observed plant stages.</p></details></div>` : '';
    return `<header class="cycle-detail-heading"><div><span class="stamp">${view.season ? `Winter ${view.season.winter_year}` : 'Historical exposure summary'}${hypothetical ? ' · Hypothetical exposures' : ''}</span><h3 id="cycle-detail-title">${stage.title}</h3></div><p>${available ? `${hypothetical ? 'Hypothetical' : view.season ? 'Modelled' : 'Median'} window<br><strong>${date(view.anchor, stage.span[0], !!view.season)} to ${date(view.anchor, stage.span[1], !!view.season)}</strong>` : escape(reason(view.season?.status))}</p></header>
      ${view.season && view.season.status !== 'complete' ? `<p class="cycle-notice">${escape(reason(view.season.status))}. Missing values are not zero exposure.</p>` : ''}
      <div class="cycle-metrics">${metrics.map(metric => metricCard(p, view, metric)).join('')}</div>${budNote}
      ${events.length ? `<details class="cycle-stage-evidence"><summary>Historical event definitions, eligibility & sources · ${events.length} assessments</summary>${events.map(event => assessmentDetail(event, !!view.season)).join('')}</details>` : ''}
      ${selected === 'harvest' ? '<p class="cycle-footnote">Rainfall totals and day counts describe different exposures. Neither is an estimate of crop loss.</p>' : ''}
      ${selected === 'whole' ? `<p class="cycle-footnote">${p.assumptions?.require_applicable_calendar ? 'Production metrics cover budbreak through harvest end.' : 'This legacy profile covers season start through harvest end.'} Totals do not locate dry spells or radiation extremes within that window.</p>` : ''}`;
  }

  // Managed-cycle scan: each 1st/15th start is a management scenario for budbreak, not a chill-triggered date.
  function managedCycle(p) {
    const m = p.managed_cycle;
    if (!m?.starts?.length) return '';
    const primary = m.role === 'primary', fav = m.favourable ?? {}, policy = m.policy ?? {};
    const favourable = new Set(fav.budbreak ?? []);
    const state = start => start.recurring_crop_loss?.length ? 'loss' : !start.rankable ? 'unrankable' : favourable.has(start.budbreak) ? 'favourable' : 'other';
    const stateLabel = { favourable: 'Favourable', loss: 'Recurring crop loss', unrankable: 'Not rankable', other: 'Not favourable' };
    const names = ids => (ids ?? []).map(id => riskLabel(p, id));
    const span = (from, to) => from && to ? `${md(from)} – ${md(to)}` : 'Unavailable';
    const startsIn = key => m.starts.filter(start => state(start) === key).map(start => md(start.budbreak)).join(', ') || 'none';
    const minCycles = finite(policy.min_valid_years) ? `fewer than ${policy.min_valid_years} complete cycles` : 'too few complete cycles';
    const cells = m.starts.map(start => {
      const kind = state(start);
      const tip = `${md(start.budbreak)} start · ${stateLabel[kind]} · ${start.cycles} complete, ${start.stalled_cycles} stalled cycles${start.recurring?.length ? ` · recurring: ${names(start.recurring).join(', ')}` : ''}`;
      return `<span class="scan-cell is-${kind}${start.stalled_cycles ? ' has-stalled' : ''}" title="${escape(tip)}"></span>`;
    }).join('');
    const rows = m.starts.map(start => {
      const kind = state(start), d = start.dates ?? {};
      // Crop-loss families first; a stalled start can list both even when other events lack complete cycles.
      const loss = start.recurring_crop_loss ?? [], ids = [...new Set([...loss, ...(start.recurring ?? [])])];
      const recurring = ids.map(id => `${riskLabel(p, id)} ${share(start.events?.[id]?.frequency)}${loss.includes(id) ? ' (crop loss)' : ''}`);
      return `<tr class="is-${kind}"><th scope="row">${md(start.budbreak)}<span class="risk-stage">${stateLabel[kind]}</span></th><td>${span(d.flowering_start, d.flowering_end)}</td><td>${span(d.harvest_start, d.harvest_end)}</td><td>${escape(exact(start.cycles))} / ${escape(exact(start.stalled_cycles))}</td>${(m.measures ?? []).map(measure => `<td>${share(start.measures?.[measure.key])}</td>`).join('')}<td>${recurring.length ? escape(recurring.join(' · ')) : 'None'}</td></tr>`;
    }).join('');
    const timing = fav.unconstrained
      ? '<div><dt>Favourable starts</dt><dd>Weather does not separate start dates; timing is a market or management choice.</dd></div>'
      : `<div><dt>Favourable starts (budbreak)</dt><dd>${escape((fav.budbreak ?? []).map(md).join(', ') || 'None')}</dd></div><div><dt>Flowering</dt><dd>${escape(monthRuns(fav.flowering_months))}</dd></div><div><dt>Harvest</dt><dd>${escape(monthRuns(fav.harvest_months))}</dd></div>`;
    return `<header class="scan-header"><div><span class="stamp">${primary ? 'Management scenario · production window for this location' : 'Comparison · management scenario'}</span><h3 id="managed-cycle-title">${primary ? 'Managed-cycle scan' : 'If managed as an evergreen cycle'}</h3>
      <p>${primary ? 'The chill-triggered calendar does not apply here. Each start date is a managed budbreak of the fruiting cycle; the favourable starts give the production window.' : 'The chill-triggered calendar applies here. This comparison scores cycles started by management on each date against the same historical weather.'}</p></div><span class="scan-chip">${escape(stageClockLabel(p.assumptions))}</span></header>
      <dl class="scan-facts">${timing}<div><dt>Recurring at favourable starts</dt><dd>${escape(names(fav.recurring).join(', ') || 'None')}</dd></div></dl>
      <div class="scan-strip-wrap"><div class="scan-strip" role="img" aria-label="Cycle starts on the 1st and 15th of each month. Favourable: ${escape(startsIn('favourable'))}. Recurring crop loss: ${escape(startsIn('loss'))}. Not rankable: ${escape(startsIn('unrankable'))}.">${cells}</div>
      <div class="scan-months" aria-hidden="true">${MONTHS.map(month => `<span>${month}</span>`).join('')}</div></div>
      <div class="scan-legend"><span><i class="scan-key is-favourable"></i>Favourable start</span><span><i class="scan-key is-loss"></i>Recurring crop loss</span><span><i class="scan-key is-unrankable"></i>Not rankable (${escape(minCycles)})</span><span><i class="scan-key is-other"></i>Other start</span><span><i class="scan-key has-stalled"></i>Some cycles stalled</span></div>
      <div class="table-scroll" tabindex="0" role="region" aria-label="Managed-cycle starts: dates, cycles, measures and recurring risks"><table class="scan-table"><thead><tr><th scope="col">Cycle start</th><th scope="col">Flowering</th><th scope="col">Harvest</th><th scope="col">Complete / stalled cycles</th>${(m.measures ?? []).map(measure => `<th scope="col">${escape(measureNames[measure.key] ?? measure.key)}</th>`).join('')}<th scope="col">Recurring risks · share of cycles</th></tr></thead><tbody>${rows}</tbody></table></div>
      <p class="scan-note">Dates are medians across complete cycles. Percentages are historical exposure shares, not loss probabilities.</p>
      <details class="scan-details"><summary>Measures, selection rule and limitations</summary><dl class="scan-measures">${(m.measures ?? []).map(measure => `<div><dt>${escape(measureNames[measure.key] ?? measure.key)}</dt><dd>${escape(measure.definition)}${finite(measure.tolerance) ? `. Separation tolerance ${escape(number(measure.tolerance * 100, 1))} percentage points.` : ''}</dd></div>`).join('')}</dl>
      <p>${escape(m.rule)}</p><ul>${(m.limitations ?? []).map(item => `<li>${escape(item)}</li>`).join('')}</ul></details>`;
  }

  function mount(root, p, context) {
    const reference = document.createElement('details');
    reference.className = 'cycle-reference';
    const summary = document.createElement('summary');
    summary.textContent = 'Full calendar, exposure tables, system rules & assumptions';
    reference.append(summary);
    const tables = root.querySelector('.production-reference');
    if (tables) reference.append(tables);
    root.append(reference);
    const panel = document.createElement('section');
    panel.className = 'cycle-panel';
    panel.setAttribute('aria-labelledby', 'cycle-heading');
    const hypothetical = !chillCalendarApplies(p);
    const unsupported = hypothetical || !p.seasons.length;
    const majority = p.classification?.multi_feature?.majority, reasons = p.chill_clock?.reasons ?? [];
    const managed = p.managed_cycle?.role === 'primary';
    panel.innerHTML = `<header class="cycle-header"><div><span class="stamp">${escape(context.site)} · Seasonal exposure</span><h3 id="cycle-heading">${unsupported ? 'Winter context & hypothetical exposures' : 'Season & exposures'}</h3><p>Select a winter and stage to compare exposures with historical means.</p></div><label class="cycle-view-label" for="cycle-winter">Winter record<select id="cycle-winter"><option value="typical">Historical summary · ${escape(p.years.join(' to '))}</option>${p.seasons.map(row => `<option value="${row.winter_year}">Winter ${row.winter_year}${row.status !== 'complete' ? ' · incomplete' : ''}</option>`).join('')}</select></label></header>
      <div class="cycle-scope"><span>${escape(p.profile)} · ${escape(stageClockLabel(p.assumptions))} · ${p.chill_clock?.chill_requirement_applies === false ? 'chill requirement not applied' : `${escape(p.assumptions.chill_requirement_hours)} h requirement`} · UTC</span><span>${escape(systemLabel(majority))}${majority === 'Transitional' ? '' : ' hypothesis'} · open field + ground · unvalidated</span></div>
      ${unsupported ? `<div class="cycle-notice"><p>${hypothetical ? `No applicable chill-triggered crop timeline.${reasons.length ? '' : ' Evergreen production needs a management anchor; an unclassified result has no supported crop calendar.'} Retained crop-stage exposures are hypothetical.${managed ? ' The managed-cycle scan above gives the production window for this location.' : ''}` : 'No winter records are available for a crop timeline.'} Warm midwinter context remains independent.</p>${hypothetical && reasons.length ? `<ul>${reasons.map(item => `<li>${escape(item)}</li>`).join('')}</ul>` : ''}</div>` : ''}
      ${!unsupported && majority === 'Transitional' ? '<p class="cycle-notice">Tentative calendar: no production system reaches a two-thirds majority across winters.</p>' : ''}
      ${context.system !== 'open_ground' ? '<p class="cycle-notice">Open-field baseline shown. No tunnel or pot adjustment is applied.</p>' : ''}
      <div class="cycle-layout"><div class="cycle-chart-side"><div class="cycle-nav-heading"><h4>${hypothetical ? 'Hypothetical stage exposures' : 'Crop stages & analysis windows'}</h4><span>Colours identify stages, not severity</span></div><div class="cycle-stage-controls" role="group" aria-label="${hypothetical ? 'Select a hypothetical stage' : 'Select a stage'}">${stages.map(stage => `<button type="button" data-cycle-stage="${stage.id}" data-stage="${stage.id}" aria-pressed="false" aria-controls="cycle-detail"><i aria-hidden="true"></i>${stage.title}</button>`).join('')}</div>
      <div class="cycle-scroll" tabindex="0" role="region" aria-label="Modelled monthly timeline. Scroll horizontally to see all months." aria-describedby="cycle-scroll-hint"${unsupported ? ' hidden' : ''}></div>
      <p class="cycle-scroll-hint" id="cycle-scroll-hint"${unsupported ? ' hidden' : ''}>Timeline scrolls horizontally on smaller screens. Stage dates are also shown below.</p>
      <div class="cycle-legend"${unsupported ? ' hidden' : ''}><span><i class="cycle-key-solid"></i>Analysis window</span><span class="cycle-spread-key"><i class="cycle-key-spread"></i>p10 start to p90 end</span><span><i class="cycle-key-marker"></i>Chill fulfilled / budbreak</span></div>
      <details class="cycle-timeline-details"${unsupported ? ' hidden' : ''}><summary>How to read the timeline</summary><p class="cycle-chart-note"></p><p>Bar length shows time, not severity. Exact weather-event dates are not available here.</p></details></div>
      <section id="cycle-detail" class="cycle-detail" aria-labelledby="cycle-detail-title"></section></div><p class="sr-only" id="cycle-status" role="status"></p>
      <div class="cycle-winter-context"></div><footer class="cycle-footer">Modelled dates are not observed phenology. Exposure counts and thresholds are not estimates of crop loss. Zero recorded events does not establish safety.</footer>`;
    root.insertBefore(panel, reference);
    const scan = managedCycle(p);
    if (scan) {
      const section = document.createElement('section');
      section.className = `managed-cycle${managed ? ' is-primary' : ''}`;
      section.setAttribute('aria-labelledby', 'managed-cycle-title');
      section.innerHTML = scan;
      // Primary: the scan is the production window, so it leads. Comparison: it follows the chill-triggered view.
      root.insertBefore(section, managed ? panel : reference);
    }
    let selected = stages.some(stage => stage.id === context.view?.stage) ? context.view.stage : 'flower';
    const selector = panel.querySelector('#cycle-winter');
    const winter = String(context.view?.winter ?? 'typical');
    if (winter === 'typical' || p.seasons.some(row => String(row.winter_year) === winter)) selector.value = winter;
    function update(announce = false) {
      const view = model(p, selector.value);
      panel.dataset.winter = selector.value;
      panel.dataset.stage = selected;
      if (!unsupported) panel.querySelector('.cycle-scroll').innerHTML = diagram(view, selected);
      panel.querySelector('.cycle-winter-context').innerHTML = winterContext(p, view);
      const detailPanel = panel.querySelector('.cycle-detail');
      detailPanel.dataset.stage = selected;
      detailPanel.innerHTML = detail(p, view, selected, hypothetical);
      panel.querySelector('.cycle-spread-key').hidden = !!view.season;
      panel.querySelector('.cycle-chart-note').textContent = view.season
        ? 'Dates and totals belong to this winter. The year label refers to the winter, not necessarily the harvest year. Each metric uses its own modelled analysis window.'
        : 'Solid bars use median stage boundaries. Outlines span the 10th-percentile start to the 90th-percentile end across valid winters. They show timing spread, not confidence limits or a single observed season. Exposure means are calculated from each winter’s own dates, not the median window.';
      panel.querySelectorAll('[data-cycle-stage]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.cycleStage === selected)));
      if (announce) {
        // One short line instead of re-reading the whole detail region on every change.
        const row = view.rows.find(item => item.id === selected), open = row.span.every(finite) && row.span[1] >= row.span[0];
        panel.querySelector('#cycle-status').textContent = `${row.title}, ${view.season ? `winter ${view.season.winter_year}` : 'historical summary'}: ${open ? `${hypothetical ? 'hypothetical ' : ''}${date(view.anchor, row.span[0], !!view.season)} to ${date(view.anchor, row.span[1], !!view.season)}` : reason(view.season?.status)}.`;
      }
    }
    panel.addEventListener('click', event => {
      const control = event.target.closest('[data-cycle-stage], [data-cycle-lane]');
      if (!control) return;
      selected = control.dataset.cycleStage || control.dataset.cycleLane;
      update(true);
    });
    selector.addEventListener('change', () => update(true));
    update();
  }

  function select(root, stage) {
    if (!stages.some(item => item.id === stage)) return false;
    const button = root.querySelector(`[data-cycle-stage="${stage}"]`);
    if (!button) return false;
    button.click();
    return true;
  }

  return { mount, select };
})();
