/**
 * GEE Script 05: Yearly GeoJSON + GeoTIFF Export Pipeline
 *
 * Complete export workflow for DarInformal platform:
 *   1. Build per-sensor composites (Landsat 5/7/8/9 + Sentinel-2)
 *   2. Compute harmonized NDVI / NDBI / BSI indices
 *   3. Vectorize ISI-classified settlement polygons
 *   4. Export GeoJSON (for API) + GeoTIFF (for raster analysis)
 *
 * After export: download from Google Drive → place in backend/data/geojson/
 */

var AOI = ee.Geometry.Rectangle([39.05, -6.95, 39.45, -6.65]);
var ANALYSIS_YEARS = [2005, 2010, 2015, 2020, 2026];
var EXPORT_SCALE = 30;
var MIN_AREA_M2 = 5000;  // Minimum settlement polygon area (0.5 ha)
var FOCAL_RADIUS = 1;    // pixels — used by focal_max/min/mean (NOT ee.Kernel)

// ---------------------------------------------------------------------------
// Sensor collections — Landsat 8 does NOT exist before 2013
// ---------------------------------------------------------------------------

function getLandsatCollection(year) {
  var start = year + '-05-01';
  var end = year + '-10-31';

  // 2005–2011: Landsat 7 (+ Landsat 5 as fallback)
  if (year <= 2011) {
    var l7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2')
      .filterBounds(AOI).filterDate(start, end)
      .filter(ee.Filter.lt('CLOUD_COVER', 40));
    var l5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
      .filterBounds(AOI).filterDate(start, end)
      .filter(ee.Filter.lt('CLOUD_COVER', 40));
    return l7.merge(l5);
  }

  // 2021+: Landsat 9 + Landsat 8
  if (year >= 2021) {
    var l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
      .filterBounds(AOI).filterDate(start, end)
      .filter(ee.Filter.lt('CLOUD_COVER', 30));
    var l8new = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
      .filterBounds(AOI).filterDate(start, end)
      .filter(ee.Filter.lt('CLOUD_COVER', 30));
    return l9.merge(l8new);
  }

  // 2012–2020: Landsat 8
  return ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterBounds(AOI).filterDate(start, end)
    .filter(ee.Filter.lt('CLOUD_COVER', 30));
}

function getSentinelCollection(year) {
  var start = year + '-05-01';
  var end = year + '-10-31';
  return ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(AOI).filterDate(start, end)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 25));
}

// ---------------------------------------------------------------------------
// Per-image index computation (harmonized band names: NDVI, NDBI, BSI)
// ---------------------------------------------------------------------------

function maskLandsatL2(image) {
  var qa = image.select('QA_PIXEL');
  var mask = qa.bitwiseAnd(1 << 3).eq(0).and(qa.bitwiseAnd(1 << 4).eq(0));
  return image.updateMask(mask);
}

function computeLandsatIndices(image) {
  image = maskLandsatL2(image);
  var optical = image.select('SR_B.*').multiply(0.0000275).add(-0.2);
  var ndvi = optical.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI');
  var ndbi = optical.normalizedDifference(['SR_B6', 'SR_B5']).rename('NDBI');
  var bsi = optical.select('SR_B6').add(optical.select('SR_B4'))
    .subtract(optical.select('SR_B5')).add(optical.select('SR_B2'))
    .divide(optical.select('SR_B6').add(optical.select('SR_B4'))
      .add(optical.select('SR_B5')).add(optical.select('SR_B2')))
    .rename('BSI');
  return ee.Image.cat([ndvi, ndbi, bsi]);
}

function computeSentinelIndices(image) {
  var qa = image.select('QA60');
  var mask = qa.bitwiseAnd(1 << 10).eq(0).and(qa.bitwiseAnd(1 << 11).eq(0));
  image = image.updateMask(mask);
  var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
  var ndbi = image.normalizedDifference(['B11', 'B8']).rename('NDBI');
  var bsi = image.select('B11').add(image.select('B4'))
    .subtract(image.select('B8')).add(image.select('B2'))
    .divide(image.select('B11').add(image.select('B4'))
      .add(image.select('B8')).add(image.select('B2')))
    .rename('BSI');
  return ee.Image.cat([ndvi, ndbi, bsi]);
}

function getYearlyIndices(year) {
  var ls = getLandsatCollection(year).map(computeLandsatIndices);
  var collection = ls;

  // Sentinel-2 available from ~2017; merge for improved composite
  if (year >= 2017) {
    var s2 = getSentinelCollection(year).map(computeSentinelIndices);
    collection = ls.merge(s2);
  }

  return collection.median().select(['NDVI', 'NDBI', 'BSI']).clip(AOI);
}

// ---------------------------------------------------------------------------
// ISI computation from harmonized index composite
// ---------------------------------------------------------------------------

