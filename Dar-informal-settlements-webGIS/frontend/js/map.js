/**
 * DarInformal Map Module
 * Hybrid rendering: GeoServer WMS tiles + API GeoJSON for popups/interaction.
 */

const DarMap = (() => {
  const RISK_COLORS = {
    low: '#22c55e',
    medium: '#f59e0b',
    high: '#ef4444',
  };

  const RISK_LABELS = {
    low: 'Low Risk',
    medium: 'Medium Risk',
    high: 'High Risk',
  };

  let map = null;
  let wmsLayer = null;
  let vectorLayer = null;
  let changeLayer = null;
  let overlayControl = null;
  let geoserverConfig = null;
  let renderMode = 'hybrid'; // 'wms' | 'geojson' | 'hybrid'
  let currentYear = 2020;
  let onFeatureClick = null;

  async function initGeoserverConfig() {
    try {
      geoserverConfig = await API.getGeoserverConfig();
      if (window.DARINFORMAL_DEFAULT_RENDER_MODE === 'geojson') {
        renderMode = 'geojson';
        const sel = document.getElementById('render-mode');
        if (sel) sel.value = 'geojson';
      }
    } catch (e) {
      console.warn('GeoServer config unavailable, using GeoJSON only', e);
      geoserverConfig = null;
      renderMode = 'geojson';
    }
  }

  function init(containerId = 'map') {
    map = L.map(containerId, {
      center: [-6.7924, 39.2083],
      zoom: 12,
      zoomControl: false,
      attributionControl: true,
    });

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    const darkBase = L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      { attribution: '&copy; OSM &copy; CARTO', maxZoom: 19 }
    );
    const lightBase = L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
      { attribution: '&copy; OSM &copy; CARTO', maxZoom: 19 }
    );
    const satellite = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      { attribution: '&copy; Esri', maxZoom: 19 }
    );

    darkBase.addTo(map);
    L.control.layers(
      { Dark: darkBase, Light: lightBase, Satellite: satellite },
      {},
      { position: 'bottomleft', collapsed: true }
    ).addTo(map);

    return map;
  }

  function buildWmsLayer(year) {
    if (!geoserverConfig) return null;
    const wmsUrl = geoserverConfig.wms_url;
    const layerName = geoserverConfig.layer_full;
    return L.tileLayer.wms(wmsUrl, {
      layers: layerName,
      styles: geoserverConfig.risk_style || '',
      format: 'image/png',
      transparent: true,
      version: '1.1.1',
      CQL_FILTER: `year=${year}`,
      attribution: 'DarInformal / PostGIS / GeoServer',
    });
  }

  function styleFeature(feature) {
    const risk = feature.properties.risk_level || 'medium';
    const isi = feature.properties.isi_score || 0;
    const isInteractionLayer = renderMode === 'hybrid';
    return {
      fillColor: RISK_COLORS[risk] || RISK_COLORS.medium,
      fillOpacity: isInteractionLayer ? 0.01 : 0.55 + isi * 0.25,
      color: isInteractionLayer ? 'transparent' : RISK_COLORS[risk],
      weight: isInteractionLayer ? 0 : 1.5,
      opacity: isInteractionLayer ? 0 : 0.85,
    };
  }

  function buildPopup(props) {
    const risk = props.risk_level || 'unknown';
    const color = RISK_COLORS[risk] || '#888';
    return `
      <div class="popup-content">
        <h3>${props.name || 'Settlement'}</h3>
        <div class="popup-risk" style="background:${color}">
          ${RISK_LABELS[risk] || risk} — ISI: ${(props.isi_score || 0).toFixed(3)}
        </div>
        <table class="popup-table">
          <tr><td>Year</td><td>${props.year || '—'}</td></tr>
          <tr><td>Area</td><td>${(props.area_ha || 0).toFixed(1)} ha</td></tr>
          <tr><td>Est. Population</td><td>${(props.population_proxy || 0).toLocaleString()}</td></tr>
          <tr><td>NDBI</td><td>${(props.ndbi || 0).toFixed(3)}</td></tr>
          <tr><td>NDVI</td><td>${(props.ndvi || 0).toFixed(3)}</td></tr>
          <tr><td>BSI</td><td>${(props.bsi || 0).toFixed(3)}</td></tr>
          <tr><td>Fragmentation</td><td>${(props.fragmentation_index || 0).toFixed(3)}</td></tr>
        </table>
        <div class="popup-id">${props.id || ''}</div>
      </div>
    `;
  }

  function onEachFeature(feature, layer) {
    const props = feature.properties;
    layer.bindPopup(buildPopup(props), { maxWidth: 300, className: 'settlement-popup' });
    layer.on({
      mouseover: (e) => {
        if (renderMode === 'wms') return;
        const l = e.target;
        l.setStyle({ weight: 3, fillOpacity: renderMode === 'hybrid' ? 0.4 : 0.75 });
        l.bringToFront();
      },
      mouseout: (e) => {
        if (vectorLayer) vectorLayer.resetStyle(e.target);
      },
      click: () => {
        if (onFeatureClick) onFeatureClick(props);
      },
    });
  }

  function clearRiskLayers() {
    if (wmsLayer) { map.removeLayer(wmsLayer); wmsLayer = null; }
    if (vectorLayer) { map.removeLayer(vectorLayer); vectorLayer = null; }
  }

  async function loadRiskLayer(year) {
    currentYear = year;
    showLoading(true);

    try {
      if (!geoserverConfig) await initGeoserverConfig();

      const data = await API.getRiskLayer(year);
      clearRiskLayers();

      // GeoServer WMS (fast tiled rendering from PostGIS)
      if (renderMode === 'wms' || renderMode === 'hybrid') {
        wmsLayer = buildWmsLayer(year);
        if (wmsLayer) wmsLayer.addTo(map);
      }

      // API GeoJSON (popups, hover, change detection)
      if (renderMode === 'geojson' || renderMode === 'hybrid') {
        vectorLayer = L.geoJSON(
          { type: 'FeatureCollection', features: data.features },
          { style: styleFeature, onEachFeature }
        ).addTo(map);

        if (renderMode === 'geojson' && vectorLayer.getBounds().isValid()) {
          map.fitBounds(vectorLayer.getBounds(), { padding: [40, 40], maxZoom: 14 });
        }
      }

      if (wmsLayer) {
        const b = data.metadata?.bounds;
        if (b) {
          map.fitBounds([[b.south, b.west], [b.north, b.east]], { padding: [40, 40], maxZoom: 14 });
        } else if (vectorLayer && vectorLayer.getBounds().isValid()) {
          map.fitBounds(vectorLayer.getBounds(), { padding: [40, 40], maxZoom: 14 });
        }
      }

      return data;
    } finally {
      showLoading(false);
    }
  }

  function setRenderMode(mode) {
    if (!['wms', 'geojson', 'hybrid'].includes(mode)) return;
    renderMode = mode;
    if (geoserverConfig === null && mode !== 'geojson') {
      renderMode = 'geojson';
    }
    loadRiskLayer(currentYear);
  }

  function getRenderMode() {
    return renderMode;
  }

  async function loadChangeOverlay(fromYear, toYear) {
    showLoading(true);
    try {
      const data = await API.getChangeDetection(fromYear, toYear);
      if (changeLayer) { map.removeLayer(changeLayer); changeLayer = null; }

      const changeFeatures = [];
      data.new_settlements.forEach((s) => {
        changeFeatures.push({ type: 'Feature', geometry: s.geometry, properties: { ...s, change_type: 'new' } });
      });
      data.expanded_settlements.forEach((s) => {
        changeFeatures.push({
          type: 'Feature', geometry: s.to.geometry,
          properties: { ...s.to, change_type: 'expanded', area_change_pct: s.area_change_pct },
        });
      });

      if (changeFeatures.length > 0) {
        changeLayer = L.geoJSON(
          { type: 'FeatureCollection', features: changeFeatures },
          {
            style: (f) => {
              const type = f.properties.change_type;
              const colors = { new: '#3b82f6', expanded: '#a855f7' };
              return {
                fillColor: colors[type] || '#888',
                fillOpacity: 0.4,
                color: colors[type] || '#888',
                weight: 2,
                dashArray: type === 'new' ? '6 4' : null,
              };
            },
            onEachFeature: (feature, layer) => {
              const p = feature.properties;
              const label = p.change_type === 'new' ? 'New Settlement' : `Expanded (+${p.area_change_pct}%)`;
              layer.bindPopup(`<b>${p.name}</b><br>${label}<br>ISI: ${p.isi_score}`);
            },
          }
        ).addTo(map);
      }
      return data;
    } finally {
      showLoading(false);
    }
  }

  function clearChangeOverlay() {
    if (changeLayer) { map.removeLayer(changeLayer); changeLayer = null; }
  }

  function setAOIBounds(bounds) {
    if (bounds) {
      L.rectangle(
        [[bounds.south, bounds.west], [bounds.north, bounds.east]],
        { color: '#60a5fa', weight: 1, fillOpacity: 0, dashArray: '8 4' }
      ).addTo(map);
    }
  }

  function showLoading(show) {
    const el = document.getElementById('map-loading');
    if (el) el.classList.toggle('visible', show);
  }

  function setFeatureClickHandler(handler) { onFeatureClick = handler; }
  function getMap() { return map; }
  function getCurrentYear() { return currentYear; }

  return {
    init,
    initGeoserverConfig,
    loadRiskLayer,
    loadChangeOverlay,
    clearChangeOverlay,
    setAOIBounds,
    setFeatureClickHandler,
    setRenderMode,
    getRenderMode,
    getMap,
    getCurrentYear,
    RISK_COLORS,
    RISK_LABELS,
  };
})();

window.DarMap = DarMap;
