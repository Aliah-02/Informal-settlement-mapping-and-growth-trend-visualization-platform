/**
 * GEE Script 02: Dynamic World Weak Labels for Informal Settlements
 *
 * Uses Google's Dynamic World V1 (10m land cover) to extract weak labels
 * for built-up / informal settlement areas in Dar es Salaam.
 *
 * Classes used:
 *   6 = Built area
 *   7 = Bare ground (common in informal expansion zones)
 */

// Import AOI (paste AOI geometry from script 01 or load asset)
var AOI = ee.Geometry.Rectangle([39.05, -6.95, 39.45, -6.65]);

var ANALYSIS_YEARS = [2005, 2010, 2015, 2020, 2026];

// Dynamic World is available from 2015; for earlier years use Landsat built-up proxy
function getDynamicWorldLabels(year) {
  var start = year + '-06-01';
  var end = year + '-09-30';  // Dry season for East Africa

  var dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
    .filterBounds(AOI)
    .filterDate(start, end)
    .select('label');

  // Mode (most frequent class) over the dry season
  var dwMode = dw.reduce(ee.Reducer.mode());

  // Built-up mask: class 6 (built) or 7 (bare ground in settlement context)
  var builtMask = dwMode.eq(6).or(dwMode.eq(7));

  // Confidence filter using DW probability bands
  var dwProb = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
    .filterBounds(AOI)
    .filterDate(start, end)
    .select(['built', 'bare']);

  var avgProb = dwProb.mean();
  var confidentBuilt = builtMask.and(avgProb.select('built').gt(0.4));

  return confidentBuilt.selfMask().rename('informal_label');
}

// For pre-2015 years: use NDBI + NDVI threshold proxy from Landsat
function getLandsatBuiltProxy(year) {
  var start = year + '-06-01';
  var end = year + '-09-30';

  var l7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2')
    .filterBounds(AOI).filterDate(start, end)
    .filter(ee.Filter.lt('CLOUD_COVER', 30));

  var l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterBounds(AOI).filterDate(start, end)
    .filter(ee.Filter.lt('CLOUD_COVER', 30));

  var collection = year < 2013 ? l7 : l8.merge(l7);

  function addIndices(img) {
    var ndvi = img.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI');
    var ndbi = img.normalizedDifference(['SR_B6', 'SR_B5']).rename('NDBI');
    return img.addBands([ndvi, ndbi]);
  }

  var composite = collection.map(addIndices).median();
  // Informal settlement proxy: high NDBI, low NDVI
  return composite.select('NDBI').gt(0.1)
    .and(composite.select('NDVI').lt(0.35))
    .selfMask()
    .rename('informal_label');
}

// Process each year
ANALYSIS_YEARS.forEach(function(year) {
  var labels = year >= 2015
    ? getDynamicWorldLabels(year)
    : getLandsatBuiltProxy(year);

  Map.addLayer(labels.clip(AOI), { palette: ['red'] }, 'Labels ' + year, false);

  // Export vectorized labels
  Export.table.toDrive({
    collection: labels.clip(AOI).reduceToVectors({
      geometry: AOI,
      scale: 30,
      maxPixels: 1e10,
      bestEffort: true,
      geometryType: 'polygon',
      eightConnected: false,
      labelProperty: 'informal_label',
      reducer: ee.Reducer.countEvery()
    }),
    description: 'DarInformal_Labels_' + year,
    folder: 'DarInformal_GEE_Exports',
    fileFormat: 'GeoJSON'
  });
});

print('Dynamic World label extraction complete. Check Tasks tab for exports.');
