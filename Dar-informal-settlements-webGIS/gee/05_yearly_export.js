/**
 * GEE Script 05: Yearly GeoJSON + GeoTIFF Export Pipeline
 *
 * Complete export workflow for DarInformal platform:
 *   1. Vectorize ISI-classified settlement polygons
 *   2. Attach spectral properties to each feature
 *   3. Export GeoJSON (for API) + GeoTIFF (for raster analysis)
 *
 * After export: download from Google Drive → place in backend/data/geojson/
 */

var AOI = ee.Geometry.Rectangle([39.05, -6.95, 39.45, -6.65]);
var ANALYSIS_YEARS = [2005, 2010, 2015, 2020, 2026];
var EXPORT_SCALE = 30;
var MIN_AREA_M2 = 5000;  // Minimum settlement polygon area (0.5 ha)

function getYearlyComposite(year) {
  var start = year + '-06-01';
  var end = year + '-09-30';

  var ls = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterBounds(AOI).filterDate(start, end)
    .filter(ee.Filter.lt('CLOUD_COVER', 25));

  var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(AOI).filterDate(start, end)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20));

  var collection = year >= 2017 ? ls.merge(s2) : ls;
  return collection.median().clip(AOI);
}

function computeAllIndices(image) {
  var scaled = image.select('SR_B.*').multiply(0.0000275).add(-0.2);
  var ndvi = scaled.normalizedDifference(['SR_B5', 'SR_B4']);
  var ndbi = scaled.normalizedDifference(['SR_B6', 'SR_B5']);
  var bsi = scaled.select('SR_B6').add(scaled.select('SR_B4'))
    .subtract(scaled.select('SR_B5')).add(scaled.select('SR_B2'))
    .divide(scaled.select('SR_B6').add(scaled.select('SR_B4'))
      .add(scaled.select('SR_B5')).add(scaled.select('SR_B2')));

  var ndbiN = ndbi.subtract(-0.5).divide(1.3).clamp(0, 1);
  var ndviInv = ee.Image(1).subtract(ndvi.subtract(-0.2).divide(1.0).clamp(0, 1));
  var bsiN = bsi.clamp(0, 1);

  var builtMask = ndbiN.gt(0.25).and(ndviInv.gt(0.35));
  var kernel = ee.Kernel.square(3);
  var frag = builtMask.focal_max(kernel).subtract(builtMask.focal_min(kernel))
    .focal_mean(kernel).clamp(0, 1);

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

  // Filter small polygons
  vectors = vectors.filter(ee.Filter.gt('area', MIN_AREA_M2));

  // Attach spectral properties via zonal statistics
  var withStats = isiImage.reduceRegions({
    collection: vectors,
    reducer: ee.Reducer.mean(),
    scale: EXPORT_SCALE
  });

  // Add metadata properties
  return withStats.map(function(feature) {
    var isi = ee.Number(feature.get('isi_score'));
    var riskLevel = isi.lt(0.2).multiply(0)  // low
      .add(isi.gte(0.2).and(isi.lte(0.5)).multiply(1))  // medium
      .add(isi.gt(0.5).multiply(2));  // high

    var riskLabels = ['low', 'medium', 'high'];
    var riskLabel = riskLevel.format('%.0f').split('').map(function(v) {
      return ee.String(ee.Algorithms.If(ee.Number(v).eq(0), 'low',
        ee.Algorithms.If(ee.Number(v).eq(1), 'medium', 'high')));
    }).get(0);

    var areaHa = ee.Number(feature.geometry().area()).divide(10000);
    var popProxy = areaHa.multiply(8500).multiply(isi.multiply(0.6).add(0.4));

    return feature.set({
      'id': ee.String('DAR-').cat(ee.String(year)).cat('-').cat(
        ee.String(feature.get('system:index')).slice(0, 4)),
      'name': ee.String('Settlement ').cat(ee.String(feature.get('system:index'))),
      'year': year,
      'risk_level': riskLabel,
      'area_ha': areaHa,
      'population_proxy': popProxy.int()
    });
  });
}

// Main export loop
ANALYSIS_YEARS.forEach(function(year) {
  print('Processing year:', year);

  var composite = getYearlyComposite(year);
  var indices = computeAllIndices(composite);
  var settlements = vectorizeSettlements(indices, year);

  // Export GeoJSON
  Export.table.toDrive({
    collection: settlements,
    description: 'DarInformal_Settlements_' + year,
    folder: 'DarInformal_GEE_Exports',
    fileNamePrefix: 'settlements_' + year,
    fileFormat: 'GeoJSON'
  });

  // Export GeoTIFF raster stack
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
print('After export completes:');
print('1. Download GeoJSON from Google Drive');
print('2. Rename to settlements_YYYY.geojson');
print('3. Place in backend/data/geojson/');
print('4. Restart the DarInformal API');
