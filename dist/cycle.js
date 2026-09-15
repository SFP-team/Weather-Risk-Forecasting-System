'use strict';

// Presentation only. Dates, assumptions and exposures come from the production result.
// Bar length represents time, never risk severity or the dates of weather events.
const CycleView = (() => {
  const DAY = 86400000;
  const stages = [
    { id: 'chill', title: 'Winter chill', subtitle: 'Cold-hour requirement', event: 'chill_shortfall' },
    { id: 'buds', title: 'Bud development', subtitle: 'Warmth after chill' },
    { id: 'flower', title: 'Flowering', subtitle: 'Freeze & wet weather', event: 'flowering_freeze' },
    { id: 'fruit', title: 'Fruit development', subtitle: 'Heat exposure', event: 'fruit_severe_heat' },
    { id: 'harvest', title: 'Harvest', subtitle: 'Rain & wet weather', event: 'harvest_heavy_rain' },
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
    if (row.id === 'whole') {
      const value = view.season ? view.season.metrics?.production_max_dry_days : p.risks.unranked_exposures.production_max_dry_days?.median;
      return finite(value) ? `${number(value)} d dry spell${view.season ? '' : ' · median'}` : 'Dry spell unavailable';
    }
    const event = p.risks.ranked.find(r => r.risk === row.event);
    const a = p.assumptions;
    const labels = { chill: `<${a.chill_requirement_hours} h`, flower: `≤${a.damaging_flower_freeze_c}°C`, fruit: `≥${a.severe_heat_threshold_c}°C`, harvest: `≥${a.heavy_rain_mm} mm` };
    if (!view.season) return event?.valid_years ? `${event.years_with_event}/${event.valid_years} winters · ${labels[row.id]}` : 'Exposure unavailable';
    if (row.id === 'chill') return finite(view.season.chill_hours)
      ? `${number(view.season.chill_hours, 0)} h / ${p.assumptions.chill_requirement_hours} h required` : 'Chill unavailable';
    const key = { flower: 'flower_freeze_days', fruit: 'fruit_severe_heat_days', harvest: 'harvest_heavy_rain_days' }[row.id];
    const value = view.season.metrics?.[key];
    return finite(value) ? `${number(value)} days · ${labels[row.id]}` : 'Exposure unavailable';
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
    const a = p.assumptions;
    const disease = `Days meeting the assumed ${a.disease_temp_min_c} to ${a.disease_temp_max_c}°C, RH ≥${a.disease_rh_threshold}% and rain ≥${a.disease_rain_threshold_mm} mm rule. Not measured disease.`;
    switch (id) {
      case 'chill': return [['chill_hours', 'Accumulated chill', 'h', 'Across the full six-month winter, not just until the requirement is reached.'], ['freeze_hours', 'Freezing exposure', 'h', `Winter hours at or below ${a.frost_threshold_c}°C.`]];
      case 'flower': return [['flower_freeze_days', 'Cold exposure', 'days', `Daily minimum ≤${a.damaging_flower_freeze_c}°C during assumed flowering.`], ['flowering_rain_mm', 'Flowering rainfall', 'mm', 'Total rain over the assumed flowering window.'], ['flowering_disease_days', 'Disease-favourable weather', 'days', disease], ['flowering_vpd_mean_kpa', 'Air drying demand', 'kPa', 'Mean vapour pressure deficit, derived from daily temperature and humidity.']];
      case 'fruit': return [['fruit_heat_days', 'Heat exposure', 'days', `Daily maximum ≥${a.heat_threshold_c}°C during fruit development.`], ['fruit_severe_heat_days', 'Higher heat exposure', 'days', `Daily maximum ≥${a.severe_heat_threshold_c}°C during fruit development.`], ['fruit_vpd_mean_kpa', 'Air drying demand', 'kPa', 'Mean vapour pressure deficit. No irrigation or plant-water model is applied.']];
      case 'harvest': return [['harvest_rain_mm', 'Harvest rainfall', 'mm', 'Total rain over the assumed harvest window.'], ['harvest_heavy_rain_days', 'Heavy-rain days', 'days', `Daily rainfall ≥${a.heavy_rain_mm} mm.`], ['harvest_disease_days', 'Disease-favourable weather', 'days', disease], ['harvest_vpd_mean_kpa', 'Air drying demand', 'kPa', 'Mean vapour pressure deficit during harvest.']];
      case 'whole': return [['production_max_dry_days', 'Longest dry spell', 'days', `Longest run of days with rain <${a.dry_day_mm} mm, from winter start through harvest. Not measured drought.`], ['production_radiation_mean_mj', 'Daily solar energy', 'MJ/m²/day', 'Mean daily shortwave radiation across the cycle.'], ['production_gdd', 'Accumulated warmth', '°C·d', `Heat units above ${a.gdd_base_c}°C across the cycle. Not a heat-damage score.`]];
      default: return [];
    }
  }

  function metricSummary(p, key) {
    if (p[key]) return p[key];
    return p.risks.unranked_exposures[key] || p.risks.ranked.find(r => r.exposure[key])?.exposure[key];
  }

  function detail(p, view, selected) {
    const stage = view.rows.find(row => row.id === selected), a = p.assumptions;
    const available = stage.span.every(finite) && stage.span[1] >= stage.span[0];
    const event = p.risks.ranked.find(r => r.risk === stage.event);
    const eventTitle = { chill: `Winter below ${a.chill_requirement_hours} chill hours`, flower: `At least one day ≤${a.damaging_flower_freeze_c}°C`, fruit: `At least one day ≥${a.severe_heat_threshold_c}°C`, harvest: `At least one day with ≥${a.heavy_rain_mm} mm rain` }[selected];
    const cells = metricsFor(selected, p).map(([key, title, unit, note]) => {
      const s = metricSummary(p, key), value = view.season ? (key in view.season ? view.season[key] : view.season.metrics?.[key]) : s?.mean;
      const coverage = view.season ? (view.season.issues?.[key] || (!finite(value) ? 'No usable value for this winter.' : 'This winter, in the analysis window.'))
        : `Mean across ${s?.n ?? 0} valid winters. Historical p10 to p90: ${number(s?.p10)} to ${number(s?.p90)} ${unit}.`;
      return `<div class="cycle-metric"><dt>${escape(title)}</dt><dd>${number(value, 2)}${finite(value) ? ` <span>${escape(unit)}</span>` : ''}</dd><p>${escape(note)}</p><p class="cycle-coverage">${escape(coverage)}</p></div>`;
    }).join('');
    const count = event?.valid_years || 0;
    const frequency = !view.season && count ? `<div class="cycle-frequency"><span>${escape(eventTitle)}</span><strong>${event.years_with_event}<small> / ${count} winters</small></strong><div class="cycle-year-marks" aria-hidden="true">${Array.from({ length: count }, (_, i) => `<i class="${i < event.years_with_event ? 'occurred' : ''}"></i>`).join('')}</div><p>${number(event.frequency * 100, 0)}% historical frequency${event.ci95 ? `; 95% Wilson interval ${number(event.ci95[0] * 100, 0)}% to ${number(event.ci95[1] * 100, 0)}%` : ''}. Each square is one valid winter, grouped by outcome, not chronology. Not a probability of crop loss.</p></div>` : '';
    const budNote = selected === 'buds' ? `<div class="cycle-explanation"><p>After ${a.chill_requirement_hours} chill hours, the model adds warmth until ${a.gdd_to_budbreak} °C·d above ${a.gdd_base_c}°C is reached.</p><p><strong>Assumed budbreak: ${date(view.anchor, view.offset('budbreak'), !!view.season)}.</strong> Flowering starts ${a.flowering_after_budbreak_days[0]} days later.</p><p>No separate bud-stage risk metric is available. These are timing assumptions, not observed plant stages.</p></div>` : '';
    return `<div class="cycle-detail-intro"><div class="cycle-detail-heading"><span class="stamp">${view.season ? `Winter ${view.season.winter_year}` : 'Historical stage exposure'}</span><h3 id="cycle-detail-title">${stage.title}</h3><p>${available ? `${view.season ? 'Modelled' : 'Median'} window · ${date(view.anchor, stage.span[0], !!view.season)} to ${date(view.anchor, stage.span[1], !!view.season)}` : escape(reason(view.season?.status))}</p></div>
      ${view.season && view.season.status !== 'complete' ? `<p class="cycle-notice">${escape(reason(view.season.status))}. Missing values are not zero exposure.</p>` : ''}
      ${frequency}</div>${budNote}<dl class="cycle-metrics">${cells}</dl>
      ${selected === 'harvest' ? '<p class="cycle-footnote">A heavy-rain day is common at humid sites. Compare rainfall totals and day counts, not frequency alone.</p>' : ''}
      ${selected === 'whole' ? '<p class="cycle-footnote">The bar marks the analysis window. These totals do not tell us on which dates dry spells or radiation extremes occurred.</p>' : ''}`;
  }

  function mount(root, p, context) {
    const reference = document.createElement('details');
    reference.className = 'cycle-reference';
    const summary = document.createElement('summary');
    summary.textContent = 'Detailed calendar, system rules, exposure tables and assumptions';
    reference.append(summary);
    while (root.firstChild) reference.append(root.firstChild);
    root.append(reference);
    const panel = document.createElement('section');
    panel.className = 'cycle-panel';
    panel.setAttribute('aria-labelledby', 'cycle-heading');
    const unsupported = p.classification?.multi_feature?.majority === 'Evergreen' || !p.seasons?.length;
    if (unsupported) {
      panel.innerHTML = '<h3 id="cycle-heading">Growing-cycle timeline unavailable</h3><p>A chill-triggered calendar is not supported for this result. An evergreen cycle needs a management anchor; no dates have been invented.</p>';
      root.prepend(panel);
      return;
    }
    panel.innerHTML = `<header class="cycle-header"><div><span class="stamp">${escape(context.site)} / Seasonal exposure</span><h3 id="cycle-heading">The growing cycle, at a glance.</h3><p>Follow the season. Select a stage to see its weather exposures.</p></div><label class="cycle-view-label">View cycle<select id="cycle-winter"><option value="typical">Typical cycle · ${escape(p.years.join(' to '))}</option>${p.seasons.map(row => `<option value="${row.winter_year}">Winter ${row.winter_year}${row.status !== 'complete' ? ' · incomplete' : ''}</option>`).join('')}</select></label></header>
      <div class="cycle-scope"><span>${escape(p.profile)} · ${p.assumptions.chill_requirement_hours} h requirement · UTC</span><span>${escape(p.classification.multi_feature.majority ?? 'Unclassified')} hypothesis · open field + ground · unvalidated</span></div>
      ${context.system !== 'open_ground' ? '<p class="cycle-notice">Showing the open-field baseline. No tunnel or pot adjustment is applied.</p>' : ''}
      <div class="cycle-layout"><div class="cycle-chart-side"><div class="cycle-stage-controls" role="group" aria-label="Explore a stage">${stages.map(stage => `<button type="button" data-cycle-stage="${stage.id}" aria-pressed="${stage.id === 'flower'}" aria-controls="cycle-detail">${stage.title}</button>`).join('')}</div>
      <div class="cycle-scroll" tabindex="0" role="region" aria-label="Monthly growing-cycle scale. Scroll horizontally on small screens."></div>
      <p class="cycle-scroll-hint">Scroll sideways to see the full scale and exposure summaries.</p>
      <div class="cycle-legend"><span><i class="cycle-key-solid"></i>Analysis window</span><span class="cycle-spread-key"><i class="cycle-key-spread"></i>p10 start to p90 end</span><span><i class="cycle-key-marker"></i>Chill fulfilled / budbreak</span></div><p class="cycle-chart-note"></p></div>
      <aside id="cycle-detail" class="cycle-detail" aria-labelledby="cycle-detail-title" aria-live="polite" aria-atomic="true"></aside></div>
      <footer class="cycle-footer">Bar length shows time, not severity. Weather totals are evaluated inside each modelled stage; exact event dates are not available here. Zero recorded events does not establish safety.</footer>`;
    root.prepend(panel);
    let selected = 'flower';
    const selector = panel.querySelector('#cycle-winter');
    function update() {
      const view = model(p, selector.value);
      panel.dataset.winter = selector.value;
      panel.dataset.stage = selected;
      panel.querySelector('.cycle-scroll').innerHTML = diagram(view, selected, p);
      panel.querySelector('.cycle-detail').innerHTML = detail(p, view, selected);
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
