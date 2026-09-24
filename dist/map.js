/* MapLibre GL JS 5.24.0 and the adapted OpenFreeMap Positron style are in vendor/. */
window.LocationMap = (() => {
  'use strict';

  const assetBase = new URL('vendor/', document.currentScript?.src || document.baseURI);
  const mercatorLimit = 85.0511287798066;
  const emptyFeatures = {type: 'FeatureCollection', features: []};
  const coordinatesValid = (lat, lon) => Number.isFinite(lat) && Number.isFinite(lon)
    && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;
  const coordinateText = (lat, lon) => `${lat.toFixed(5)}°, ${lon.toFixed(5)}°`;
  const wrapLongitude = lon => ((lon + 180) % 360 + 360) % 360 - 180;
  const textNode = (tag, className, text) => {
    const node = document.createElement(tag);
    node.className = className;
    if (text) node.textContent = text;
    return node;
  };
  const link = (text, href) => {
    const node = textNode('a', '', text);
    node.href = href;
    node.target = '_blank';
    node.rel = 'noopener noreferrer';
    return node;
  };

  function cellGeometry(lat, lon) {
    const south = Math.max(-mercatorLimit, lat - 0.25);
    const north = Math.min(mercatorLimit, lat + 0.25);
    if (south >= north) return emptyFeatures;
    const west = lon - 0.3125;
    const east = lon + 0.3125;
    const intervals = west < -180 ? [[west + 360, 180], [-180, east]]
      : east > 180 ? [[west, 180], [-180, east - 360]] : [[west, east]];
    const polygons = intervals.map(([left, right]) => [
      [[left, south], [right, south], [right, north], [left, north], [left, south]]
    ]);
    return {
      type: 'Feature', properties: {},
      geometry: {type: 'MultiPolygon', coordinates: polygons}
    };
  }

  function mount(id, {sites = [], onSelect, onPreset} = {}) {
    const root = typeof id === 'string' ? document.getElementById(id) : id;
    if (!root) throw new Error('Location map container was not found.');
    root.classList.add('location-map');
    const canvas = textNode('div', 'location-map-canvas');
    const help = textNode('p', 'location-map-help', 'Scroll or pinch to zoom. Click to place a pin, or focus the map and use arrow keys to pan, + / − to zoom, and Enter to select the center. Drag the selected pin to move it. Then use Analyze location. Coordinate entry is always available. OpenFreeMap and its CDN receive your IP and viewed map area; place lookup stays in your browser. ');
    help.id = `${root.id || 'location-map'}-help`;
    help.append(link('Map privacy', 'https://openfreemap.org/privacy/'));
    const toolbar = textNode('div', 'location-map-toolbar');
    const world = textNode('button', 'location-map-world', 'World view');
    world.type = 'button';
    world.setAttribute('aria-label', 'Reset map to world view');
    const center = textNode('button', 'location-map-center', 'Use map center');
    center.type = 'button';
    const legend = textNode('div', 'location-map-legend');
    legend.append(
      textNode('span', 'location-map-key location-map-key-saved', 'Saved analysis'),
      textNode('span', 'location-map-key location-map-key-selected', 'Selected point')
    );
    toolbar.append(world, center, legend);
    const caption = textNode('p', 'location-map-caption', 'Basemap is geographic context, not weather risk. Saved pins are saved analyses, not all supported areas. Labels prefer English, then romanized names where available. Boundaries are reference data, not a legal determination.');
    const evidence = textNode('p', 'location-map-evidence');
    evidence.hidden = true;
    const warning = textNode('p', 'location-map-warning');
    warning.setAttribute('role', 'status');
    warning.setAttribute('aria-live', 'polite');
    warning.hidden = true;
    root.replaceChildren(canvas, toolbar, caption, evidence, warning, help);

    let map = null;
    let selected = null;
    let selection = null;
    let gridData = null;
    let styleReady = false;
    let failed = false;
    let mapMessage = '';
    let latitudeMessage = '';
    let waitingTimer = null;
    let styleTimer = null;
    let styleRequest = null;
    let basemapInstalled = false;
    let resourceFailed = false;
    const updateWarning = () => {
      warning.textContent = [mapMessage, latitudeMessage].filter(Boolean).join(' ');
      warning.hidden = !warning.textContent;
    };
    const warn = message => {
      mapMessage = message;
      updateWarning();
    };
    const syncEvidence = () => {
      if (!map || failed || !styleReady) return;
      const source = map.getSource('weather-source-cell');
      if (source) {
        source.setData(gridData || emptyFeatures);
      } else if (gridData) {
        map.addSource('weather-source-cell', {type: 'geojson', data: gridData});
        map.addLayer({
          id: 'weather-source-cell-fill', type: 'fill', source: 'weather-source-cell',
          paint: {'fill-color': '#b88544', 'fill-opacity': 0.12}
        });
        map.addLayer({
          id: 'weather-source-cell-line', type: 'line', source: 'weather-source-cell',
          paint: {'line-color': '#8b561c', 'line-width': 2, 'line-opacity': 0.95, 'line-dasharray': [3, 2]}
        });
      }
    };
    const clearEvidence = () => {
      gridData = null;
      syncEvidence();
      evidence.hidden = true;
      evidence.textContent = '';
    };
    const failMap = () => {
      if (failed) return;
      failed = true;
      clearTimeout(waitingTimer);
      clearTimeout(styleTimer);
      styleRequest?.abort();
      if (map) map.remove();
      map = null;
      canvas.hidden = true;
      toolbar.hidden = true;
      help.hidden = true;
      latitudeMessage = '';
      warn('The interactive map could not load. Enter coordinates or choose a saved analysis in the location panel. Map availability does not indicate weather-data availability.');
    };
    const markerLabel = () => `${selection.label || 'Selected point'}: ${coordinateText(selection.lat, selection.lon)}. Drag to move, or use coordinate entry.`;
    const makePin = (kind, label) => {
      const element = textNode(kind === 'saved' ? 'button' : 'div', `location-map-pin location-map-pin-${kind}`);
      if (kind === 'saved') element.type = 'button';
      else {
        element.tabIndex = 0;
        element.setAttribute('role', 'img');
      }
      const dot = textNode('span', 'location-map-pin-dot');
      dot.setAttribute('aria-hidden', 'true');
      const tooltip = textNode('span', 'location-map-pin-tooltip', label);
      tooltip.setAttribute('aria-hidden', 'true');
      element.append(dot, tooltip);
      element.setAttribute('aria-label', label);
      element.title = label;
      return element;
    };

    function setLabel(label) {
      if (!selection) return;
      selection.label = String(label || '');
      if (!selected) return;
      const element = selected.getElement();
      const accessibleLabel = markerLabel();
      element.setAttribute('aria-label', accessibleLabel);
      element.title = accessibleLabel;
      element.querySelector('.location-map-pin-tooltip').textContent = accessibleLabel;
    }

    function setSelection(lat, lon, {label, recenter = true} = {}) {
      if (!coordinatesValid(lat, lon)) return;
      clearEvidence();
      selection = {lat, lon, label: String(label || '')};
      if (!map || failed) return;
      const outsideMap = Math.abs(lat) > mercatorLimit;
      latitudeMessage = outsideMap
        ? `Selected coordinates ${coordinateText(lat, lon)} are beyond this flat map's latitude limit of ±85.05113°. The coordinates are unchanged; use coordinate entry for polar locations.` : '';
      updateWarning();
      if (!selected) {
        selected = new maplibregl.Marker({
          element: makePin('selected', markerLabel()), draggable: true,
          anchor: 'center', offset: [0, -12 * Math.SQRT2], subpixelPositioning: true
        }).setLngLat([lon, Math.max(-mercatorLimit, Math.min(mercatorLimit, lat))]).addTo(map);
        selected.on('dragstart', clearEvidence);
        selected.on('dragend', () => choose(selected.getLngLat()));
      }
      // Do not project an unsupported polar coordinate to a different visible pin.
      selected.getElement().hidden = outsideMap;
      if (!outsideMap) selected.setLngLat([lon, lat]);
      setLabel(selection.label);
      if (recenter) map.jumpTo({
        center: [lon, Math.max(-mercatorLimit, Math.min(mercatorLimit, lat))],
        zoom: Math.max(map.getZoom(), 7)
      });
    }

    function focusArea(bounds) {
      if (!Array.isArray(bounds) || bounds.length !== 2
        || !bounds.every(point => Array.isArray(point) && point.length === 2
          && coordinatesValid(point[1], point[0]))
        || bounds[0][0] > bounds[1][0] || bounds[0][1] > bounds[1][1]) return;
      selection = null;
      if (selected) selected.getElement().hidden = true;
      clearEvidence();
      latitudeMessage = '';
      updateWarning();
      if (!map || failed) return;
      const framed = bounds.map(([lon, lat]) => [lon, Math.max(-mercatorLimit, Math.min(mercatorLimit, lat))]);
      map.fitBounds(framed, {padding: 36, maxZoom: 9, duration: 0});
    }

    function choose(point) {
      if (!Number.isFinite(point.lat) || !Number.isFinite(point.lng)) return;
      const lat = Math.max(-90, Math.min(90, point.lat));
      const lon = wrapLongitude(point.lng);
      setSelection(lat, lon, {recenter: false});
      if (typeof onSelect === 'function') onSelect({lat, lon});
    }

    function setEvidence(result) {
      clearEvidence();
      const source = result?.hourly_source;
      if (!source || !coordinatesValid(source.source_lat, source.source_lon)) return;
      evidence.textContent = `Hourly weather grid, not parcel. Source cell center ${coordinateText(source.source_lat, source.source_lon)}; 0.5° latitude × 0.625° longitude. This cell is evidence for this analysis, not a coverage map.`;
      evidence.hidden = false;
      gridData = cellGeometry(source.source_lat, source.source_lon);
      syncEvidence();
    }

    const controller = {
      setSelection, setEvidence, setLabel, focusArea,
      resize() { if (map && !failed) map.resize(); }
    };
    if (!window.maplibregl || typeof window.maplibregl.Map !== 'function') {
      failMap();
      return controller;
    }

    try {
      const reducedMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
      map = new maplibregl.Map({
        container: canvas, center: [0, 18], zoom: 1, minZoom: 0, maxZoom: 18,
        style: {version: 8, sources: {}, layers: [{id: 'background', type: 'background', paint: {'background-color': '#eef1ec'}}]},
        attributionControl: false, keyboard: true, scrollZoom: true,
        doubleClickZoom: false, dragRotate: false, touchPitch: false,
        pitch: 0, maxPitch: 0, renderWorldCopies: true,
        respectPrefersReducedMotion: true, fadeDuration: reducedMotion ? 0 : 200
      });
      map.touchZoomRotate.disableRotation();
      map.keyboard.disableRotation();
      map.addControl(new maplibregl.NavigationControl({showCompass: false}), 'top-left');
      map.addControl(new maplibregl.AttributionControl({
        compact: false,
        customAttribution: `<a href="https://maplibre.org/" target="_blank" rel="noopener noreferrer">MapLibre</a> · <a href="${new URL('openfreemap-positron-LICENSE.txt', assetBase).href}" target="_blank" rel="noopener noreferrer">Positron style credits</a>`
      }));
      const mapCanvas = map.getCanvas();
      mapCanvas.setAttribute('aria-label', 'Location map. Select coordinates, then use Analyze location.');
      mapCanvas.setAttribute('aria-describedby', help.id);
      world.addEventListener('click', () => map?.jumpTo({center: [0, 18], zoom: 1, bearing: 0, pitch: 0}));
      center.addEventListener('click', () => { if (map) choose(map.getCenter()); });
      map.on('click', event => {
        if (!event.originalEvent.target.closest('.location-map-pin')) choose(event.lngLat);
      });
      mapCanvas.addEventListener('keydown', event => {
        if (event.key === 'Enter' && map) {
          event.preventDefault();
          choose(map.getCenter());
        }
      });
      map.on('webglcontextlost', failMap);
      map.on('style.load', () => {
        styleReady = true;
        syncEvidence();
      });
      map.on('error', () => {
        resourceFailed = true;
        warn('Some basemap tiles or labels could not load. You can still select coordinates or choose a saved analysis. This is not a weather-data limitation.');
      });
      map.on('dataloading', () => {
        if (!basemapInstalled || waitingTimer || failed) return;
        waitingTimer = setTimeout(() => {
          waitingTimer = null;
          if (map && (!map.isStyleLoaded() || !map.areTilesLoaded())) warn('The basemap is taking longer to load. Coordinates and saved analyses still work. This is not a weather-data limitation.');
        }, 12000);
      });
      map.on('idle', () => {
        clearTimeout(waitingTimer);
        waitingTimer = null;
        if (basemapInstalled && !resourceFailed) warn('');
      });

      for (const entry of sites) {
        const site = entry?.site;
        if (!site || !coordinatesValid(site.lat, site.lon) || Math.abs(site.lat) > mercatorLimit) continue;
        const name = String(site.name || 'Saved analysis');
        const element = makePin('saved', `Select saved analysis: ${name}`);
        new maplibregl.Marker({element, anchor: 'center', subpixelPositioning: true})
          .setLngLat([site.lon, site.lat]).addTo(map);
        element.addEventListener('click', event => {
          event.stopPropagation();
          setSelection(site.lat, site.lon, {label: name, recenter: false});
          if (typeof onPreset === 'function') onPreset(name);
        });
      }

      if (window.location.protocol !== 'http:' && window.location.protocol !== 'https:') {
        warn('Basemap resources need an HTTP or HTTPS page. Coordinates and saved analyses still work; this is not a weather-data limitation.');
      } else {
        warn('Loading the basemap. Coordinates and saved analyses are already available.');
        styleRequest = new AbortController();
        styleTimer = setTimeout(() => styleRequest.abort(), 12000);
        fetch(new URL('openfreemap-positron-en.json', assetBase), {signal: styleRequest.signal})
          .then(response => {
            if (!response.ok) throw new Error(`Basemap style HTTP ${response.status}`);
            return response.json();
          })
          .then(style => {
            if (failed) return;
            styleReady = false;
            basemapInstalled = true;
            map.setStyle(style, {diff: false});
          })
          .catch(() => {
            if (!failed) warn('The basemap style could not load. You can still select coordinates or choose a saved analysis. This is not a weather-data limitation.');
          })
          .finally(() => clearTimeout(styleTimer));
      }
    } catch (error) {
      failMap();
    }
    return controller;
  }

  return {mount};
})();
