/* Natural Earth reference data is loaded from this site's static geography/ bundle.
 * Selected coordinates are used only in browser memory, never in a name request.
 */
window.PlaceNames = (() => {
  'use strict';

  const dataURL = new URL('geography/places-v1.json.gz', document.currentScript?.src || document.baseURI);
  const radians = Math.PI / 180;
  const earthRadius = 6371.0088;
  const nearLimitKm = 100;
  const epsilon = 1e-6;
  const sourceText = 'Made with Natural Earth. Public domain. Admin boundaries 5.1.1; populated places 5.1.2.';
  const caveat = 'Approximate cartographic context, not an address or legal boundary. Natural Earth uses generalized de facto borders; small islands, coasts and border points may be unresolved or misclassified. Nearest means nearest represented settlement, not necessarily the nearest town. Distances are approximate great-circle distances.';
  let loading;
  let searching;

  const coordinatesValid = (lat, lon) => Number.isFinite(lat) && Number.isFinite(lon)
    && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;
  const coordinateText = (lat, lon) => `${lat.toFixed(4)}°, ${lon.toFixed(4)}°`;

  const normalize = value => String(value || '').normalize('NFD').replace(/\p{M}/gu, '')
    .toLowerCase().replace(/[.'’]/g, '').replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
  async function load() {
    if (!loading) {
      loading = (async () => {
        const response = await fetch(dataURL, {credentials: 'same-origin'});
        if (!response.ok) throw new Error('Geographic reference request failed.');
        const bytes = new Uint8Array(await response.arrayBuffer());
        let data;
        // A server may send the .gz file as bytes or apply Content-Encoding.
        if (bytes[0] === 0x1f && bytes[1] === 0x8b) {
          if (typeof DecompressionStream !== 'function') throw new Error('Gzip decoding is unavailable.');
          const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
          data = await new Response(stream).json();
        } else {
          data = JSON.parse(new TextDecoder().decode(bytes));
        }
        if (data.version !== 1 || !data.entities?.length || !data.areas?.length
          || !data.arcs?.length || !data.places?.length || !data.transform?.scale) {
          throw new Error('Geographic reference format is unsupported.');
        }
        // Decode each shared arc once. Ring tests use its segments directly,
        // so adjacent polygons do not need their own copies of the coordinates.
        const arcs = data.arcs.map(encoded => {
          const decoded = new Int32Array(encoded.length * 2);
          let x = 0;
          let y = 0;
          for (let i = 0; i < encoded.length; i++) {
            x += encoded[i][0];
            y += encoded[i][1];
            decoded[i * 2] = x;
            decoded[i * 2 + 1] = y;
          }
          return decoded;
        });
        const countries = [];
        const regions = Array.from({length: data.country_count}, () => []);
        for (const area of data.areas) {
          if (area[0] < data.country_count) countries.push(area);
          else regions[data.entities[area[0]][1]].push(area);
        }
        const vectors = new Float64Array(data.places.length * 3);
        for (let i = 0; i < data.places.length; i++) {
          const lat = data.places[i][2] * radians;
          const lon = data.places[i][1] * radians;
          const cos = Math.cos(lat);
          vectors[i * 3] = cos * Math.cos(lon);
          vectors[i * 3 + 1] = cos * Math.sin(lon);
          vectors[i * 3 + 2] = Math.sin(lat);
        }
        return {arcs, countries, regions, entities: data.entities, places: data.places,
          vectors, transform: data.transform};
      })().catch(() => null);
    }
    return loading;
  }

  // 0 = outside, 1 = inside, 2 = on a boundary. Arc direction does not affect
  // segment crossing parity, including when TopoJSON uses a reversed arc.
  function ringContains(ring, x, y, arcs) {
    let inside = false;
    for (const index of ring) {
      const arc = arcs[index < 0 ? ~index : index];
      for (let i = 2; i < arc.length; i += 2) {
        const ax = arc[i - 2];
        const ay = arc[i - 1];
        const bx = arc[i];
        const by = arc[i + 1];
        const dx = bx - ax;
        const dy = by - ay;
        if (x >= Math.min(ax, bx) - epsilon && x <= Math.max(ax, bx) + epsilon
          && y >= Math.min(ay, by) - epsilon && y <= Math.max(ay, by) + epsilon
          && Math.abs((x - ax) * dy - (y - ay) * dx) <= epsilon * Math.max(1, Math.abs(dx) + Math.abs(dy))) {
          return 2;
        }
        if ((ay > y) !== (by > y) && x < ax + (y - ay) * dx / dy) inside = !inside;
      }
    }
    return inside ? 1 : 0;
  }

  function polygonContains(rings, x, y, arcs) {
    const outer = ringContains(rings[0], x, y, arcs);
    if (outer !== 1) return outer;
    for (let i = 1; i < rings.length; i++) {
      const hole = ringContains(rings[i], x, y, arcs);
      if (hole === 2) return 2;
      if (hole === 1) return 0;
    }
    return 1;
  }

  // -1 = no containing area; -2 = shared boundary or overlapping entities.
  function containingEntity(areas, x, y, arcs) {
    let match = -1;
    for (const area of areas) {
      const bounds = area[1];
      if (x < bounds[0] - epsilon || x > bounds[2] + epsilon
        || y < bounds[1] - epsilon || y > bounds[3] + epsilon) continue;
      const contains = polygonContains(area[2], x, y, arcs);
      if (contains === 2) return -2;
      if (contains === 1) {
        if (match >= 0 && match !== area[0]) return -2;
        match = area[0];
      }
    }
    return match;
  }

  function locate(areas, x, y, seam, data) {
    if (!seam) return containingEntity(areas, x, y, data.arcs);
    // The data is split at +/-180. Test just inside both artificial seams,
    // rather than mistaking that cut for a national or regional boundary.
    const {scale, translate} = data.transform;
    const west = containingEntity(areas, (-180 - translate[0]) / scale[0] + 1e-4, y, data.arcs);
    const east = containingEntity(areas, (180 - translate[0]) / scale[0] - 1e-4, y, data.arcs);
    if (west === -2 || east === -2 || (west >= 0 && east >= 0 && west !== east)) return -2;
    return west >= 0 ? west : east;
  }

  function nearestPlace(lat, lon, data) {
    const latitude = lat * radians;
    const longitude = lon * radians;
    const cos = Math.cos(latitude);
    const x = cos * Math.cos(longitude);
    const y = cos * Math.sin(longitude);
    const z = Math.sin(latitude);
    let nearest = 0;
    let best = -Infinity;
    for (let i = 0; i < data.places.length; i++) {
      const dot = x * data.vectors[i * 3] + y * data.vectors[i * 3 + 1] + z * data.vectors[i * 3 + 2];
      if (dot > best) {
        best = dot;
        nearest = i;
      }
    }
    const place = data.places[nearest];
    const dlat = (place[2] - lat) * radians;
    const dlon = (place[1] - lon) * radians;
    const a = Math.sin(dlat / 2) ** 2 + cos * Math.cos(place[2] * radians) * Math.sin(dlon / 2) ** 2;
    const distance = 2 * earthRadius * Math.asin(Math.sqrt(Math.min(1, Math.max(0, a))));
    return {name: place[0], distance_km: Math.round(distance * 10) / 10};
  }

  function principalBounds(data) {
    const {scale, translate} = data.transform;
    // Spherical ring integrals let the largest polygon win, not the polygon
    // with the widest bounding box. Overseas parts do not stretch the frame.
    const integrals = data.arcs.map(arc => {
      let sum = 0;
      for (let i = 2; i < arc.length; i += 2) {
        const south = (arc[i - 1] * scale[1] + translate[1]) * radians;
        const north = (arc[i + 1] * scale[1] + translate[1]) * radians;
        sum += (arc[i] - arc[i - 2]) * scale[0] * radians * (Math.sin(south) + Math.sin(north));
      }
      return sum;
    });
    const largest = new Float64Array(data.entities.length);
    const bounds = new Array(data.entities.length);
    for (const areas of [data.countries, ...data.regions]) {
      for (const [id, box, rings] of areas) {
        let size = 0;
        for (let r = 0; r < rings.length; r++) {
          let sum = 0;
          for (const arc of rings[r]) sum += arc < 0 ? -integrals[~arc] : integrals[arc];
          size += (r === 0 ? 1 : -1) * Math.abs(sum);
        }
        if (bounds[id] && size <= largest[id]) continue;
        largest[id] = size;
        bounds[id] = [
          [Math.max(-180, box[0] * scale[0] + translate[0]), Math.max(-90, box[1] * scale[1] + translate[1])],
          [Math.min(180, box[2] * scale[0] + translate[0]), Math.min(90, box[3] * scale[1] + translate[1])]
        ];
      }
    }
    return bounds;
  }

  function countryAliases(data) {
    const count = data.regions.length;
    const aliases = Array.from({length: count}, () => []);
    const names = new Map();
    for (let i = 0; i < count; i++) {
      const name = normalize(data.entities[i][0]);
      names.set(name, i);
      // Match shorter localized labels to formal names with an "of" suffix.
      const short = name.replace(/^the /, '').split(' of ')[0];
      if (short !== name && (short.includes(' ') || name.startsWith('the '))) {
        names.set(short, names.has(short) ? null : i);
      }
      // Initialisms come from the full dataset name, not a hand-picked list.
      const words = name.split(' ').filter(word => !['of', 'the', 'and'].includes(word));
      if (words.length > 1) aliases[i].push(words.map(word => word[0]).join(''));
    }
    if (typeof Intl.DisplayNames !== 'function') return aliases;
    const longNames = new Intl.DisplayNames(['en'], {type: 'region', fallback: 'none'});
    const shortNames = new Intl.DisplayNames(['en'], {type: 'region', style: 'short', fallback: 'none'});
    for (let a = 65; a <= 90; a++) {
      for (let b = 65; b <= 90; b++) {
        const code = String.fromCharCode(a, b);
        const long = normalize(longNames.of(code));
        const short = normalize(shortNames.of(code));
        const id = names.get(long) ?? names.get(short);
        if (id !== undefined && id !== null) aliases[id].push(code.toLowerCase(), long, short);
      }
    }
    return aliases;
  }

  async function searchIndex(data) {
    const entries = [];
    const bounds = principalBounds(data);
    const aliases = countryAliases(data);
    const countryCount = data.regions.length;
    const names = data.entities.map(entity => normalize(entity[0]));
    const add = (result, countryId, regionId) => {
      const name = normalize(result.name);
      entries.push({
        result, name,
        fields: [name, regionId >= 0 ? names[regionId] : '',
          countryId >= 0 ? names[countryId] : ''],
        aliases: countryId >= 0 ? aliases[countryId] : []
      });
    };
    for (let id = 0; id < data.entities.length; id++) {
      const [name, countryId] = data.entities[id];
      if (!name || !bounds[id]) continue;
      const country = data.entities[countryId][0];
      const isCountry = id < countryCount;
      add({
        id: `${isCountry ? 'country' : 'region'}:${id}`,
        type: isCountry ? 'country' : 'region', name,
        region: isCountry ? null : name, country, bounds: bounds[id]
      }, countryId, isCountry ? -1 : id);
    }
    const {scale, translate} = data.transform;
    for (let id = 0; id < data.places.length; id++) {
      const [name, lon, lat] = data.places[id];
      const x = (lon - translate[0]) / scale[0];
      const y = (lat - translate[1]) / scale[1];
      const seam = Math.abs(lon) === 180;
      const countryId = locate(data.countries, x, y, seam, data);
      const regionId = countryId >= 0 ? locate(data.regions[countryId], x, y, seam, data) : -1;
      add({
        id: `place:${id}`, type: 'place', name, lat, lon,
        region: regionId >= 0 ? data.entities[regionId][0] : null,
        country: countryId >= 0 ? data.entities[countryId][0] : null
      }, countryId, regionId);
      // Index once, yielding between batches so typing and map controls work.
      if (id % 256 === 255) await new Promise(resolve => setTimeout(resolve, 0));
    }
    return entries;
  }

  function matchRank(entry, query, terms) {
    let rank = 0;
    let named = false;
    for (const term of terms) {
      let best = Infinity;
      for (let i = 0; i < entry.fields.length; i++) {
        const field = entry.fields[i];
        const position = field.indexOf(term);
        if (position < 0) continue;
        const quality = field === term ? 0 : position === 0 || field[position - 1] === ' ' ? 1 : 2;
        best = Math.min(best, quality);
        if (i === 0) named = true;
      }
      // Short country aliases match as a whole, never inside another word.
      if (entry.aliases.includes(term)) {
        best = 0;
        if (entry.result.type === 'country') named = true;
      }
      if (!Number.isFinite(best)) return Infinity;
      rank = Math.max(rank, best);
    }
    if (entry.name === query || (entry.result.type === 'country' && entry.aliases.includes(query))) return 0;
    return 1 + rank * 2 + (named ? 0 : 1);
  }

  async function search(query, {limit = 15} = {}) {
    const data = await load();
    if (!data) return {results: [], available: false};
    const normalized = normalize(query);
    const size = Number.isFinite(limit) ? Math.max(0, Math.min(50, Math.floor(limit))) : 15;
    if (!normalized || !size) return {results: [], available: true};
    if (!searching) searching = searchIndex(data).catch(() => null);
    const entries = await searching;
    if (!entries) return {results: [], available: false};
    const terms = normalized.split(' ');
    const best = [];
    for (const entry of entries) {
      const rank = matchRank(entry, normalized, terms);
      if (!Number.isFinite(rank)) continue;
      let index = 0;
      while (index < best.length && (best[index].rank < rank
        || (best[index].rank === rank && best[index].entry.result.name.localeCompare(entry.result.name) <= 0))) index++;
      if (index >= size) continue;
      best.splice(index, 0, {entry, rank});
      if (best.length > size) best.pop();
    }
    // Only the bounded result set is copied; the shared index stays private.
    return {results: best.map(({entry}) => {
      const result = {...entry.result};
      if (result.bounds) result.bounds = result.bounds.map(point => [...point]);
      return result;
    }), available: true};
  }

  async function lookup(lat, lon) {
    if (!coordinatesValid(lat, lon)) {
      return {label: 'Unresolved location', region: null, country: null, nearest: null,
        source: null, note: 'Place names unavailable. Coordinates must be finite latitude/longitude within geographic bounds.'};
    }
    const coordinates = coordinateText(lat, lon);
    const data = await load();
    if (!data) {
      return {label: coordinates, region: null, country: null, nearest: null, source: null,
        note: 'Local geographic reference data could not be loaded or decoded. Place names are unavailable; coordinates remain usable. No external name lookup was attempted.'};
    }
    const {scale, translate} = data.transform;
    const x = (lon - translate[0]) / scale[0];
    const y = (lat - translate[1]) / scale[1];
    const seam = Math.abs(lon) === 180;
    const countryId = locate(data.countries, x, y, seam, data);
    const regionId = countryId >= 0 ? locate(data.regions[countryId], x, y, seam, data) : -1;
    const country = countryId >= 0 ? data.entities[countryId][0] : null;
    const region = regionId >= 0 ? data.entities[regionId][0] : null;
    const nearest = nearestPlace(lat, lon, data);
    let label;
    let note;
    if (countryId === -2) {
      label = `Boundary area: ${coordinates}`;
      note = 'The point touches a mapped country boundary or overlapping areas; no country or region has been assigned.';
    } else if (!country) {
      label = `Ocean or unmapped area: ${coordinates}`;
      note = 'No containing country polygon was found. This may be ocean or land omitted by the reference data. A nearby settlement does not establish jurisdiction.';
    } else {
      label = nearest.distance_km <= nearLimitKm ? `Near ${nearest.name}` : region || country;
      note = regionId === -2
        ? 'The country contains the point, but its region is unresolved at a mapped boundary or overlap.'
        : region ? 'Country and region are assigned by polygon containment.'
          : 'The country contains the point; a named containing region is not represented.';
      if (nearest.distance_km > nearLimitKm) note += ' No represented settlement is within 100 km, so the label uses the containing area.';
    }
    return {label, region, country, nearest, source: sourceText, note: `${note} ${caveat}`};
  }

  return {lookup, search};
})();
