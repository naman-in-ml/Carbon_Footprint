-- CarbonProof initial schema. Run via Supabase dashboard SQL editor or:
--   supabase db push
-- Tables are created by these migrations only — never run create_all.

-- Projects
CREATE TABLE IF NOT EXISTS projects (
    id                BIGSERIAL PRIMARY KEY,
    verra_id          TEXT NOT NULL UNIQUE,
    name              TEXT NOT NULL,
    registry          TEXT NOT NULL DEFAULT 'Verra',
    pdd_url           TEXT,
    pdd_storage_path  TEXT,
    status            TEXT NOT NULL DEFAULT 'pending',
    country           TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_projects_verra_id ON projects(verra_id);

-- Extracted claims (Track A: Nugen document extraction)
CREATE TABLE IF NOT EXISTS extracted_claims (
    id                    BIGSERIAL PRIMARY KEY,
    project_id            BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    coordinates_raw       TEXT,
    geometry_wkt          TEXT,
    geocoding_method      TEXT,
    claimed_hectares      DOUBLE PRECISION,
    start_year            INTEGER,
    species               TEXT,
    baseline_method       TEXT,
    claimed_tco2          DOUBLE PRECISION,
    claimed_tco2_per_ha   DOUBLE PRECISION,
    monitoring_period     TEXT,
    extraction_confidence DOUBLE PRECISION,
    uncertainty_flags     JSONB,
    requires_review       BOOLEAN NOT NULL DEFAULT false,
    raw_nugen_response    JSONB,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_claims_project_id ON extracted_claims(project_id);

-- Satellite verifications (Track B: GEE + FIRMS + allometric)
CREATE TABLE IF NOT EXISTS satellite_verifications (
    id                       BIGSERIAL PRIMARY KEY,
    claim_id                 BIGINT NOT NULL REFERENCES extracted_claims(id) ON DELETE CASCADE,
    ndvi_before              DOUBLE PRECISION,
    ndvi_after_1yr           DOUBLE PRECISION,
    ndvi_after_3yr           DOUBLE PRECISION,
    ndvi_control             DOUBLE PRECISION,
    ndvi_trend               TEXT,
    planting_verified        TEXT,
    planting_confidence      DOUBLE PRECISION,
    ndvi_current             DOUBLE PRECISION,
    still_standing           TEXT,
    decline_detected_since   TEXT,
    likely_cause             TEXT,
    fire_events_detected     INTEGER,
    fire_dates               JSONB,
    estimated_biomass_tha    DOUBLE PRECISION,
    estimated_tco2           DOUBLE PRECISION,
    estimated_tco2_low       DOUBLE PRECISION,
    estimated_tco2_high      DOUBLE PRECISION,
    credit_delta_pct         DOUBLE PRECISION,
    credit_flag              TEXT,
    ndvi_time_series         JSONB,
    firms_raw                JSONB,
    gee_run_at               TIMESTAMPTZ,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_verifications_claim_id ON satellite_verifications(claim_id);

-- Credibility scores (Stage 5)
CREATE TABLE IF NOT EXISTS credibility_scores (
    id                 BIGSERIAL PRIMARY KEY,
    project_id         BIGINT NOT NULL UNIQUE REFERENCES projects(id) ON DELETE CASCADE,
    verification_id    BIGINT NOT NULL REFERENCES satellite_verifications(id),
    extraction_score   DOUBLE PRECISION NOT NULL,
    planting_score     DOUBLE PRECISION NOT NULL,
    permanence_score   DOUBLE PRECISION NOT NULL,
    credit_math_score  DOUBLE PRECISION NOT NULL,
    composite_score    DOUBLE PRECISION NOT NULL,
    risk_flag          TEXT NOT NULL,
    flag_reasons       JSONB,
    reviewed_by        TEXT,
    review_notes       TEXT,
    reviewed_at        TIMESTAMPTZ,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_scores_project_id ON credibility_scores(project_id);

-- Geocoding cache (Nominatim is rate-limited to 1 req/s; cache results here)
CREATE TABLE IF NOT EXISTS geocode_cache (
    id         BIGSERIAL PRIMARY KEY,
    query      TEXT NOT NULL UNIQUE,
    lat        DOUBLE PRECISION NOT NULL,
    lon        DOUBLE PRECISION NOT NULL,
    method     TEXT NOT NULL DEFAULT 'nominatim',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_geocode_cache_query ON geocode_cache(query);

-- Auto-update updated_at on projects
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_projects_updated_at ON projects;
CREATE TRIGGER trg_projects_updated_at
BEFORE UPDATE ON projects
FOR EACH ROW EXECUTE FUNCTION update_updated_at();