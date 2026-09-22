/* Leaflet 1.9.4 is vendored in vendor/. Tiles follow the OSM tile usage policy. */
window.LocationMap = (() => {
  'use strict';

  const coordinatesValid = (lat, lon) => Number.isFinite(lat) && Number.isFinite(lon)
    && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;
  const coordinateText = (lat, lon) => `${lat.toFixed(5)}°, ${lon.toFixed(5)}°`;
  const textNode = (tag, className, text) => {
    const node = document.createElement(tag);
    node.className = className;
    if (text) node.textContent = text;
    return node;
  };

  function mount(id, {sites = [], onSelect, onPreset} = {}) {
    const root = typeof id === 'string' ? document.getElementById(id) : id;
    if (!root) throw new Error('Location map container was not found.');
    root.classList.add('location-map');
    const canvas = textNode('div', 'location-map-canvas');
    const help = textNode('p', 'location-map-help', 'Scroll or pinch over the map to zoom. Click to place a pin, or focus the map and use arrow keys to pan, + / − to zoom, and Enter to select the center. Coordinate entry is also available in the location panel. OpenStreetMap receives your IP and viewed map area; location search stays within the saved list.');
    help.id = `${root.id || 'location-map'}-help`;
    canvas.setAttribute('aria-label', 'Location map. Select coordinates, then use Analyze location.');
    canvas.setAttribute('aria-describedby', help.id);
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
    const caption = textNode('p', 'location-map-caption', 'Basemap is geographic context, not weather risk. Saved pins are saved analyses, not all supported areas.');
    const evidence = textNode('p', 'location-map-evidence');
    evidence.hidden = true;
    const warning = textNode('p', 'location-map-warning');
    warning.setAttribute('role', 'status');
    warning.setAttribute('aria-live', 'polite');
    warning.hidden = true;
    root.replaceChildren(canvas, toolbar, caption, evidence, warning, help);

    let map = null;
    let selected = null;
    let grid = null;
    let failed = false;
    const warn = message => {
      warning.textContent = message;
      warning.hidden = !message;
    };
    const clearEvidence = () => {
      if (map && grid) map.removeLayer(grid);
      grid = null;
      evidence.hidden = true;
      evidence.textContent = '';
    };
    const failMap = () => {
      failed = true;
      if (map) map.remove();
      map = null;
      canvas.hidden = true;
      toolbar.hidden = true;
      help.hidden = true;
      warn('The interactive map could not load. Enter coordinates or choose a saved analysis in the location panel. Map availability does not indicate weather-data availability.');
    };
    const markerLabel = (lat, lon, label) => `${label || 'Selected point'}: ${coordinateText(lat, lon)}. Drag to move, or use coordinate entry.`;

    function setSelection(lat, lon, {label, recenter = true} = {}) {
      clearEvidence();
      if (!coordinatesValid(lat, lon)) return;
      if (!map || failed) return;
      const accessibleLabel = markerLabel(lat, lon, label);
      const popup = textNode('span', '', accessibleLabel);
      if (!selected) {
        selected = L.marker([lat, lon], {
          icon: L.divIcon({className: 'location-map-pin location-map-pin-selected', html: '<span aria-hidden="true"></span>', iconSize: [44, 44], iconAnchor: [22, 30]}),
          draggable: true,
          keyboard: true,
          title: accessibleLabel,
          alt: accessibleLabel,
          zIndexOffset: 1000,
          autoPan: true,
          autoPanOnFocus: true
        }).addTo(map).bindTooltip(popup, {direction: 'top', offset: [0, -24]});
        selected.on('dragstart', clearEvidence);
        selected.on('dragend', () => choose(selected.getLatLng()));
      } else {
        selected.setLatLng([lat, lon]);
        selected.setTooltipContent(popup);
      }
      const element = selected.getElement();
      if (element) {
        element.setAttribute('aria-label', accessibleLabel);
        element.setAttribute('title', accessibleLabel);
      }
      if (recenter) map.setView([lat, lon], Math.max(map.getZoom(), 7), {animate: false});
    }

    function choose(point) {
      const lat = Math.max(-90, Math.min(90, point.lat));
      const lon = ((point.lng + 180) % 360 + 360) % 360 - 180;
      setSelection(lat, lon, {recenter: false});
      if (typeof onSelect === 'function') onSelect({lat, lon});
    }

    function setEvidence(result) {
      clearEvidence();
      const source = result?.hourly_source;
      if (!source || !coordinatesValid(source.source_lat, source.source_lon)) return;
      evidence.textContent = `Hourly weather grid, not parcel. Source cell center ${coordinateText(source.source_lat, source.source_lon)}; 0.5° latitude × 0.625° longitude. This cell is evidence for this analysis, not a coverage map.`;
      evidence.hidden = false;
      if (!map || failed) return;
      const lat = source.source_lat;
      const lon = source.source_lon;
      grid = L.rectangle([[lat - 0.25, lon - 0.3125], [lat + 0.25, lon + 0.3125]], {
        color: '#8b561c', weight: 2, opacity: 0.95,
        fillColor: '#b88544', fillOpacity: 0.12,
        dashArray: '6 4', interactive: false
      }).addTo(map);
    }

    const controller = {
      setSelection,
      setEvidence,
      resize() { if (map && !failed) map.invalidateSize({animate: false, pan: false}); }
    };
    if (!window.L || typeof window.L.map !== 'function') {
      failMap();
      return controller;
    }

    try {
      const reducedMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
      map = L.map(canvas, {
        center: [18, 0], zoom: 2, minZoom: 1, maxZoom: 18,
        zoomControl: true, attributionControl: true,
        keyboard: true, scrollWheelZoom: true, doubleClickZoom: false,
        worldCopyJump: true, zoomAnimation: !reducedMotion,
        fadeAnimation: !reducedMotion, markerZoomAnimation: !reducedMotion
      });
      map.attributionControl.setPrefix('<a href="https://leafletjs.com/">Leaflet</a>');
      world.addEventListener('click', () => map.setView([18, 0], 2, {animate: false}));
      center.addEventListener('click', () => choose(map.getCenter()));
      map.on('click', event => choose(event.latlng));
      canvas.addEventListener('keydown', event => {
        if (event.target === canvas && event.key === 'Enter') {
          event.preventDefault();
          choose(map.getCenter());
        }
      });

      for (const entry of sites) {
        const site = entry?.site;
        if (!site || !coordinatesValid(site.lat, site.lon)) continue;
        const name = String(site.name || 'Saved analysis');
        const accessibleLabel = `Select saved analysis: ${name}`;
        const marker = L.marker([site.lat, site.lon], {
          icon: L.divIcon({className: 'location-map-pin location-map-pin-saved', html: '<span aria-hidden="true"></span>', iconSize: [44, 44], iconAnchor: [22, 22]}),
          title: accessibleLabel, alt: accessibleLabel,
          keyboard: true, autoPanOnFocus: true, bubblingMouseEvents: false
        }).addTo(map).bindTooltip(textNode('span', '', name), {direction: 'top', offset: [0, -12]});
        const selectSaved = () => {
          setSelection(site.lat, site.lon, {label: name, recenter: false});
          if (typeof onPreset === 'function') onPreset(name);
        };
        marker.on('click', selectSaved);
        const element = marker.getElement();
        element.setAttribute('aria-label', accessibleLabel);
        element.addEventListener('keydown', event => {
          if (event.key === ' ') {
            event.preventDefault();
            event.stopPropagation();
            selectSaved();
          }
        });
      }

      if (window.location.protocol !== 'http:' && window.location.protocol !== 'https:') {
        warn('Basemap tiles need an HTTP or HTTPS page. Coordinates and saved analyses still work; this is not a weather-data limitation.');
      } else {
        const failedTiles = new Set();
        let waitingTimer = null;
        let waiting = false;
        const tileWarning = () => {
          warn(failedTiles.size || waiting
            ? 'Some basemap tiles could not load. You can still select a point, enter coordinates, or choose a saved analysis. This is not a weather-data limitation.'
            : '');
        };
        const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 18, minZoom: 1, keepBuffer: 1,
          updateWhenIdle: true, updateWhenZooming: false,
          referrerPolicy: 'strict-origin-when-cross-origin',
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors · <a href="https://www.openstreetmap.org/fixthemap">Report a map issue</a>'
        });
        tiles.on('loading', () => {
          clearTimeout(waitingTimer);
          waitingTimer = setTimeout(() => { waiting = true; tileWarning(); }, 12000);
        });
        tiles.on('tileerror', event => {
          failedTiles.add(event.tile);
          tileWarning();
        });
        tiles.on('tileunload', event => {
          failedTiles.delete(event.tile);
          tileWarning();
        });
        tiles.on('load', () => {
          clearTimeout(waitingTimer);
          waiting = false;
          tileWarning();
        });
        tiles.addTo(map);
      }
    } catch (error) {
      failMap();
    }
    return controller;
  }

  return {mount};
})();
