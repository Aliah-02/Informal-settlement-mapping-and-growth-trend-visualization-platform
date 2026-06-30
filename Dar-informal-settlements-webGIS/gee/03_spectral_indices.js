/**
 * GEE Script 03: Spectral Indices Computation (NDVI, NDBI, BSI)
 *
 * Computes yearly spectral indices for Dar es Salaam using:
 *   - Landsat 5/7 (2005–2012)
 *   - Landsat 8 (2013–2020)
 *   - Sentinel-2 + Landsat 9 (2021–2026)
 */

var AOI = ee.Geometry.Rectangle([39.05, -6.95, 39.45, -6.65]);
var ANALYSIS_YEARS = [2005, 2010, 2015, 2020, 2026];
var TARGET_SCALE = 30;  // meters

function getLandsatCollection(year) {
  var start = year + '-06-01';
  var end = year + '-09-30';

  if (year <= 2011) {
    return ee.ImageCollection('LANDSAT/LE07/C02/T1_L2')
      .filterBounds(AOI).filterDate(start, end)
      .filter(ee.Filter.lt('CLOUD_COVER', 25));
  }
  return ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterBounds(AOI).filterDate(start, end)
    .filter(ee.Filter.lt('CLOUD_COVER', 25));
}

function getSentinelCollection(year) {
  var start = year + '-06-01';
  var end = year + '-09-30';
  return ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(AOI).filterDate(start, end)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20));
}

function applyScaleFactors(image) {
  var optical = image.select('SR_B.*').multiply(0.0000275).add(-0.2);
  return image.addBands(optical, null, true);
}

function computeLandsatIndices(image) {
  image = applyScaleFactors(image);
  var ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI');
  var ndbi = image.normalizedDifference(['SR_B6', 'SR_B5']).rename('NDBI');
  var blue = image.select('SR_B2');
  var red = image.select('SR_B4');
  var nir = image.select('SR_B5');
  var swir = image.select('SR_B6');
  // Bare Soil Index: ((SWIR + RED) - NIR + BLUE) / ((SWIR + RED) + NIR + BLUE)
  var bsi = swir.add(red).subtract(nir).add(blue)
    .divide(swir.add(red).add(nir).add(blue))
    .rename('BSI');
  return image.addBands([ndvi, ndbi, bsi]);
}

function computeSentinelIndices(image) {
  var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
  var ndbi = image.normalizedDifference(['B11', 'B8']).rename('NDBI');
  var bsi = image.select('B11').add(image.select('B4'))
    .subtract(image.select('B8')).add(image.select('B2'))
    .divide(image.select('B11').add(image.select('B4'))
      .add(image.select('B8')).add(image.select('B2')))
    .rename('BSI');
  return image.addBands([ndvi, ndbi, bsi]);
}

function getYearlyIndices(year) {
  var indices;
  if (year >= 2017) {
    var s2 = getSentinelCollection(year).map(computeSentinelIndices);
    var ls = getLandsatCollection(year).map(computeLandsatIndices);
    indices = s2.merge(ls);
  } else {
    indices = getLandsatCollection(year).map(computeLandsatIndices);
  }
  return indices.median().select(['NDVI', 'NDBI', 'BSI']).clip(AOI);
}

// Process and export each year
ANALYSIS_YEARS.forEach(function(year) {
  var indices = getYearlyIndices(year);

  // Visualization
  Map.addLayer(indices.select('NDVI'), { min: -0.2, max: 0.8, palette: ['red', 'yellow', 'green'] },
    'NDVI ' + year, false);
  Map.addLayer(indices.select('NDBI'), { min: -0.3, max: 0.5, palette: ['white', 'brown'] },
    'NDBI ' + year, false);

  // Export GeoTIFF
  Export.image.toDrive({
    image: indices.toFloat(),
    description: 'DarInformal_Indices_' + year,
    folder: 'DarInformal_GEE_Exports',
    fileNamePrefix: 'indices_' + year,
    region: AOI,
    scale: TARGET_SCALE,
    maxPixels: 1e10,
    crs: 'EPSG:4326'
  });
});

Map.centerObject(AOI, 11);
print('Spectral indices computation queued. Check Tasks tab.');
