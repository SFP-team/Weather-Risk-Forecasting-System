/* Reviewed regional evidence from published industry reports.
 * The library is a static same-origin file. Nothing here reads weather results,
 * requests source documents or sends the selected location anywhere.
 */
window.RegionalEvidence = (() => {
  'use strict';

  const dataURL = new URL('evidence/ibo-regional-v1.json', document.currentScript?.src || document.baseURI);
  const timeoutMs = 15000;
  const kinds = ['practice', 'event', 'constraint'];
  const topics = ['harvest', 'management', 'weather', 'resources'];
  const precisions = ['day', 'month', 'season', 'reported_practice'];
  const evidenceTypes = ['association_report', 'industry_narrative', 'interview_estimate'];
  const categories = [
    ['all', 'All'],
    ['harvest', 'Harvest'],
    ['management', 'Management'],
    ['weather', 'Weather events'],
    ['resources', 'Resources'],
  ];
  const kindLabels = {event: 'Reported event', practice: 'Reported practice', constraint: 'Reported constraint'};
  const topicLabels = {harvest: 'Harvest', management: 'Management', weather: 'Weather event', resources: 'Resources'};
  const evidenceLabels = {
    association_report: 'Grower or industry association report',
    industry_narrative: 'Industry narrative',
    interview_estimate: 'Interview estimate',
  };
  const reportNote = 'These items are paraphrased from published industry reports and checked against the cited pages. They are reports, not model output. They are separate from the computed weather risk frequencies, which are calculated from the weather record for this pin.';
  const eventNote = 'Reported occurrence in the source. Not a modelled recurrence, forecast or farm-level loss at this pin.';
  let loading;
  let idCounter = 0;

  // Matches the place-name normalization: accents, case and punctuation only.
  const normalize = value => String(value || '').normalize('NFD').replace(/\p{M}/gu, '')
    .toLowerCase().replace(/[.'’]/g, '').replace(/[^\p{L}\p{N}]+/gu, ' ').trim();

  const isObject = value => value !== null && typeof value === 'object' && !Array.isArray(value);
  const isText = value => typeof value === 'string' && value.trim() !== '';
  const isPage = value => Number.isInteger(value) && value > 0;
  const isoDate = value => {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    const [y, m, d] = value.split('-').map(Number);
    const date = new Date(Date.UTC(y, m - 1, d));
    return date.getUTCFullYear() === y && date.getUTCMonth() === m - 1 && date.getUTCDate() === d;
  };
  const safeURL = value => {
    if (typeof value !== 'string') return null;
    try {
      const url = new URL(value);
      return url.protocol === 'https:' && !url.username && !url.password ? url.href : null;
    } catch {
      return null;
    }
  };
  const plain = value => JSON.parse(JSON.stringify(value));
  const freeze = value => {
    if (value && typeof value === 'object') {
      Object.values(value).forEach(freeze);
      Object.freeze(value);
    }
    return value;
  };

  function validate(data) {
    const fail = where => { throw new Error(`Regional evidence library is malformed (${where}).`); };
    const textList = (list, where, allowEmpty) => {
      if (!Array.isArray(list) || (!allowEmpty && !list.length) || !list.every(isText)) fail(where);
    };
    const pageList = (list, where, allowEmpty, max) => {
      if (!Array.isArray(list) || (!allowEmpty && !list.length) || !list.every(isPage)) fail(where);
      if (max && list.some(page => page > max)) fail(where);
    };
    if (!isObject(data) || data.schema_version !== 1) fail('schema_version');
    for (const key of ['version', 'scope_note', 'coverage_note']) if (!isText(data[key])) fail(key);
    if (!isoDate(data.reviewed_on)) fail('reviewed_on');
    for (const key of ['sources', 'geographies', 'records']) if (!Array.isArray(data[key])) fail(key);
    const reference = data.geography_reference;
    if (!isObject(reference) || typeof reference.sha256 !== 'string'
      || !/^[0-9a-f]{64}$/i.test(reference.sha256) || !isObject(reference.region_ids)) fail('geography_reference');

    const sources = new Map();
    data.sources.forEach((source, i) => {
      const where = `sources[${i}]`;
      if (!isObject(source) || !isText(source.id) || sources.has(source.id)) fail(`${where}.id`);
      for (const key of ['title', 'source_family', 'attribution']) if (!isText(source[key])) fail(`${where}.${key}`);
      if (!Number.isInteger(source.edition)) fail(`${where}.edition`);
      if (!safeURL(source.url)) fail(`${where}.url`);
      if (typeof source.sha256 !== 'string' || !/^[0-9a-f]{64}$/i.test(source.sha256)) fail(`${where}.sha256`);
      if (!isPage(source.pdf_pages)) fail(`${where}.pdf_pages`);
      if (!isObject(source.license) || !isText(source.license.label)) fail(`${where}.license`);
      pageList(source.license.printed_pages, `${where}.license.printed_pages`, true);
      pageList(source.license.pdf_pages, `${where}.license.pdf_pages`, true, source.pdf_pages);
      sources.set(source.id, source);
    });

    const geographies = new Set();
    data.geographies.forEach((geo, i) => {
      const where = `geographies[${i}]`;
      if (!isObject(geo) || !isText(geo.id) || geographies.has(geo.id)) fail(`${where}.id`);
      for (const key of ['country_code', 'label']) if (!isText(geo[key])) fail(`${where}.${key}`);
      textList(geo.country_names, `${where}.country_names`, false);
      textList(geo.region_names, `${where}.region_names`, true);
      if (geo.precision === 'region' ? !geo.region_names.length
        : geo.precision !== 'country' || geo.region_names.length) fail(`${where}.precision`);
      if (geo.precision === 'region') {
        const ids = reference.region_ids[geo.id];
        if (!Array.isArray(ids) || !ids.length || !ids.every(id => Number.isInteger(id) && id >= 0)) fail(`${where}.region_ids`);
      }
      geographies.add(geo.id);
    });

    const records = new Set();
    data.records.forEach((record, i) => {
      const where = `records[${i}]`;
      if (!isObject(record) || !isText(record.id) || records.has(record.id)) fail(`${where}.id`);
      if (!kinds.includes(record.kind)) fail(`${where}.kind`);
      if (!topics.includes(record.topic)) fail(`${where}.topic`);
      for (const key of ['title', 'summary', 'crop_context', 'review_status', 'source_family']) {
        if (!isText(record[key])) fail(`${where}.${key}`);
      }
      if (!evidenceTypes.includes(record.evidence_type)) fail(`${where}.evidence_type`);
      if (!Array.isArray(record.geography_ids) || !record.geography_ids.length
        || !record.geography_ids.every(id => geographies.has(id))) fail(`${where}.geography_ids`);
      const period = record.period;
      if (!isObject(period) || !isText(period.label) || !precisions.includes(period.precision)) fail(`${where}.period`);
      for (const key of ['start', 'end']) {
        if (period[key] !== null && !isoDate(period[key])) fail(`${where}.period.${key}`);
      }
      if (period.start && period.end && period.end < period.start) fail(`${where}.period.end`);
      if (period.precision === 'reported_practice' ? period.start || period.end
        : period.precision === 'day' && (!period.start || !period.end)) fail(`${where}.period.precision`);
      if (record.event_id !== null && !isText(record.event_id)) fail(`${where}.event_id`);
      if (record.kind === 'event' && record.event_id === null) fail(`${where}.event_id`);
      if (!Array.isArray(record.citations) || !record.citations.length) fail(`${where}.citations`);
      record.citations.forEach((citation, j) => {
        const at = `${where}.citations[${j}]`;
        if (!isObject(citation) || !sources.has(citation.source_id)) fail(`${at}.source_id`);
        pageList(citation.printed_pages, `${at}.printed_pages`, true);
        pageList(citation.pdf_pages, `${at}.pdf_pages`, false, sources.get(citation.source_id).pdf_pages);
        if (!isText(citation.locator)) fail(`${at}.locator`);
      });
      textList(record.limitations, `${where}.limitations`, true);
      records.add(record.id);
    });
    return freeze(plain(data));
  }

  function load() {
    if (!loading) {
      loading = (async () => {
        if (dataURL.origin !== location.origin) throw new Error('Regional evidence library must be served from this site.');
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), timeoutMs);
        let data;
        try {
          const response = await fetch(dataURL, {credentials: 'same-origin', signal: controller.signal});
          if (!response.ok) throw new Error(`Regional evidence library request failed (HTTP ${response.status}).`);
          data = await response.json();
        } catch (error) {
          if (error?.name === 'AbortError') throw new Error('Regional evidence library request timed out.');
          if (error instanceof SyntaxError) throw new Error('Regional evidence library is not valid JSON.');
          throw error instanceof Error && /^Regional evidence/.test(error.message) ? error
            : new Error('Regional evidence library could not be loaded.');
        } finally {
          clearTimeout(timer);
        }
        return validate(data);
      })();
      // Keep successful loads; allow a later retry after a failure.
      loading.catch(() => { loading = null; });
    }
    return loading;
  }

  const finite = value => Number.isFinite(value) ? value : null;
  const nameOrNull = value => typeof value === 'string' && value.trim() ? value : null;
  const baselineDate = value => {
    if (value instanceof Date && !Number.isNaN(value.getTime())) return value.toISOString().slice(0, 10);
    if (typeof value === 'string' && isoDate(value.slice(0, 10))) return value.slice(0, 10);
    return null;
  };

  function select(registry, place, {baselineEnd} = {}) {
    if (!isObject(registry) || !Array.isArray(registry.records) || !Array.isArray(registry.geographies)
      || !Array.isArray(registry.sources)) {
      throw new TypeError('RegionalEvidence.select needs a loaded registry.');
    }
    const country = nameOrNull(place?.country);
    const region = nameOrNull(place?.region);
    const selection = {
      status: 'pending',
      version: registry.version ?? null,
      reviewed_on: registry.reviewed_on ?? null,
      location: {latitude: finite(place?.lat), longitude: finite(place?.lon), country, region,
        region_id: Number.isInteger(place?.region_id) ? place.region_id : null,
        geography_sha256: place?.geography_sha256 ?? null},
      scope_note: registry.scope_note ?? null,
      coverage_note: registry.coverage_note ?? null,
      reason: '',
      geographies: [],
      records: [],
      sources: [],
      baseline_end: baselineDate(baselineEnd ?? null),
    };
    if (!place || place.status === 'pending') {
      selection.reason = 'Waiting for the map boundary lookup for this point.';
      return selection;
    }
    if (place.status !== 'resolved' || !country) {
      selection.status = 'unresolved';
      selection.reason = place.status === 'invalid'
        ? 'The coordinates are not valid, so no geographic context was resolved.'
        : place.status === 'unavailable'
          ? 'Boundary data could not be loaded, so the country and region for this point are unknown.'
          : 'This point is not inside a mapped country boundary (it may be on a coast or border). Evidence from another country is never substituted.';
      return selection;
    }
    if (!registry.geography_reference?.sha256 || place.geography_sha256 !== registry.geography_reference.sha256) {
      selection.status = 'unresolved';
      selection.reason = 'The geographic reference does not match this evidence library. No name-only regional match is substituted; weather results remain usable.';
      return selection;
    }

    const countryKey = normalize(country);
    const regionKey = region ? normalize(region) : '';
    const matched = new Map();
    for (const geo of registry.geographies) {
      if (!geo.country_names.some(name => normalize(name) === countryKey)) continue;
      if (geo.precision === 'country') matched.set(geo.id, geo);
      else if (regionKey && registry.geography_reference.region_ids[geo.id]?.includes(place.region_id)
        && geo.region_names.some(name => normalize(name) === regionKey)) matched.set(geo.id, geo);
    }
    const editions = new Map(registry.sources.map(source => [source.id, source.edition]));
    const sortKey = record => record.period.start
      || `${String(Math.max(...record.citations.map(c => editions.get(c.source_id) ?? 0))).padStart(4, '0')}`;
    const regional = [];
    const national = [];
    const seen = new Set();
    for (const record of registry.records) {
      if (record.review_status !== 'source_checked' || seen.has(record.id)) continue;
      const ids = record.geography_ids.filter(id => matched.has(id));
      if (!ids.length) continue;
      seen.add(record.id);
      (ids.some(id => matched.get(id).precision === 'region') ? regional : national).push(record);
    }
    const order = (a, b) => (a.kind === 'event') !== (b.kind === 'event') ? (a.kind === 'event' ? -1 : 1)
      : sortKey(b).localeCompare(sortKey(a)) || a.id.localeCompare(b.id);
    const records = [...regional.sort(order), ...national.sort(order)];
    const place_ = region ? `${region}, ${country}` : country;
    if (!records.length) {
      selection.status = 'no_match';
      selection.reason = `No reviewed evidence for ${place_} is recorded in this library. The library is a curated subset, so this is not evidence that nothing was reported or that risk is low.`;
      return selection;
    }
    const usedGeo = new Set(records.flatMap(record => record.geography_ids.filter(id => matched.has(id))));
    const usedSources = new Set(records.flatMap(record => record.citations.map(c => c.source_id)));
    selection.status = 'available';
    selection.geographies = plain(registry.geographies.filter(geo => usedGeo.has(geo.id)));
    selection.records = plain(records);
    selection.sources = plain(registry.sources.filter(source => usedSources.has(source.id))
      .sort((a, b) => a.edition - b.edition || a.id.localeCompare(b.id)));
    return selection;
  }

  // Rendering uses DOM text nodes only, so every string is escaped.
  const make = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  };
  const uid = name => `regional-${name}-${++idCounter}`;
  const list = value => Array.isArray(value) ? value : [];
  const pageRanges = pages => {
    const sorted = [...new Set(list(pages).filter(isPage))].sort((a, b) => a - b);
    const parts = [];
    for (let i = 0; i < sorted.length; i++) {
      let j = i;
      while (j + 1 < sorted.length && sorted[j + 1] === sorted[j] + 1) j++;
      parts.push(j > i ? `${sorted[i]}–${sorted[j]}` : String(sorted[i]));
      i = j;
    }
    return parts.join(', ');
  };
  const pageText = (printed, pdf) => [
    pageRanges(printed) && `printed p. ${pageRanges(printed)}`,
    pageRanges(pdf) && `PDF p. ${pageRanges(pdf)}`,
  ].filter(Boolean).join('; ');
  const link = (href, text) => {
    const url = safeURL(href);
    if (!url) return make('span', '', text);
    const a = make('a', '', text);
    a.href = url;
    a.rel = 'noopener noreferrer';
    a.target = '_blank';
    a.referrerPolicy = 'no-referrer';
    return a;
  };
  const definition = (dl, term, value) => {
    if (value === null || value === undefined || value === '') return;
    const row = make('div', 'regional-fact');
    row.append(make('dt', '', term));
    const dd = make('dd');
    if (value instanceof Node) dd.append(value); else dd.textContent = String(value);
    row.append(dd);
    dl.append(row);
  };
  const disclosure = (summary, open) => {
    const details = make('details', 'regional-details');
    if (open) details.open = true;
    details.append(make('summary', '', summary));
    return details;
  };

  function baselineState(record, baselineEnd) {
    const start = record?.period?.start;
    const end = record?.period?.end || start;
    if (!baselineEnd || !start || !isoDate(start)) return null;
    if (start > baselineEnd) return `Outside weather baseline (baseline ends ${baselineEnd})`;
    if (end > baselineEnd) return `Partly outside weather baseline (baseline ends ${baselineEnd})`;
    return null;
  }

  function citationList(citations, sources, snapshot) {
    const ul = make('ul', 'regional-citations');
    for (const citation of list(citations)) {
      const source = sources.get(citation?.source_id);
      const li = make('li', 'regional-citation');
      if (!source) {
        li.append(make('span', 'regional-missing', `Source ${citation?.source_id ?? 'unknown'} is not included in this selection.`));
        ul.append(li);
        continue;
      }
      const title = make('strong');
      const target = safeURL(source.url);
      if (target) {
        const url = new URL(target);
        if (url.pathname.toLowerCase().endsWith('.pdf') && citation.pdf_pages?.length) {
          url.hash = `page=${citation.pdf_pages[0]}`;
        }
        title.append(link(url.href, `${source.title} (${source.edition})`));
      } else title.textContent = `${source.title} (${source.edition})`;
      li.append(title);
      const pages = pageText(citation.printed_pages, citation.pdf_pages);
      if (pages) li.append(make('span', 'regional-pages', pages));
      if (citation.locator) li.append(make('span', 'regional-locator', `Section: ${citation.locator}`));
      if (snapshot) li.append(make('span', 'regional-attribution', source.attribution));
      ul.append(li);
    }
    return ul;
  }

  function recordBody(record, sources, snapshot, headingTag) {
    const fragment = document.createDocumentFragment();
    if (headingTag) fragment.append(make(headingTag, 'regional-subtitle', record.title));
    fragment.append(make('p', 'regional-summary', record.summary));
    const dl = make('dl', 'regional-facts');
    definition(dl, 'Period', record.period?.label);
    definition(dl, 'Crop context', record.crop_context);
    definition(dl, 'Evidence type', evidenceLabels[record.evidence_type] || record.evidence_type);
    fragment.append(dl);
    const limitations = list(record.limitations);
    if (limitations.length) {
      const box = make('div', 'regional-limitations');
      box.append(make('p', 'regional-label', 'Limitations'));
      const ul = make('ul');
      limitations.forEach(text => ul.append(make('li', '', text)));
      box.append(ul);
      fragment.append(box);
    }
    const sourcesBox = disclosure(`Cited pages (${list(record.citations).length})`, snapshot);
    sourcesBox.append(citationList(record.citations, sources, snapshot));
    fragment.append(sourcesBox);
    return fragment;
  }

  function card(entry, context, sources, baselineEnd, snapshot) {
    const [record, ...others] = entry.records;
    const article = make('article', 'regional-card');
    article.dataset.topic = record.topic;
    article.dataset.kind = record.kind;
    const titleId = uid('card');
    article.setAttribute('aria-labelledby', titleId);

    const tags = make('p', 'regional-tags');
    tags.append(make('span', `regional-tag regional-kind-${record.kind}`, kindLabels[record.kind] || 'Reported item'));
    tags.append(make('span', 'regional-tag', topicLabels[record.topic] || record.topic));
    tags.append(make('span', `regional-tag regional-scope-${context.precision}`,
      context.precision === 'region' ? 'Regional report' : 'Country context'));
    const outside = entry.records.map(item => baselineState(item, baselineEnd)).find(Boolean);
    if (outside) tags.append(make('span', 'regional-tag regional-outside', outside));
    article.append(tags);

    const title = make('h5', 'regional-card-title', record.title);
    title.id = titleId;
    article.append(title);
    if (context.labels.length) {
      article.append(make('p', 'regional-scope', `Report scope: ${context.labels.join('; ')}`));
    }
    if (record.kind === 'event') article.append(make('p', 'regional-event-note', eventNote));
    article.append(recordBody(record, sources, snapshot, null));

    if (others.length) {
      const more = disclosure(`Same event in ${others.length} other reviewed record${others.length === 1 ? '' : 's'}`, snapshot);
      more.append(make('p', 'regional-note', 'Repeated citations of one event share a source family. They are not independent observations.'));
      for (const other of others) {
        const block = make('div', 'regional-related');
        block.append(recordBody(other, sources, snapshot, 'h6'));
        more.append(block);
      }
      article.append(more);
    }
    return article;
  }

  function sourceLibrary(selection, snapshot) {
    const sources = list(selection.sources);
    const details = disclosure(`Source library (${sources.length} report${sources.length === 1 ? '' : 's'})`, snapshot);
    details.classList.add('regional-library');
    const ul = make('ul', 'regional-sources');
    for (const source of sources) {
      const li = make('li', 'regional-source');
      li.append(make('strong', '', `${source.title} (${source.edition})`));
      const dl = make('dl', 'regional-facts');
      definition(dl, 'Attribution', source.attribution);
      const license = source.license || {};
      const licensePages = pageText(license.printed_pages, license.pdf_pages);
      definition(dl, 'Reuse terms', license.label && (licensePages ? `${license.label} (stated on ${licensePages})` : license.label));
      definition(dl, 'Report length', isPage(source.pdf_pages) ? `${source.pdf_pages} PDF pages` : null);
      definition(dl, 'Source family', source.source_family);
      definition(dl, 'SHA-256 of reviewed PDF', source.sha256 ? make('code', 'regional-hash', source.sha256) : null);
      definition(dl, 'Publisher link', safeURL(source.url) ? link(source.url, safeURL(source.url)) : 'No safe link available');
      li.append(dl);
      ul.append(li);
    }
    details.append(ul);
    return details;
  }

  function placeText(location) {
    const country = nameOrNull(location?.country);
    const region = nameOrNull(location?.region);
    return region && country ? `${region}, ${country}` : country || 'this point';
  }

  function render(container, selection, {snapshot = false} = {}) {
    if (!container || typeof container.replaceChildren !== 'function') {
      throw new TypeError('RegionalEvidence.render needs a container element.');
    }
    const data = isObject(selection) ? selection : {status: 'unavailable', reason: 'No evidence selection was provided.'};
    const status = ['available', 'no_match', 'unresolved', 'pending', 'loading', 'unavailable'].includes(data.status)
      ? data.status : 'unavailable';
    const root = make('section', 'regional-evidence');
    root.dataset.status = status;
    if (snapshot) root.dataset.snapshot = 'true';
    const headingId = uid('heading');
    root.setAttribute('aria-labelledby', headingId);

    const head = make('div', 'regional-head');
    const heading = make('h3', 'regional-title', `Regional context for ${placeText(data.location)}`);
    heading.id = headingId;
    head.append(heading);
    const meta = [
      data.version && `Library ${data.version}`,
      data.reviewed_on && `reviewed ${data.reviewed_on}`,
    ].filter(Boolean).join(' · ');
    if (meta) head.append(make('p', 'regional-meta', meta));
    root.append(head);

    const message = make('div', 'regional-status');
    message.setAttribute('role', 'status');
    const reason = typeof data.reason === 'string' && data.reason.trim() ? data.reason : '';
    const where = placeText(data.location);
    const messages = {
      loading: ['Loading the reviewed evidence library…', ''],
      unavailable: ['The regional evidence library is unavailable.', 'Weather results are not affected. No regional evidence is shown rather than guessing.'],
      pending: ['Waiting for the country and region of this point.', 'Evidence is matched only after the map boundary lookup finishes.'],
      unresolved: ['Geographic context cannot be used for regional evidence.', 'Evidence requires a compatible boundary reference and a containing country/region, never a nearby country or a matching place name alone.'],
      no_match: [`No reviewed evidence is recorded for ${where}.`, 'The library is a curated subset of report findings. An empty result is not evidence that events did not occur, and it does not mean low risk.'],
    };
    if (status !== 'available') {
      const [lead, note] = messages[status];
      message.append(make('p', 'regional-lead', lead));
      if (reason) message.append(make('p', 'regional-reason', reason));
      if (note && note !== reason) message.append(make('p', 'regional-note', note));
      root.append(message);
      if (status === 'no_match' || status === 'unresolved') {
        if (data.coverage_note) root.append(make('p', 'regional-coverage', data.coverage_note));
      }
      container.replaceChildren(root);
      return root;
    }

    const sources = new Map(list(data.sources).map(source => [source?.id, source]));
    const geos = new Map(list(data.geographies).map(geo => [geo?.id, geo]));
    const baselineEnd = baselineDate(data.baseline_end);
    // One card per event_id; the first record in selection order is the primary one.
    const entries = [];
    const byEvent = new Map();
    const seenIds = new Set();
    for (const record of list(data.records)) {
      if (!isObject(record) || seenIds.has(record.id)) continue;
      seenIds.add(record.id);
      if (record.event_id && byEvent.has(record.event_id)) {
        byEvent.get(record.event_id).records.push(record);
        continue;
      }
      const entry = {records: [record]};
      if (record.event_id) byEvent.set(record.event_id, entry);
      entries.push(entry);
    }
    const contextOf = entry => {
      const matched = entry.records.flatMap(record => list(record.geography_ids)).map(id => geos.get(id)).filter(Boolean);
      const unique = [...new Map(matched.map(geo => [geo.id, geo])).values()];
      const regional = unique.filter(geo => geo.precision === 'region');
      const chosen = regional.length ? regional : unique;
      return {precision: regional.length ? 'region' : 'country', labels: chosen.map(geo => geo.label)};
    };
    const groups = {region: [], country: []};
    for (const entry of entries) {
      const context = contextOf(entry);
      groups[context.precision].push(card(entry, context, sources, baselineEnd, snapshot));
    }
    const recordCount = seenIds.size;
    const editions = [...new Set(list(data.sources).map(source => source?.edition).filter(Number.isInteger))].sort();
    message.append(make('p', 'regional-lead',
      `${entries.length} reviewed item${entries.length === 1 ? '' : 's'}`
      + ` (${groups.region.length} regional, ${groups.country.length} country context)`));
    message.append(make('p', 'regional-note',
      `${recordCount} source-checked record${recordCount === 1 ? '' : 's'}`
      + (editions.length ? ` from report edition${editions.length === 1 ? '' : 's'} ${editions.join(', ')}.` : '.')));
    root.append(message);

    const notes = make('div', 'regional-notes');
    notes.append(make('p', '', 'Regional reports, not observations at this pin. Weather calculations are unchanged.'));
    const coverage = disclosure('Coverage and interpretation', snapshot);
    coverage.append(make('p', '', reportNote));
    if (data.coverage_note) coverage.append(make('p', 'regional-coverage', data.coverage_note));
    if (data.scope_note) coverage.append(make('p', '', data.scope_note));
    if (baselineEnd) coverage.append(make('p', '', `Where date bounds are known, items beyond ${baselineEnd} are labelled. Read the period and limitations for season-only or undated accounts; no date-by-date weather match is implied.`));
    notes.append(coverage);
    root.append(notes);

    const live = make('p', 'regional-filter-status');
    const empty = make('p', 'regional-empty', '');
    empty.hidden = true;
    if (!snapshot) {
      const filter = make('div', 'regional-filter');
      filter.setAttribute('role', 'group');
      filter.setAttribute('aria-label', 'Filter regional evidence by category');
      live.setAttribute('aria-live', 'polite');
      const cards = [...groups.region, ...groups.country];
      const buttons = [];
      const apply = key => {
        let shown = 0;
        for (const element of cards) {
          const visible = key === 'all' || element.dataset.topic === key;
          element.hidden = !visible;
          if (visible) shown++;
        }
        for (const section of root.querySelectorAll('.regional-group')) {
          section.hidden = ![...section.querySelectorAll('.regional-card')].some(element => !element.hidden);
        }
        buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.category === key)));
        const label = categories.find(([value]) => value === key)[1];
        live.textContent = key === 'all' ? `Showing all ${cards.length} items.` : `Showing ${shown} of ${cards.length} items: ${label}.`;
        empty.hidden = shown > 0;
        empty.textContent = shown ? '' : `No records in the ${label.toLowerCase()} category for this location. This does not indicate low risk.`;
      };
      for (const [key, label] of categories) {
        const count = key === 'all' ? cards.length : cards.filter(element => element.dataset.topic === key).length;
        const button = make('button', 'regional-filter-button', `${label} (${count})`);
        button.type = 'button';
        button.dataset.category = key;
        button.setAttribute('aria-pressed', String(key === 'all'));
        button.addEventListener('click', () => apply(key));
        buttons.push(button);
        filter.append(button);
      }
      root.append(filter);
      live.textContent = `Showing all ${cards.length} items.`;
      root.append(live, empty);
    } else {
      root.append(make('p', 'regional-filter-status', `Snapshot: all ${entries.length} matched items with cited pages shown.`));
    }

    const groupTitles = {
      region: `Regional reports: ${nameOrNull(data.location?.region) || 'matched region'}`,
      country: `Country context: ${nameOrNull(data.location?.country) || 'matched country'}`,
    };
    const groupNotes = {
      region: 'Reports whose stated scope includes the region containing this pin. They describe the region, not this field.',
      country: 'Country-level or other-region reports for this country. Treat as background context, not a regional observation.',
    };
    for (const key of ['region', 'country']) {
      if (!groups[key].length) continue;
      const section = make('section', `regional-group regional-group-${key}`);
      const id = uid('group');
      section.setAttribute('aria-labelledby', id);
      const title = make('h4', 'regional-group-title', groupTitles[key]);
      title.id = id;
      section.append(title, make('p', 'regional-note', groupNotes[key]));
      const grid = make('div', 'regional-cards');
      grid.append(...groups[key]);
      section.append(grid);
      root.append(section);
    }
    root.append(sourceLibrary(data, snapshot));
    container.replaceChildren(root);
    return root;
  }

  return Object.freeze({load, select, render});
})();
