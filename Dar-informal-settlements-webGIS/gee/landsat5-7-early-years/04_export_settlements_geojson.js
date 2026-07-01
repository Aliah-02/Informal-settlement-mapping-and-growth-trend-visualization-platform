/**
 * DarInformal — Landsat 5 + 7 Early Years
 * Script 04: Full pipeline — collect, classify, export settlements (2005 & 2010)
 *
 * ★ RECOMMENDED: Run this single script for complete GeoJSON + raster export.
 *
 * Outputs (Google Drive → DarInformal_L5L7_EarlyYears):
 *   settlements_2005.geojson
 *   settlements_2010.geojson
 *   darinformal_2005.tif  (ISI stack)
 *   darinformal_2010.tif  (ISI stack)
 */

// ── Config ─────────────────────────────────────────────────────────────────
var AOI = ee.Geometry.Rectangle([39.05, -6.95, 39.45, -6.65]);
var EARLY_YEARS = [2005, 2010];
var DRY_START = '-05-01';
var DRY_END = '-10-31';
var MAX_CLOUD_COVER = 40;
var EXPORT_SCALE = 30;
var MIN_AREA_M2 = 5000;
var ISI_THRESHOLD = 0.15;
var FOCAL_RADIUS = 1;
var DRIVE_FOLDER = 'DarInformal_L5L7_EarlyYears';

var L5 = 'LANDSAT/LT05/C02/T1_L2';
var L7 = 'LANDSAT/LE07/C02/T1_L2';

// ── Landsat 5 + 7 collection ───────────────────────────────────────────────

function getMergedCollection(year) {
  var l5 = ee.ImageCollection(L5)
    .filterBounds(AOI)
    .filterDate(year + DRY_START, year + DRY_END)
    .filter(ee.Filter.lt('CLOUD_COVER', MAX_CLOUD_COVER));
  var l7 = ee.ImageCollection(L7)
    .filterBounds(AOI)
    .filterDate(year + DRY_START, year + DRY_END)
    .filter(ee.Filter.lt('CLOUD_COVER', MAX_CLOUD_COVER));
  return l5.merge(l7);
}

function maskLandsatL2(image) {
  var qa = image.select('QA_PIXEL');
  return image.updateMask(
    qa.bitwiseAnd(1 << 3).eq(0).and(qa.bitwiseAnd(1 << 4).eq(0))
  );
}

function tagSensor(image) {
  var sat = ee.String(image.get('SPACECRAFT_ID'));
  return image.set('sensor', sat);
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
  var count = getMergedCollection(year).size();
  print('Year', year, '— merged L5+L7 scenes:', count);
  return getMergedCollection(year)
    .map(tagSensor)
    .map(computeIndices)
    .median()
    .select(['NDVI', 'NDBI', 'BSI'])
    .clip(AOI);
}

// ── ISI ──────────────────────────────────────────────────────────────────────

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

  var isi = ndbiN.multiply(0.3)
    .add(ndviInv.multiply(0.25))
    .add(bsiN.multiply(0.2))
    .add(frag.multiply(0.25))
    .clamp(0, 1);

  return ee.Image.cat([
    isi.rename('isi_score'),
    ndbi.rename('ndbi'),
    ndvi.rename('ndvi'),
    bsiN.rename('bsi'),
    frag.rename('fragmentation_index'),
    builtMask.rename('built_mask')
  ]);
}

// ── Vectorize ────────────────────────────────────────────────────────────────

function vectorizeSettlements(isiImage, year) {
  var settlementMask = isiImage.select('isi_score').gt(ISI_THRESHOLD);

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
      'population_proxy': popProxy.int(),
      'data_source': 'Landsat5_Landsat7'
    });
  });
}

// ── Main export loop ─────────────────────────────────────────────────────────

Map.centerObject(AOI, 11);
Map.addLayer(AOI, {color: 'yellow'}, 'AOI', false);

EARLY_YEARS.forEach(function(year) {
  print('═══ Processing', year, '(L5 + L7) ═══');

  var indices = getYearlyIndices(year);
  var stack = computeISIStack(indices);
  var settlements = vectorizeSettlements(stack, year);

  Map.addLayer(stack.select('isi_score'),
    {min: 0, max: 1, palette: ['green', 'yellow', 'red']},
    'ISI ' + year, year === 2010);

  // GeoJSON → backend/data/geojson/
  Export.table.toDrive({
    collection: settlements,
    description: 'DarInformal_L5L7_Settlements_' + year,
    folder: DRIVE_FOLDER,
    fileNamePrefix: 'settlements_' + year,
    fileFormat: 'GeoJSON'
  });

  // Full ISI raster stack
  Export.image.toDrive({
    image: stack.toFloat(),
    description: 'DarInformal_L5L7_Raster_' + year,
    folder: DRIVE_FOLDER,
    fileNamePrefix: 'darinformal_' + year,
    region: AOI,
    scale: EXPORT_SCALE,
    maxPixels: 1e10,
    crs: 'EPSG:4326'
  });
});

print('');
print('══════════════════════════════════════════════');
print('DarInformal L5+L7 Early Years Export');
print('Years: 2005, 2010');
print('Drive folder:', DRIVE_FOLDER);
print('');
print('After Tasks complete:');
print('  1. Download settlements_2005.geojson & settlements_2010.geojson');
print('  2. Place in backend/data/geojson/');
print('  3. Restart DarInformal API');
print('══════════════════════════════════════════════');