function computeISIStack(indicesImage) {
  var ndvi = indicesImage.select('NDVI');
  var ndbi = indicesImage.select('NDBI');
  var bsi = indicesImage.select('BSI');

  var ndbiN = ndbi.subtract(-0.5).divide(1.3).clamp(0, 1);
  var ndviInv = ee.Image(1).subtract(ndvi.subtract(-0.2).divide(1.0).clamp(0, 1));
  var bsiN = bsi.clamp(0, 1);

  var builtMask = ndbiN.gt(0.25).and(ndviInv.gt(0.35));

  // focal_max/min/mean require {radius: N}, NOT ee.Kernel
  var focalOpts = {radius: FOCAL_RADIUS, units: 'pixels'};
  var frag = builtMask.focal_max(focalOpts)
    .subtract(builtMask.focal_min(focalOpts))
    .focal_mean(focalOpts)
    .clamp(0, 1);

  var isi = ndbiN.multiply(0.3).add(ndviInv.multiply(0.25))
    .add(bsiN.multiply(0.2)).add(frag.multiply(0.25)).clamp(0, 1);

  return ee.Image.cat([
    isi.rename('isi_score'),
    ndbi.rename('ndbi'),
    ndvi.rename('ndvi'),
    bsiN.rename('bsi'),
    frag.rename('fragmentation_index'),
    builtMask.rename('built_mask')
  ]);
}

// ---------------------------------------------------------------------------
// Vectorize settlements and attach attributes
// ---------------------------------------------------------------------------

function vectorizeSettlements(isiImage, year) {
  var settlementMask = isiImage.select('isi_score').gt(0.15);

  var vectors = settlementMask.selfMask().reduceToVectors({
    geometry: AOI,
    scale: EXPORT_SCALE,
    maxPixels: 1e10,
    bestEffort: true,
    geometryType: 'polygon',
    eightConnected: false,
    labelProperty: 'settlement',
    reducer: ee.Reducer.countEvery()
  });

  vectors = vectors.filter(ee.Filter.gt('area', MIN_AREA_M2));

  var withStats = isiImage.reduceRegions({
    collection: vectors,
    reducer: ee.Reducer.mean(),
    scale: EXPORT_SCALE
  });

  return withStats.map(function(feature) {
    var isi = ee.Number(feature.get('isi_score'));

    var riskLabel = ee.Algorithms.If(
      isi.lt(0.2), 'low',
      ee.Algorithms.If(isi.lte(0.5), 'medium', 'high')
    );

    var areaHa = ee.Number(feature.geometry().area()).divide(10000);
    var popProxy = areaHa.multiply(8500).multiply(isi.multiply(0.6).add(0.4));
    var indexStr = ee.Number.parse(feature.get('system:index')).add(1).format('%04d');

    return feature.set({
      'id': ee.String('DAR-').cat(ee.String(year)).cat('-').cat(indexStr),
      'name': ee.String('Settlement ').cat(indexStr),
      'year': year,
      'risk_level': riskLabel,
      'area_ha': areaHa,
      'population_proxy': popProxy.int()
    });
  });
}

// ---------------------------------------------------------------------------
// Main export loop
// ---------------------------------------------------------------------------

ANALYSIS_YEARS.forEach(function(year) {
  print('Processing year:', year);

  var indicesComposite = getYearlyIndices(year);
  var indices = computeISIStack(indicesComposite);
  var settlements = vectorizeSettlements(indices, year);

  // Preview (toggle in Layers panel)
  Map.addLayer(indices.select('isi_score'),
    {min: 0, max: 1, palette: ['green', 'yellow', 'red']},
    'ISI ' + year, false);

  Export.table.toDrive({
    collection: settlements,
    description: 'DarInformal_Settlements_' + year,
    folder: 'DarInformal_GEE_Exports',
    fileNamePrefix: 'settlements_' + year,
    fileFormat: 'GeoJSON'
  });

  Export.image.toDrive({
    image: indices.toFloat(),
    description: 'DarInformal_Raster_' + year,
    folder: 'DarInformal_GEE_Exports',
    fileNamePrefix: 'darinformal_' + year,
    region: AOI,
    scale: EXPORT_SCALE,
    maxPixels: 1e10,
    crs: 'EPSG:4326'
  });
});

Map.centerObject(AOI, 11);
print('=== DarInformal Export Pipeline ===');
print('Years:', ANALYSIS_YEARS);
print('Sensors: L5/L7 (<=2011), L8 (2012-2020), L8/L9+S2 (>=2017)');
print('After export completes:');
print('1. Download GeoJSON from Google Drive');
print('2. Rename to settlements_YYYY.geojson');
print('3. Place in backend/data/geojson/');
print('4. Restart the DarInformal API');
