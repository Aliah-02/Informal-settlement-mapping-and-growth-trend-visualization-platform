#!/usr/bin/env bash
# Import all GEE-exported GeoJSON files into PostGIS
set -euo pipefail
cd "$(dirname "$0")/../backend"
python scripts/import_geojson_to_postgis.py --all
python scripts/compute_yearly_metrics.py
echo "Done. Verify with: psql -c 'SELECT year, COUNT(*) FROM settlements GROUP BY year ORDER BY year'"
