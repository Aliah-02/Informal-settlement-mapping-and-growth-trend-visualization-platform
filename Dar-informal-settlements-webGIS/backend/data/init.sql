-- DarInformal PostGIS initialization script
-- Creates spatial schema for future direct PostGIS storage

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Settlements table (for future direct DB ingestion from GEE exports)
CREATE TABLE IF NOT EXISTS settlements (
    id SERIAL PRIMARY KEY,
    settlement_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255),
    year INTEGER NOT NULL,
    isi_score FLOAT CHECK (isi_score >= 0 AND isi_score <= 1),
    risk_level VARCHAR(10) CHECK (risk_level IN ('low', 'medium', 'high')),
    area_ha FLOAT,
    population_proxy INTEGER,
    ndbi FLOAT,
    ndvi FLOAT,
    bsi FLOAT,
    fragmentation_index FLOAT,
    geom GEOMETRY(MultiPolygon, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_settlements_year ON settlements(year);
CREATE INDEX IF NOT EXISTS idx_settlements_risk ON settlements(risk_level);
CREATE INDEX IF NOT EXISTS idx_settlements_geom ON settlements USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_settlements_isi ON settlements(isi_score);

-- Yearly metrics summary table
CREATE TABLE IF NOT EXISTS yearly_metrics (
    id SERIAL PRIMARY KEY,
    year INTEGER UNIQUE NOT NULL,
    total_settlements INTEGER,
    total_area_ha FLOAT,
    average_isi FLOAT,
    high_risk_area_ha FLOAT,
    medium_risk_area_ha FLOAT,
    low_risk_area_ha FLOAT,
    population_proxy_total INTEGER,
    computed_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE settlements IS 'Informal settlement polygons with ISI attributes for Dar es Salaam';
COMMENT ON TABLE yearly_metrics IS 'Pre-computed yearly analytics for dashboard performance';
