/**
 * DarInformal — Landsat 5 + 7 Early Years
 * Script 01: Collect & preview L5/L7 scenes for 2005 and 2010
 *
 * Run first to verify scene availability before exporting.
 * Check Console output for scene counts per sensor.
 */

// ── Shared config ──────────────────────────────────────────────────────────
var AOI = ee.Geometry.Rectangle([39.05, -6.95, 39.45, -6.65]);
var EARLY_YEARS = [2005, 2010];
var DRY_START = '-05-01';
var DRY_END = '-10-31';
var MAX_CLOUD_COVER = 40;

var L5 = 'LANDSAT/LT05/C02/T1_L2';
var L7 = 'LANDSAT/LE07/C02/T1_L2';

// ── Collection helpers ─────────────────────────────────────────────────────

function getL5Collection(year) {
  return ee.ImageCollection(L5)
    .filterBounds(AOI)
    .filterDate(year + DRY_START, year + DRY_END)
    .filter(ee.Filter.lt('CLOUD_COVER', MAX_CLOUD_COVER));
}

function getL7Collection(year) {
  return ee.ImageCollection(L7)
    .filterBounds(AOI)
    .filterDate(year + DRY_START, year + DRY_END)
    .filter(ee.Filter.lt('CLOUD_COVER', MAX_CLOUD_COVER));
}

function getMergedCollection(year) {
  return getL5Collection(year).merge(getL7Collection(year));
}

function maskLandsatL2(image) {
  var qa = image.select('QA_PIXEL');
  var cloudMask = qa.bitwiseAnd(1 << 3).eq(0);
  var shadowMask = qa.bitwiseAnd(1 << 4).eq(0);
  return image.updateMask(cloudMask.and(shadowMask));
}

function applyScale(image) {
  return image.select('SR_B.*').multiply(0.0000275).add(-0.2);
}

function buildRgbComposite(year) {
  var collection = getMergedCollection(year).map(maskLandsatL2);
  var composite = collection.median();
  var scaled = applyScale(composite);
  return scaled.select(['SR_B4', 'SR_B3', 'SR_B2']).clip(AOI);
}

// ── Inspect scene counts ───────────────────────────────────────────────────

EARLY_YEARS.forEach(function(year) {
  var l5Count = getL5Collection(year).size();
  var l7Count = getL7Collection(year).size();
  var mergedCount = getMergedCollection(year).size();

  print('──── Year ' + year + ' ────');
  print('  Landsat 5 scenes :', l5Count);
  print('  Landsat 7 scenes :', l7Count);
  print('  Merged total     :', mergedCount);

  // List first 5 scene IDs for verification
  print('  Sample L7 IDs:', getL7Collection(year).limit(5).aggregate_array('system:index'));
  print('  Sample L5 IDs:', getL5Collection(year).limit(5).aggregate_array('system:index'));
});

// ── Map preview ────────────────────────────────────────────────────────────

Map.centerObject(AOI, 11);
Map.addLayer(AOI, {color: 'yellow'}, 'Dar es Salaam AOI', true);

EARLY_YEARS.forEach(function(year) {
  var rgb = buildRgbComposite(year);
  Map.addLayer(rgb,
    {min: 0.0, max: 0.3, bands: ['SR_B4', 'SR_B3', 'SR_B2']},
    'L5+L7 RGB ' + year,
    year === 2010  // show 2010 by default
  );
});

print('');
print('If merged total > 0 for both years, proceed to script 02 or 04.');
print('If counts are 0, increase MAX_CLOUD_COVER or widen DRY_START/DRY_END.');
