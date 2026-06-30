/**
 * DarInformal — Landsat 5 + 7 Early Years
 * Script 02: Dry-season median composite + spectral indices export
 *
 * Exports per year:
 *   - RGB composite GeoTIFF (visual QA)
 *   - NDVI / NDBI / BSI stack GeoTIFF
 */

// ── Shared config ──────────────────────────────────────────────────────────
var AOI = ee.Geometry.Rectangle([39.05, -6.95, 39.45, -6.65]);
var EARLY_YEARS = [2005, 2010];
var DRY_START = '-05-01';
var DRY_END = '-10-31';
var MAX_CLOUD_COVER = 40;
var EXPORT_SCALE = 30;
var DRIVE_FOLDER = 'DarInformal_L5L7_EarlyYears';

var L5 = 'LANDSAT/LT05/C02/T1_L2';
var L7 = 'LANDSAT/LE07/C02/T1_L2';

// ── Helpers ────────────────────────────────────────────────────────────────

function getMergedCollection(year) {
  var l5 = ee.ImageCollection(L5)
    .filterBounds(AOI).filterDate(year + DRY_START, year + DRY_END)
    .filter(ee.Filter.lt('CLOUD_COVER', MAX_CLOUD_COVER));
  var l7 = ee.ImageCollection(L7)
    .filterBounds(AOI).filterDate(year + DRY_START, year + DRY_END)
    .filter(ee.Filter.lt('CLOUD_COVER', MAX_CLOUD_COVER));
  return l5.merge(l7);
}

function maskLandsatL2(image) {
  var qa = image.select('QA_PIXEL');
  return image.updateMask(
    qa.bitwiseAnd(1 << 3).eq(0).and(qa.bitwiseAnd(1 << 4).eq(0))
  );
}

function computeIndices(image) {
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

function getYearlyIndices(year) {
  return getMergedCollection(year)
    .map(computeIndices)
    .median()
    .select(['NDVI', 'NDBI', 'BSI'])
    .clip(AOI);
}

function getRgbComposite(year) {
  var composite = getMergedCollection(year)
    .map(maskLandsatL2)
    .median();
  return applyScale(composite)
    .select(['SR_B4', 'SR_B3', 'SR_B2'])
    .clip(AOI);
}

function applyScale(image) {
  return image.select('SR_B.*').multiply(0.0000275).add(-0.2);
}

// ── Export ─────────────────────────────────────────────────────────────────

Map.centerObject(AOI, 11);

EARLY_YEARS.forEach(function(year) {
  var indices = getYearlyIndices(year);
  var rgb = getRgbComposite(year);

  Map.addLayer(indices.select('NDVI'),
    {min: -0.1, max: 0.7, palette: ['red', 'yellow', 'green']},
    'NDVI ' + year, false);
  Map.addLayer(indices.select('NDBI'),
    {min: -0.2, max: 0.4, palette: ['white', 'brown']},
    'NDBI ' + year, false);

  Export.image.toDrive({
    image: rgb.toFloat(),
    description: 'DarInformal_L5L7_RGB_' + year,
    folder: DRIVE_FOLDER,
    fileNamePrefix: 'rgb_' + year,
    region: AOI,
    scale: EXPORT_SCALE,
    maxPixels: 1e10,
    crs: 'EPSG:4326'
  });

  Export.image.toDrive({
    image: indices.toFloat(),
    description: 'DarInformal_L5L7_Indices_' + year,
    folder: DRIVE_FOLDER,
    fileNamePrefix: 'indices_' + year,
    region: AOI,
    scale: EXPORT_SCALE,
    maxPixels: 1e10,
    crs: 'EPSG:4326'
  });

  print('Queued RGB + indices export for', year);
});

print('Check Tasks tab for DarInformal_L5L7_RGB_* and DarInformal_L5L7_Indices_*');
