/**
 * GEE Script 01: Dar es Salaam Area of Interest (AOI) Definition
 *
 * Run in Google Earth Engine Code Editor:
 * https://code.earthengine.google.com/
 *
 * Defines the metropolitan boundary for informal settlement analysis.
 */

// Dar es Salaam metropolitan bounding box
var DAR_BOUNDS = ee.Geometry.Rectangle([39.05, -6.95, 39.45, -6.65]);

// Refined AOI using GAUL admin boundaries (Level 2 — Dar es Salaam Region)
// Fallback to bounding box if GAUL not available
var gaul = ee.FeatureCollection('FAO/GAUL/2015/level2')
  .filter(ee.Filter.eq('ADM1_NAME', 'Dar es Salaam'));

var AOI = gaul.geometry().dissolve().intersection(DAR_BOUNDS, 1);

// Visualize
Map.centerObject(AOI, 11);
Map.addLayer(AOI, { color: 'blue' }, 'Dar es Salaam AOI', false);
Map.addLayer(DAR_BOUNDS, { color: 'red' }, 'Bounding Box', false);

// Export AOI as asset (run once)
/*
Export.table.toAsset({
  collection: ee.FeatureCollection([ee.Feature(AOI, { name: 'Dar_es_Salaam_AOI' })]),
  description: 'Dar_es_Salaam_AOI',
  assetId: 'projects/YOUR_PROJECT/assets/dar_es_salaam_aoi'
});
*/

print('AOI Area (km²):', AOI.area().divide(1e6));
print('AOI Bounds:', AOI.bounds());

// Export for use in subsequent scripts
exports.AOI = AOI;
exports.DAR_BOUNDS = DAR_BOUNDS;
