/**
 * DarInformal — Landsat 5 + 7 Early Years
 * Script 03: ISI raster computation and export (2005 & 2010)
 *
 * ISI = 0.3*NDBI + 0.25*(1-NDVI) + 0.2*BSI + 0.25*fragmentation
 */

// ── Shared config ──────────────────────────────────────────────────────────
var AOI = ee.Geometry.Rectangle([39.05, -6.95, 39.45, -6.65]);
var EARLY_YEARS = [2005, 2010];
var DRY_START = '-05-01';
var DRY_END = '-10-31';
var MAX_CLOUD_COVER = 40;
var EXPORT_SCALE = 30;
var FOCAL_RADIUS = 1;
var DRIVE_FOLDER = 'DarInformal_L5L7_EarlyYears';

var L5 = 'LANDSAT/LT05/C02/T1_L2';
var L7 = 'LANDSAT/LE07/C02/T1_L2';

// ISI weights (match backend/config.py)
var W_NDBI = 0.3;
var W_NDVI_INV = 0.25;
var W_BSI = 0.2;
var W_FRAG = 0.25;

// ── Collection + indices ───────────────────────────────────────────────────

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

// ── ISI stack ──────────────────────────────────────────────────────────────

function computeISIStack(indicesImage) {
  var ndvi = indicesImage.select('NDVI');
  var ndbi = indicesImage.select('NDBI');
  var bsi = indicesImage.select('BSI');

  var ndbiN = ndbi.subtract(-0.5).divide(1.3).clamp(0, 1);
  var ndviInv = ee.Image(1).subtract(ndvi.subtract(-0.2).divide(1.0).clamp(0, 1));
  var bsiN = bsi.clamp(0, 1);

  var builtMask = ndbiN.gt(0.25).and(ndviInv.gt(0.35));
  var focalOpts = {radius: FOCAL_RADIUS, units: 'pixels'};
  var frag = builtMask.focal_max(focalOpts)
    .subtract(builtMask.focal_min(focalOpts))
    .focal_mean(focalOpts)
    .clamp(0, 1);

  var isi = ndbiN.multiply(W_NDBI)
    .add(ndviInv.multiply(W_NDVI_INV))
    .add(bsiN.multiply(W_BSI))
    .add(frag.multiply(W_FRAG))
    .clamp(0, 1);

  var riskClass = isi
    .where(isi.lt(0.2), 1)
    .where(isi.gte(0.2).and(isi.lte(0.5)), 2)
    .where(isi.gt(0.5), 3)
    .rename('risk_class');

  return ee.Image.cat([
    isi.rename('isi_score'),
    riskClass,
    ndbi.rename('ndbi'),
    ndvi.rename('ndvi'),
    bsiN.rename('bsi'),
    frag.rename('fragmentation_index'),
    builtMask.rename('built_mask')
  ]);
}

// ── Export ─────────────────────────────────────────────────────────────────

Map.centerObject(AOI, 11);
var riskPalette = ['22c55e', 'f59e0b', 'ef4444'];

EARLY_YEARS.forEach(function(year) {
  var indices = getYearlyIndices(year);
  var stack = computeISIStack(indices);

  Map.addLayer(stack.select('isi_score'),
    {min: 0, max: 1, palette: ['green', 'yellow', 'red']},
    'ISI ' + year, year === 2010);
  Map.addLayer(stack.select('risk_class'),
    {min: 1, max: 3, palette: riskPalette},
    'Risk ' + year, false);

  Export.image.toDrive({
    image: stack.toFloat(),
    description: 'DarInformal_L5L7_ISI_' + year,
    folder: DRIVE_FOLDER,
    fileNamePrefix: 'isi_' + year,
    region: AOI,
    scale: EXPORT_SCALE,
    maxPixels: 1e10,
    crs: 'EPSG:4326'
  });

  print('Queued ISI raster export for', year);
});

print('Exports → Google Drive folder:', DRIVE_FOLDER);
