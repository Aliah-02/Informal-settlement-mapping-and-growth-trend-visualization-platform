-- DarInformal PostGIS Schema
-- Central spatial database for informal settlement intelligence

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- ── Settlements (primary spatial layer from GEE GeoJSON exports) ─────────────

CREATE TABLE IF NOT EXISTS settlements (
    id SERIAL PRIMARY KEY,
    settlement_id VARCHAR(32) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL DEFAULT 'Settlement',
    year INTEGER NOT NULL,
    isi_score FLOAT CHECK (isi_score >= 0 AND isi_score <= 1),
    risk_level VARCHAR(10) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
    area_ha FLOAT CHECK (area_ha >= 0),
    population_proxy INTEGER CHECK (population_proxy >= 0),
    ndbi FLOAT,
    ndvi FLOAT,
    bsi FLOAT,
    fragmentation_index FLOAT,
    data_source VARCHAR(64) DEFAULT 'geojson_import',
    geom GEOMETRY(MultiPolygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_settlements_year ON settlements(year);
CREATE INDEX IF NOT EXISTS idx_settlements_risk ON settlements(risk_level);
CREATE INDEX IF NOT EXISTS idx_settlements_year_risk ON settlements(year, risk_level);
CREATE INDEX IF NOT EXISTS idx_settlements_isi ON settlements(isi_score);
CREATE INDEX IF NOT EXISTS idx_settlements_geom ON settlements USING GIST(geom);

-- ── Pre-computed yearly analytics (dashboard performance) ───────────────────

CREATE TABLE IF NOT EXISTS yearly_metrics (
    id SERIAL PRIMARY KEY,
    year INTEGER UNIQUE NOT NULL,
    total_settlements INTEGER NOT NULL DEFAULT 0,
    total_area_ha FLOAT NOT NULL DEFAULT 0,
    average_isi FLOAT NOT NULL DEFAULT 0,
    high_risk_area_ha FLOAT NOT NULL DEFAULT 0,
    medium_risk_area_ha FLOAT NOT NULL DEFAULT 0,
    low_risk_area_ha FLOAT NOT NULL DEFAULT 0,
    high_risk_count INTEGER NOT NULL DEFAULT 0,
    medium_risk_count INTEGER NOT NULL DEFAULT 0,
    low_risk_count INTEGER NOT NULL DEFAULT 0,
    population_proxy_total INTEGER NOT NULL DEFAULT 0,
    computed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_yearly_metrics_year ON yearly_metrics(year);

-- ── Change detection results (pre-computed or cached) ───────────────────────

CREATE TABLE IF NOT EXISTS change_detection (
    id SERIAL PRIMARY KEY,
    from_year INTEGER NOT NULL,
    to_year INTEGER NOT NULL,
    settlement_id VARCHAR(32),
    to_settlement_id VARCHAR(32),
    name VARCHAR(255),
    change_type VARCHAR(20) NOT NULL CHECK (
        change_type IN ('new', 'expanded', 'contracted', 'stable', 'disappeared')
    ),
    isi_score FLOAT,
    to_isi_score FLOAT,
    area_ha FLOAT,
    to_area_ha FLOAT,
    area_change_ha FLOAT,
    area_change_pct FLOAT,
    isi_change FLOAT,
    overlap_ratio FLOAT,
    population_proxy INTEGER,
    geom GEOMETRY(MultiPolygon, 4326),
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_change_record UNIQUE (from_year, to_year, settlement_id, change_type)
);

CREATE INDEX IF NOT EXISTS idx_change_years ON change_detection(from_year, to_year);
CREATE INDEX IF NOT EXISTS idx_change_type ON change_detection(change_type);
CREATE INDEX IF NOT EXISTS idx_change_geom ON change_detection USING GIST(geom);

-- ── Import audit log ────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS import_log (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    source_file VARCHAR(512),
    features_imported INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    message TEXT,
    imported_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── All-years view for analytics exports ─────────────────────────────────────

CREATE OR REPLACE VIEW v_settlements_all AS
SELECT
    id,
    settlement_id,
    name,
    year,
    isi_score,
    risk_level,
    area_ha,
    population_proxy,
    ndbi,
    ndvi,
    bsi,
    fragmentation_index,
    geom
FROM settlements;

COMMENT ON TABLE settlements IS 'Informal settlement polygons with ISI attributes — primary spatial store';
COMMENT ON TABLE yearly_metrics IS 'Pre-computed dashboard metrics per analysis year';
COMMENT ON TABLE change_detection IS 'Temporal settlement change records between analysis years';
COMMENT ON VIEW v_settlements_all IS 'All settlement polygons across analysis years';

-- ── Platform users & activity tracking ────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(120) NOT NULL,
    last_name VARCHAR(120) NOT NULL,
    mobile VARCHAR(32),
    company_name VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    session_token VARCHAR(64) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    ip_address VARCHAR(64),
    user_agent TEXT,
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_seen ON user_sessions(last_seen_at);

CREATE TABLE IF NOT EXISTS page_visits (
    id SERIAL PRIMARY KEY,
    session_token VARCHAR(64) NOT NULL,
    page_path VARCHAR(512) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    ip_address VARCHAR(64),
    visited_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_page_visits_session ON page_visits(session_token);
CREATE INDEX IF NOT EXISTS idx_page_visits_visited_at ON page_visits(visited_at);

CREATE TABLE IF NOT EXISTS download_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    user_email VARCHAR(255),
    session_token VARCHAR(64),
    report_type VARCHAR(64) NOT NULL,
    report_label VARCHAR(255) NOT NULL,
    ip_address VARCHAR(64),
    downloaded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_download_logs_user ON download_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_download_logs_downloaded_at ON download_logs(downloaded_at);
