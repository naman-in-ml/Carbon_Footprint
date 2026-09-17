export type RiskFlag = "low" | "medium" | "high" | "critical";

export interface Project {
  id: number;
  verra_id: string;
  name: string;
  registry: string;
  country: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Claim {
  id: number;
  project_id: number;
  coordinates_raw: string | null;
  geometry_wkt: string | null;
  geocoding_method: string | null;
  claimed_hectares: number | null;
  start_year: number | null;
  species: string | null;
  baseline_method: string | null;
  claimed_tco2: number | null;
  claimed_tco2_per_ha: number | null;
  monitoring_period: string | null;
  extraction_confidence: number | null;
  uncertainty_flags: Record<string, string> | null;
  requires_review: boolean;
  created_at: string;
}

export interface Verification {
  id: number;
  claim_id: number;
  ndvi_before: number | null;
  ndvi_after_1yr: number | null;
  ndvi_after_3yr: number | null;
  ndvi_control: number | null;
  ndvi_trend: string | null;
  planting_verified: string | null;
  planting_confidence: number | null;
  ndvi_current: number | null;
  still_standing: string | null;
  decline_detected_since: string | null;
  likely_cause: string | null;
  fire_events_detected: number | null;
  estimated_biomass_tha: number | null;
  estimated_tco2: number | null;
  estimated_tco2_low: number | null;
  estimated_tco2_high: number | null;
  credit_delta_pct: number | null;
  credit_flag: string | null;
  ndvi_time_series: Record<string, number> | null;
  gee_run_at: string | null;
}

export interface Score {
  id: number;
  project_id: number;
  verification_id: number;
  extraction_score: number;
  planting_score: number;
  permanence_score: number;
  credit_math_score: number;
  composite_score: number;
  risk_flag: RiskFlag;
  flag_reasons: Record<string, string> | null;
  created_at: string;
}

export interface ProjectDetail {
  project: Project;
  claim: Claim | null;
  verification: Verification | null;
  score: Score | null;
}

export interface ScoreListItem {
  project_id: number;
  verra_id: string;
  name: string;
  country: string | null;
  registry: string;
  status: string;
  composite_score: number | null;
  risk_flag: RiskFlag | null;
}