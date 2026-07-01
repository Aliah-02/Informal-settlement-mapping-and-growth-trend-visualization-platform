# AGENTS.md

## Cursor Cloud specific instructions

The project lives in `Dar-informal-settlements-webGIS/`. It is a **Docker Compose–first WebGIS
platform** (DarInformal): PostGIS spatial DB + FastAPI backend + GeoServer WMS + a static Leaflet
frontend served through Nginx. Standard commands are documented in
`Dar-informal-settlements-webGIS/README.md` and `Dar-informal-settlements-webGIS/Makefile`; the
notes below only cover non-obvious, Cloud-specific caveats.

### Running the stack
- Docker Engine + compose plugin are pre-installed (snapshot), with the daemon configured for
  `fuse-overlayfs` storage. The daemon is **not auto-started** — start it once per session, e.g.
  `sudo dockerd` (run it in a background tmux session) or `sudo service docker start`.
- The `ubuntu` user is **not** in the `docker` group, so run docker with `sudo` (`sudo docker …`,
  `sudo docker compose …`).
- From `Dar-informal-settlements-webGIS/`: `cp -n .env.example .env`, then build/run with
  `sudo docker compose up --build -d`.
- URLs: web app `http://localhost` (Nginx), API docs `http://localhost:8000/docs`, API health
  `http://localhost:8000/api/health`, GeoServer `http://localhost:8080/geoserver` (`admin`/`geoserver`).

### Known gotchas (important)
- **`data-import` job is currently broken.** `backend/scripts/import_geojson_to_postgis.py` writes
  the geometry into a column named `geometry`, but the `settlements` table's geometry column is
  `geom`, so `to_postgis(..., if_exists="append")` fails with
  `find_srid() - could not find the corresponding SRID`. Because `api`, `geoserver`, and `nginx`
  all `depends_on: data-import (service_completed_successfully)`, a plain `docker compose up -d`
  **aborts**. This is an application bug, not an environment problem.
- **Workaround to run the app** until the import is fixed — start services without the dependency
  gate: `sudo docker compose up -d --no-deps postgis api geoserver nginx`. The FastAPI backend
  auto-falls back to reading the GeoJSON files in `backend/data/geojson/` when PostGIS is empty
  (health then reports `data_source: geojson`), so the product is fully usable: map, dashboard
  KPIs, time slider, and settlement popups all work.
- **Nginx needs GeoServer's DNS to exist.** `nginx/nginx.conf` uses a static `proxy_pass
  http://geoserver:8080`, so Nginx refuses to start (`host not found in upstream "geoserver"`)
  unless the `geoserver` container is running. Start `geoserver` before/with `nginx`.
- **Map source default is "Hybrid (WMS + API)"**, which relies on GeoServer having a published
  layer. Since the import failure leaves GeoServer/PostGIS empty, switch the legend's **"Map
  source" dropdown to "API GeoJSON"** to render the settlement polygons from the API.

### Dev workflow notes
- Backend code is bind-mounted into the `api` container and uvicorn runs with `--reload`, so Python
  edits hot-reload without a rebuild. Only rebuild images (`sudo docker compose build`) after
  changing `backend/requirements.txt` or a Dockerfile.
- A host Python venv is maintained at `Dar-informal-settlements-webGIS/backend/.venv` (created by
  the startup update script) for running the backend scripts / `uvicorn` locally per the README's
  non-Docker path and for editor tooling. The geo wheels (geopandas/shapely/rasterio) bundle
  GDAL/GEOS/PROJ, so no host GDAL system packages are required.
- There is **no automated test suite** and **no linter configured**. `make test-api` simply curls
  the health endpoint.
