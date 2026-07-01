# GeoServer Configuration

GeoServer serves **WMS/WFS** layers directly from the PostGIS `settlements` table.

## Docker (automatic)

`docker compose up` runs `geoserver-setup` which:

1. Creates workspace `darinformal`
2. Connects PostGIS datastore
3. Publishes `settlements` layer
4. Uploads `styles/settlements_risk.sld` (ISI risk colors)

## Manual setup

```bash
pip install requests
GEOSERVER_URL=http://localhost:8080/geoserver \
POSTGRES_HOST=localhost \
python scripts/setup_geoserver.py
```

## WMS URL (via Nginx proxy)

```
http://localhost/geoserver/darinformal/wms
  ?service=WMS&version=1.1.1&request=GetMap
  &layers=darinformal:settlements
  &styles=settlements_risk
  &CQL_FILTER=year=2020
  &bbox=39.05,-6.95,39.45,-6.65
  &width=800&height=600&srs=EPSG:4326&format=image/png&transparent=true
```

## Admin UI

- URL: http://localhost:8080/geoserver/web/
- User: `admin` / Password: `geoserver` (change in `.env`)

## Styles

| File | Purpose |
|------|---------|
| `styles/settlements_risk.sld` | Choropleth by `risk_level` (low/medium/high) |

Colors match the DarInformal frontend: `#22c55e`, `#f59e0b`, `#ef4444`.
