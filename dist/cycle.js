'use strict';

// Presentation only. Dates, assumptions and exposures come from the production result.
// Bar length represents time, never risk severity or the dates of weather events.
const CycleView = (() => {
  const DAY = 86400000;
  const stages = [
    { id: 'chill', title: 'Winter chill', subtitle: 'Cold-hour requirement', event: 'chill_shortfall' },
    { id: 'buds', title: 'Bud development', subtitle: 'Warmth after chill' },
    { id: 'flower', title: 'Flowering', subtitle: 'Cold, wet weather & dry runs', event: 'flowering_freeze' },
    { id: 'fruit', title: 'Fruit development', subtitle: 'Heat, frost & disease weather', event: 'fruit_severe_heat' },
    { id: 'harvest', title: 'Harvest', subtitle: 'Rain & disease weather', event: 'harvest_heavy_rain' },
    { id: 'whole', title: 'Whole cycle', subtitle: 'Dry spells, light & warmth' },
  ];
  const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
  const finite = value => typeof value === 'number' && Number.isFinite(value);
  const number = (value, digits = 1) => finite(value) ? value.toLocaleString('en-US', { maximumFractionDigits: digits }) : 'Unavailable';
  const date = (anchor, offset, year = false) => finite(offset)
    ? new Date(anchor + Math.round(offset) * DAY).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', ...(year ? { year: 'numeric' } : {}), timeZone: 'UTC' })
    : 'Unavailable';
  const parse = value => typeof value === 'string' ? Date.parse(`${value}T00:00:00Z`) : NaN;
  const shift = (value, delta) => finite(value) ? value + delta : null;
  const reason = status => ({ chill_not_met: 'Chill requirement not met', incomplete_chill: 'Incomplete hourly winter',
    incomplete_gdd: 'Incomplete temperature history', gdd_not_met_within_horizon: 'Heat requirement not reached',
    incomplete_metrics: 'Some stage exposures are unavailable' })[status] || 'Stage timing unavailable';

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
        case 'whole': return [0, offset('harvest_end', qEnd)];
      }
    };
    const rows = stages.map(stage => ({ ...stage, span: interval(stage.id), spread: season ? null : interval(stage.id, 'p10', 'p90') }));
    // Keep the same horizon when switching winters. Do not clip a late season.
    const ends = p.seasons.map(row => row.offset_days?.harvest_end).filter(finite);
    const latest = Math.max(winterEnd, ...ends.map(value => value + 1));
    const lastDate = new Date(anchor + latest * DAY);
    const end = Date.UTC(lastDate.getUTCFullYear(), lastDate.getUTCMonth() + 1, 1);
    return { season, anchor, rows, offset, days: (end - anchor) / DAY };
  }

  function laneSummary(p, view, row) {
    if (row.id === 'buds') return `Budbreak ${date(view.anchor, view.offset('budbreak'))}`;
    const key = { chill: 'chill_hours', flower: 'flower_freeze_days', fruit: 'fruit_severe_heat_days', harvest: 'harvest_heavy_rain_days', whole: 'production_max_dry_days' }[row.id];
    const metric = p.metric_catalog.find(m => m.key === key);
    const event = p.risks.by_id[row.event];
    if (!view.season && finite(event?.years_with_event)) return `${event.years_with_event}/${event.valid_years} winters · ${event.eligibility === 'ranked' ? 'recurring' : 'not ranked'}`;
    const value = view.season ? (key in view.season ? view.season[key] : view.season.metrics?.[key]) : metricSummary(p, key)?.mean;
    return finite(value) ? `${number(value)} ${metric?.unit ?? ''}${view.season ? '' : ' · mean'}` : 'Exposure unavailable';
  }

  function diagram(view, selected, p) {
    const left = 182, width = 776, right = left + width, top = 74, pitch = 50, height = top + stages.length * pitch + 8;
    const x = offset => left + offset / view.days * width;
    const months = [];
    let cursor = new Date(view.anchor);
    while ((cursor.getTime() - view.anchor) / DAY < view.days) {
      const offset = (cursor.getTime() - view.anchor) / DAY;
      const month = cursor.toLocaleDateString('en-GB', { month: 'short', timeZone: 'UTC' });
      const year = view.season && (offset === 0 || cursor.getUTCMonth() === 0) ? ` ${cursor.getUTCFullYear()}` : '';
      months.push(`<line x1="${x(offset)}" x2="${x(offset)}" y1="52" y2="${height - 12}" class="cycle-gridline"/>
        <text x="${x(offset) + 5}" y="35" class="cycle-month">${month}${year}</text>`);
      cursor = new Date(Date.UTC(cursor.getUTCFullYear(), cursor.getUTCMonth() + 1, 1));
    }
    return `<svg viewBox="0 0 ${right + 210} ${height}" role="img" aria-labelledby="cycle-svg-title cycle-svg-desc">
      <title id="cycle-svg-title">Growing cycle by month</title><desc id="cycle-svg-desc">${view.season ? `Modelled winter ${view.season.winter_year}` : 'Median dates across historical winters'}. Rows show analysis windows, not dates of weather events. Select a stage using the buttons above to read its exposures.</desc>
      <text x="12" y="35" class="cycle-axis-title">STAGE / EXPOSURE</text><text x="${right + 20}" y="35" class="cycle-axis-title">EXPOSURE SUMMARY</text>${months.join('')}
      ${view.rows.map((row, index) => {
        const y = top + index * pitch, on = selected === row.id;
        const available = row.span.every(finite) && row.span[1] >= row.span[0];
        const broad = row.spread?.every(finite) && row.spread[1] >= row.spread[0];
        const track = available ? `<rect x="${x(row.span[0])}" y="${y + 5}" width="${Math.max(2, x(row.span[1] + 1) - x(row.span[0]))}" height="18" rx="3" class="cycle-bar ${row.id === 'whole' ? 'cycle-context-bar' : ''}"/>` : `<text x="${left + 10}" y="${y + 19}" class="cycle-missing">${escape(reason(view.season?.status))}</text>`;
        const markerKey = row.id === 'chill' ? 'chill' : row.id === 'buds' ? 'budbreak' : null;
        const marker = markerKey ? view.offset(markerKey) : null;
        return `<g class="cycle-lane${on ? ' is-selected' : ''}" data-cycle-lane="${row.id}">
          <title>${row.title}: ${available ? `${date(view.anchor, row.span[0])} to ${date(view.anchor, row.span[1])}` : 'Unavailable'}</title>
          <rect x="0" y="${y - 10}" width="${right + 206}" height="46" rx="5" class="cycle-row-highlight"/>
          <text x="12" y="${y + 8}" class="cycle-row-title">${row.title}</text><text x="12" y="${y + 27}" class="cycle-row-subtitle">${escape(row.subtitle)}</text>
          ${broad && row.id !== 'chill' ? `<rect x="${x(row.spread[0])}" y="${y}" width="${Math.max(2, x(row.spread[1] + 1) - x(row.spread[0]))}" height="28" rx="4" class="cycle-spread"/>` : ''}${track}
          ${finite(marker) ? `<path d="M ${x(marker)} ${y - 5} v 35" class="cycle-marker"/><circle cx="${x(marker)}" cy="${y - 6}" r="3" class="cycle-marker-dot"><title>${markerKey === 'chill' ? 'Requirement reached' : 'Budbreak'}: ${date(view.anchor, marker)}</title></circle>` : ''}
          <text x="${right + 20}" y="${y + 17}" class="cycle-lane-summary">${escape(laneSummary(p, view, row))}</text>
        </g>`;
      }).join('')}</svg>`;
  }

  function metricsFor(id, p) {
    return p.metric_catalog.filter(m => m.stage === id && m.key !== 'warm_midwinter_hours');
  }

  function metricSummary(p, key) {
    return p.risks.exposures[key] ?? p[key];
  }

  function winterContext(p, view) {
    const m = p.metric_catalog.find(metric => metric.key === 'warm_midwinter_hours');
    if (!m) return '';
    const s = metricSummary(p, m.key), value = view.season ? view.season[m.key] : s?.mean;
    const window = view.season?.warm_midwinter_window;
    const assessment = p.risks.by_id.warm_midwinter;
    return `<section class="winter-context" aria-labelledby="winter-context-title"><div><span class="stamp">Independent winter context</span><h3 id="winter-context-title">${escape(m.label)}</h3><p class="winter-value">${number(value, 1)}${finite(value) ? ` ${escape(m.unit)}` : ''}</p></div>
      <div><p>${escape(m.note)}</p><p>${window ? `${escape(window[0])} to ${escape(window[1])}, inclusive. UTC.` : 'Exact UTC windows appear in the per-winter record.'}</p><p>${view.season ? escape(view.season.issues?.[m.key] || 'This winter only; independent of chill fulfilment and crop-stage dates.') : `Mean across ${s?.n ?? 0} valid winters. p10 to p90 ${number(s?.p10)} to ${number(s?.p90)} ${escape(m.unit)}.`}</p>${assessment ? `<p>${escape(eligibilityLabel[assessment.eligibility])}. ${escape(assessment.reason)}</p><p>${sourceLinks(assessment.evidence)}</p>` : ''}</div></section>`;
  }

  function detail(p, view, selected, hypothetical) {
    const stage = view.rows.find(row => row.id === selected), a = p.assumptions;
    const available = stage.span.every(finite) && stage.span[1] >= stage.span[0];
    const metrics = metricsFor(selected, p);
    const events = Object.values(p.risks.by_id).filter(r => r.risk !== 'warm_midwinter' && (r.stage === selected || metrics.some(m => m.key in r.exposure)));
    const cells = metrics.map(({ key, label, unit, note }) => {
      const s = metricSummary(p, key), value = view.season ? (key in view.season ? view.season[key] : view.season.metrics?.[key]) : s?.mean;
      const coverage = view.season ? (view.season.issues?.[key] || (!finite(value) ? 'No usable value for this winter.' : 'This winter, in its own analysis window.'))
        : `Mean across ${s?.n ?? 0} valid winters. Historical p10 to p90: ${number(s?.p10)} to ${number(s?.p90)} ${unit}.`;
      return `<div class="cycle-metric"><dt>${escape(label)}</dt><dd>${number(value, 2)}${finite(value) ? ` <span>${escape(unit)}</span>` : ''}</dd><p>${escape(note)}</p><p class="cycle-coverage">${escape(coverage)}</p></div>`;
    }).join('');
    const assessments = events.map(event => `<div class="cycle-frequency"><h4>${escape(event.label)}</h4><p>${escape(event.event_definition ?? 'No event threshold is assigned.')}</p>
      ${finite(event.years_with_event) && finite(event.frequency) ? `<strong>${event.years_with_event}<small> / ${event.valid_years} valid winters</small></strong><p>${number(event.frequency * 100, 2)}% historical frequency${event.ci95 ? `; 95% Wilson CI ${number(event.ci95[0] * 100, 2)}% to ${number(event.ci95[1] * 100, 2)}%` : ''}. ${event.total_years} total winters.</p>` : `<p>Event frequency not assigned. ${event.valid_years} valid exposure winters out of ${event.total_years}.</p>`}
      <p><strong class="cycle-eligibility">${escape(eligibilityLabel[event.eligibility])}</strong> ${escape(event.reason)}</p><p class="evidence-sources">${sourceLinks(event.evidence)}</p>${view.season ? '<p>Ranking and frequency summarize historical winters; the metric values shown alongside belong only to the selected winter.</p>' : ''}</div>`).join('');
    const budNote = selected === 'buds' ? `<div class="cycle-explanation"><p>After ${a.chill_requirement_hours} chill hours, the model adds warmth until ${a.gdd_to_budbreak} °C·d above ${a.gdd_base_c}°C is reached.</p><p>Assumed budbreak: ${date(view.anchor, view.offset('budbreak'), !!view.season)}. Flowering starts ${a.flowering_after_budbreak_days[0]} days later.</p><p>No separate bud-stage risk metric is available. These are timing assumptions, not observed plant stages.</p></div>` : '';
    return `<div class="cycle-detail-intro"><div class="cycle-detail-heading"><span class="stamp">${view.season ? `Winter ${view.season.winter_year}` : 'Historical stage exposure'}${hypothetical ? ' / Hypothetical calendar' : ''}</span><h3 id="cycle-detail-title">${stage.title}</h3><p>${available ? `${hypothetical ? 'Hypothetical' : view.season ? 'Modelled' : 'Median'} window · ${date(view.anchor, stage.span[0], !!view.season)} to ${date(view.anchor, stage.span[1], !!view.season)}` : escape(reason(view.season?.status))}</p></div>
      ${view.season && view.season.status !== 'complete' ? `<p class="cycle-notice">${escape(reason(view.season.status))}. Missing values are not zero exposure.</p>` : ''}
      ${assessments}${budNote}</div><dl class="cycle-metrics">${cells}</dl>
      ${selected === 'harvest' ? '<p class="cycle-footnote">Compare rainfall totals and day counts, not event frequency alone.</p>' : ''}
      ${selected === 'whole' ? '<p class="cycle-footnote">Whole-cycle totals do not identify the dates on which dry spells or radiation extremes occurred.</p>' : ''}`;
  }

  function mount(root, p, context) {
    const reference = document.createElement('details');
    reference.className = 'cycle-reference';
    const summary = document.createElement('summary');
    summary.textContent = 'Detailed calendar, system rules, exposure tables and assumptions';
    reference.append(summary);
    const tables = root.querySelector('.production-reference');
    reference.append(tables);
    root.append(reference);
    const panel = document.createElement('section');
    panel.className = 'cycle-panel';
    panel.setAttribute('aria-labelledby', 'cycle-heading');
    const hypothetical = !p.classification?.multi_feature?.majority || p.classification.multi_feature.majority === 'Evergreen';
    const unsupported = hypothetical || !p.seasons.length;
    panel.innerHTML = `<header class="cycle-header"><div><span class="stamp">${escape(context.site)} / Seasonal exposure</span><h3 id="cycle-heading">${unsupported ? 'Winter context and hypothetical stage exposures' : 'The bearing-plant cycle'}</h3><p>Select a winter and stage to read its weather exposures.</p></div><label class="cycle-view-label">View winter<select id="cycle-winter"><option value="typical">Historical summary · ${escape(p.years.join(' to '))}</option>${p.seasons.map(row => `<option value="${row.winter_year}">Winter ${row.winter_year}${row.status !== 'complete' ? ' · incomplete' : ''}</option>`).join('')}</select></label></header>
      <div class="cycle-scope"><span>${escape(p.profile)} · ${p.assumptions.chill_requirement_hours} h requirement · UTC</span><span>${escape(p.classification?.multi_feature?.majority ?? 'Unclassified')} hypothesis · open field + ground · unvalidated</span></div>
      ${unsupported ? '<p class="cycle-notice">A chill-triggered bearing calendar is not applicable here. Evergreen production needs a management anchor; an unclassified result has no supported crop calendar. Any retained crop-stage values below are hypothetical, not applicable risk labels. Winter warm-hour context remains independent.</p>' : ''}
      <div class="cycle-winter-context"></div>
      ${context.system !== 'open_ground' ? '<p class="cycle-notice">Showing the open-field baseline. No tunnel or pot adjustment is applied.</p>' : ''}
      <div class="cycle-layout"><div class="cycle-chart-side"><div class="cycle-stage-controls" role="group" aria-label="Explore a stage">${stages.map(stage => `<button type="button" data-cycle-stage="${stage.id}" aria-pressed="${stage.id === 'flower'}" aria-controls="cycle-detail">${stage.title}</button>`).join('')}</div>
      <div class="cycle-scroll" tabindex="0" role="region" aria-label="Monthly growing-cycle scale. Scroll horizontally on small screens."${unsupported ? ' hidden' : ''}></div>
      <p class="cycle-scroll-hint"${unsupported ? ' hidden' : ''}>Scroll sideways to see the full scale and exposure summaries.</p>
      <div class="cycle-legend"${unsupported ? ' hidden' : ''}><span><i class="cycle-key-solid"></i>Analysis window</span><span class="cycle-spread-key"><i class="cycle-key-spread"></i>p10 start to p90 end</span><span><i class="cycle-key-marker"></i>Chill fulfilled / budbreak</span></div><p class="cycle-chart-note"${unsupported ? ' hidden' : ''}></p></div>
      <aside id="cycle-detail" class="cycle-detail" aria-labelledby="cycle-detail-title" aria-live="polite" aria-atomic="true"></aside></div>
      <footer class="cycle-footer">Bar length shows time, not severity. Weather totals are evaluated inside each modelled stage; exact event dates are not available here. Zero recorded events does not establish safety.</footer>`;
    root.insertBefore(panel, reference);
    let selected = stages.some(stage => stage.id === context.view?.stage) ? context.view.stage : 'flower';
    const selector = panel.querySelector('#cycle-winter');
    if (context.view?.winter === 'typical' || p.seasons.some(row => String(row.winter_year) === context.view?.winter)) selector.value = context.view.winter;
    function update() {
      const view = model(p, selector.value);
      panel.dataset.winter = selector.value;
      panel.dataset.stage = selected;
      if (!unsupported) panel.querySelector('.cycle-scroll').innerHTML = diagram(view, selected, p);
      panel.querySelector('.cycle-winter-context').innerHTML = winterContext(p, view);
      panel.querySelector('.cycle-detail').innerHTML = detail(p, view, selected, hypothetical);
      panel.querySelector('.cycle-spread-key').hidden = !!view.season;
      panel.querySelector('.cycle-chart-note').textContent = view.season
        ? 'Dates and totals belong to this winter. Stage dates are modelled, not observed. The year label refers to the winter, not necessarily the harvest year.'
        : 'Solid bars use median stage boundaries. Outlines span the 10th-percentile start to the 90th-percentile end across valid winters; they are timing spread, not confidence limits or a single observed season.';
      panel.querySelectorAll('[data-cycle-stage]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.cycleStage === selected)));
    }
    panel.addEventListener('click', event => {
      const control = event.target.closest('[data-cycle-stage], [data-cycle-lane]');
      if (!control) return;
      selected = control.dataset.cycleStage || control.dataset.cycleLane;
      update();
    });
    selector.addEventListener('change', update);
    update();
  }

  return { mount };
})();
