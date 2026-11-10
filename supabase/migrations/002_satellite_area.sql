-- Satellite-measured area fields + optional uploaded project boundary.
ALTER TABLE extracted_claims ADD COLUMN IF NOT EXISTS boundary_geojson JSONB;
ALTER TABLE satellite_verifications ADD COLUMN IF NOT EXISTS tree_cover_ha DOUBLE PRECISION;
ALTER TABLE satellite_verifications ADD COLUMN IF NOT EXISTS aoi_ha DOUBLE PRECISION;
ALTER TABLE satellite_verifications ADD COLUMN IF NOT EXISTS forest_loss_ha DOUBLE PRECISION;
