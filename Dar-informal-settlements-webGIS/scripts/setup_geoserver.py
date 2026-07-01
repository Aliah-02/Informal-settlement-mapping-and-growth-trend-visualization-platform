#!/usr/bin/env python3
"""Configure GeoServer workspace, PostGIS datastore, and settlements layer.

Run after GeoServer container is healthy:
    python scripts/setup_geoserver.py

Environment variables (with defaults for Docker Compose):
    GEOSERVER_URL, GEOSERVER_USER, GEOSERVER_PASSWORD
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
"""

from __future__ import annotations

import os
import sys
import time

import requests
from requests.auth import HTTPBasicAuth

GEOSERVER_URL = os.getenv("GEOSERVER_URL", "http://localhost:8080/geoserver")
GEOSERVER_USER = os.getenv("GEOSERVER_USER", "admin")
GEOSERVER_PASSWORD = os.getenv("GEOSERVER_PASSWORD", "geoserver")
WORKSPACE = os.getenv("GEOSERVER_WORKSPACE", "darinformal")
LAYER_NAME = os.getenv("GEOSERVER_LAYER", "settlements")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "darinformal")
POSTGRES_USER = os.getenv("POSTGRES_USER", "darinformal")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "darinformal")

AUTH = HTTPBasicAuth(GEOSERVER_USER, GEOSERVER_PASSWORD)
HEADERS_JSON = {"Content-Type": "application/json"}
HEADERS_XML = {"Content-Type": "text/xml"}
MAX_RETRIES = 30
RETRY_DELAY = 5


def wait_for_geoserver():
    """Wait until GeoServer REST API is reachable."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(f"{GEOSERVER_URL}/rest/about/version", auth=AUTH, timeout=5)
            if r.status_code == 200:
                print(f"GeoServer ready (attempt {attempt})")
                return
        except requests.RequestException:
            pass
        print(f"Waiting for GeoServer... ({attempt}/{MAX_RETRIES})")
        time.sleep(RETRY_DELAY)
    print("ERROR: GeoServer not reachable", file=sys.stderr)
    sys.exit(1)


def create_workspace():
    url = f"{GEOSERVER_URL}/rest/workspaces"
    payload = {"workspace": {"name": WORKSPACE}}
    r = requests.post(url, json=payload, auth=AUTH, headers=HEADERS_JSON)
    if r.status_code in (200, 201):
        print(f"  ✓ Workspace '{WORKSPACE}' created")
    elif r.status_code == 409:
        print(f"  · Workspace '{WORKSPACE}' already exists")
    else:
        print(f"  ! Workspace response {r.status_code}: {r.text}")


def create_postgis_datastore():
    url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/datastores"
    xml = f"""<dataStore>
  <name>postgis</name>
  <type>PostGIS</type>
  <enabled>true</enabled>
  <connectionParameters>
    <entry key="host">{POSTGRES_HOST}</entry>
    <entry key="port">{POSTGRES_PORT}</entry>
    <entry key="database">{POSTGRES_DB}</entry>
    <entry key="user">{POSTGRES_USER}</entry>
    <entry key="passwd">{POSTGRES_PASSWORD}</entry>
    <entry key="dbtype">postgis</entry>
    <entry key="schema">public</entry>
    <entry key="Expose primary keys">true</entry>
    <entry key="validate connections">true</entry>
    <entry key="max connections">10</entry>
    <entry key="min connections">1</entry>
  </connectionParameters>
</dataStore>"""
    r = requests.post(url, data=xml, auth=AUTH, headers=HEADERS_XML)
    if r.status_code in (200, 201):
        print("  ✓ PostGIS datastore created")
    elif r.status_code == 409:
        print("  · PostGIS datastore already exists — updating")
        requests.put(
            f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/datastores/postgis",
            data=xml, auth=AUTH, headers=HEADERS_XML,
        )
    else:
        print(f"  ! Datastore response {r.status_code}: {r.text}")


def publish_layer():
    url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/datastores/postgis/featuretypes"
    xml = f"""<featureType>
  <name>{LAYER_NAME}</name>
  <nativeName>settlements</nativeName>
  <title>Dar es Salaam Informal Settlements</title>
  <abstract>ISI-classified informal settlement polygons from PostGIS</abstract>
  <enabled>true</enabled>
  <srs>EPSG:4326</srs>
</featureType>"""
    r = requests.post(url, data=xml, auth=AUTH, headers=HEADERS_XML)
    if r.status_code in (200, 201):
        print(f"  ✓ Layer '{LAYER_NAME}' published")
    elif r.status_code == 409:
        print(f"  · Layer '{LAYER_NAME}' already exists")
    else:
        print(f"  ! Layer response {r.status_code}: {r.text}")


def upload_style():
    sld_path = os.path.join(os.path.dirname(__file__), "..", "geoserver", "styles", "settlements_risk.sld")
    if not os.path.exists(sld_path):
        print(f"  ! SLD not found at {sld_path}")
        return

    with open(sld_path, "r", encoding="utf-8") as f:
        sld_content = f.read()

    style_name = "settlements_risk"
    url = f"{GEOSERVER_URL}/rest/styles"
    r = requests.post(
        url,
        params={"name": style_name},
        data=sld_content,
        auth=AUTH,
        headers={"Content-Type": "application/vnd.ogc.sld+xml"},
    )
    if r.status_code in (200, 201):
        print(f"  ✓ Style '{style_name}' uploaded")
    elif r.status_code == 409:
        requests.put(
            f"{GEOSERVER_URL}/rest/styles/{style_name}",
            data=sld_content,
            auth=AUTH,
            headers={"Content-Type": "application/vnd.ogc.sld+xml"},
        )
        print(f"  · Style '{style_name}' updated")
    else:
        print(f"  ! Style response {r.status_code}: {r.text}")

    # Assign style as default for layer
    layer_url = f"{GEOSERVER_URL}/rest/layers/{WORKSPACE}:{LAYER_NAME}"
    layer_xml = f"""<layer>
  <defaultStyle>
    <name>{style_name}</name>
  </defaultStyle>
</layer>"""
    requests.put(layer_url, data=layer_xml, auth=AUTH, headers=HEADERS_XML)
    print(f"  ✓ Default style assigned to {WORKSPACE}:{LAYER_NAME}")


def main():
    print("=== DarInformal GeoServer Setup ===")
    wait_for_geoserver()
    create_workspace()
    create_postgis_datastore()
    publish_layer()
    upload_style()
    print("")
    print(f"WMS: {GEOSERVER_URL}/{WORKSPACE}/wms")
    print(f"Layer: {WORKSPACE}:{LAYER_NAME}")
    print(f"CQL filter example: year=2020")


if __name__ == "__main__":
    main()
