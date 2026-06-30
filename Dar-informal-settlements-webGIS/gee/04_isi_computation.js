/**
 * GEE Script 04: Informal Settlement Index (ISI) Computation
 *
 * ISI = (0.3 * NDBI) + (0.25 * (1 - NDVI)) + (0.2 * BSI) + (0.25 * fragmentation_index)
 *
 * Risk levels:
 *   Low:    ISI < 0.2  (Green)
 *   Medium: 0.2 <= ISI <= 0.5  (Yellow/Orange)
 *   High:   ISI > 0.5  (Red)
 */

var AOI = ee.Geometry.Rectangle([39.05, -6.95, 39.45, -6.65]);
var ANALYSIS_YEARS = [2005, 2010, 2015, 2020, 2026];

// ISI weights (must match backend config)
var W_NDBI = 0.3;
var W_NDVI_INV = 0.25;
var W_BSI = 0.2;
var W_FRAG = 0.25;

var ISI_LOW = 0.2;
var ISI_HIGH = 0.5;

function normalizeIndex(image, band, min, max) {
  return image.select(band).subtract(min).divide(max - min).clamp(0, 1);
}

function computeFragmentation(builtMask) {
  // Use morphological edge detection as fragmentation proxy
  var kernel = ee.Kernel.square({ radius: 1 });
  var dilated = builtMask.focal_max({ kernel: kernel, iterations: 1 });
  var eroded = builtMask.focal_min({ kernel: kernel, iterations: 1 });
  var edges = dilated.subtract(eroded);
  // Edge density as fragmentation index
  return edges.focal_mean({ kernel: ee.Kernel.square(3) }).rename('fragmentation');
}

function computeISI(year) {
  // Load pre-computed indices (from script 03) or compute inline
  var start = year + '-06-01';
  var end = year + '-09-30';

  var ls = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterBounds(AOI).filterDate(start, end)
    .filter(ee.Filter.lt('CLOUD_COVER', 25));

  var composite = ls.median();
  var scaled = composite.select('SR_B.*').multiply(0.0000275).add(-0.2);

  var ndvi = scaled.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI');
  var ndbi = scaled.normalizedDifference(['SR_B6', 'SR_B5']).rename('NDBI');
  var bsi = scaled.select('SR_B6').add(scaled.select('SR_B4'))
    .subtract(scaled.select('SR_B5')).add(scaled.select('SR_B2'))
    .divide(scaled.select('SR_B6').add(scaled.select('SR_B4'))
      .add(scaled.select('SR_B5')).add(scaled.select('SR_B2')))
    .rename('BSI');

  var indices = ee.Image.cat([ndvi, ndbi, bsi]).clip(AOI);

  // Normalize to [0, 1]
  var ndbiNorm = normalizeIndex(indices, 'NDBI', -0.5, 0.8);
  var ndviInv = ee.Image(1).subtract(normalizeIndex(indices, 'NDVI', -0.2, 0.8));
  var bsiNorm = normalizeIndex(indices, 'BSI', 0, 1);

  // Built-up mask for fragmentation
  var builtMask = ndbiNorm.gt(0.3).and(ndviInv.gt(0.4));
  var fragIndex = computeFragmentation(builtMask);

  // ISI computation
  var isi = ndbiNorm.multiply(W_NDBI)
    .add(ndviInv.multiply(W_NDVI_INV))
    .add(bsiNorm.multiply(W_BSI))
    .add(fragIndex.multiply(W_FRAG))
    .clamp(0, 1)
    .rename('ISI');

  // Risk classification
  var riskClass = isi
    .where(isi.lt(ISI_LOW), 1)       // Low = 1
    .where(isi.gte(ISI_LOW).and(isi.lte(ISI_HIGH)), 2)  // Medium = 2
    .where(isi.gt(ISI_HIGH), 3)       // High = 3
    .rename('risk_class');

  return ee.Image.cat([isi, riskClass, ndbiNorm.rename('NDBI_n'),
    ndviInv.rename('NDVI_inv'), bsiNorm.rename('BSI_n'), fragIndex])
    .clip(AOI);
}

var riskPalette = ['22c55e', 'f59e0b', 'ef4444'];  // Green, Orange, Red

ANALYSIS_YEARS.forEach(function(year) {
  var result = computeISI(year);
  var isi = result.select('ISI');
  var risk = result.select('risk_class');

  Map.addLayer(isi, { min: 0, max: 1, palette: ['green', 'yellow', 'red'] },
    'ISI ' + year, false);
  Map.addLayer(risk, { min: 1, max: 3, palette: riskPalette },
    'Risk ' + year, false);

  // Export ISI raster
  Export.image.toDrive({
    image: result.toFloat(),
    description: 'DarInformal_ISI_' + year,
    folder: 'DarInformal_GEE_Exports',
    fileNamePrefix: 'isi_' + year,
    region: AOI,
    scale: 30,
    maxPixels: 1e10,
    crs: 'EPSG:4326'
  });
});

Map.centerObject(AOI, 11);
print('ISI computation queued for all years.');
