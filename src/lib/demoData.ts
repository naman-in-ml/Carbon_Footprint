// Static demo data, generated from scripts/seed_projects.py using the real
// scoring functions. Used as a fallback when the API is unreachable (e.g. the
// frontend deployed without a backend/DB), so the dashboard always renders.
import type { ProjectDetail, ScoreListItem } from "@/types";

export const DEMO_PROJECTS: ScoreListItem[] = [
  {
    "project_id": 1,
    "verra_id": "VCS-1566",
    "name": "Khasi Hills Community REDD Project",
    "country": "India",
    "registry": "Verra",
    "status": "scored",
    "composite_score": 90.5,
    "risk_flag": "low"
  },
  {
    "project_id": 2,
    "verra_id": "VCS-0045",
    "name": "Mai Ndombe REDD+ Project",
    "country": "DRC",
    "registry": "Verra",
    "status": "scored",
    "composite_score": 50.6,
    "risk_flag": "medium"
  },
  {
    "project_id": 3,
    "verra_id": "GS-5984",
    "name": "Eden Reforestation Madagascar",
    "country": "Madagascar",
    "registry": "Gold Standard",
    "status": "scored",
    "composite_score": 91.5,
    "risk_flag": "low"
  },
  {
    "project_id": 4,
    "verra_id": "VCS-1477",
    "name": "Rimba Raya Biodiversity Reserve",
    "country": "Indonesia",
    "registry": "Verra",
    "status": "scored",
    "composite_score": 81.5,
    "risk_flag": "low"
  },
  {
    "project_id": 5,
    "verra_id": "VCS-934",
    "name": "Cordillera Azul National Park",
    "country": "Peru",
    "registry": "Verra",
    "status": "scored",
    "composite_score": 26.8,
    "risk_flag": "critical"
  }
];

export const DEMO_DETAILS: Record<string, ProjectDetail> = {
  "1": {
    "project": {
      "id": 1,
      "verra_id": "VCS-1566",
      "name": "Khasi Hills Community REDD Project",
      "registry": "Verra",
      "country": "India",
      "status": "scored",
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-01T00:00:00Z"
    },
    "claim": {
      "id": 1,
      "project_id": 1,
      "coordinates_raw": "25.55°N, 91.42°E, Meghalaya, India",
      "geometry_wkt": null,
      "geocoding_method": "doc",
      "claimed_hectares": 2500,
      "start_year": 2019,
      "species": "mixed broadleaf",
      "baseline_method": "VM0007",
      "claimed_tco2": 490000,
      "claimed_tco2_per_ha": 196.0,
      "monitoring_period": "2019-2030",
      "extraction_confidence": 0.92,
      "uncertainty_flags": null,
      "requires_review": false,
      "created_at": "2026-01-01T00:00:00Z"
    },
    "verification": {
      "id": 1,
      "claim_id": 1,
      "ndvi_before": 0.42,
      "ndvi_after_1yr": 0.51,
      "ndvi_after_3yr": 0.71,
      "ndvi_control": 0.4,
      "ndvi_trend": "rising",
      "planting_verified": "yes",
      "planting_confidence": 0.82,
      "ndvi_current": 0.76,
      "still_standing": "yes",
      "decline_detected_since": null,
      "likely_cause": "unclear",
      "fire_events_detected": 0,
      "estimated_biomass_tha": 195.9,
      "estimated_tco2": 489843.8,
      "estimated_tco2_low": 244921.9,
      "estimated_tco2_high": 734765.6,
      "credit_delta_pct": 0.0,
      "credit_flag": "ok",
      "ndvi_time_series": {
        "2019": 0.42,
        "2020": 0.51,
        "2021": 0.63,
        "2022": 0.71,
        "2023": 0.74,
        "2024": 0.76
      },
      "gee_run_at": "2026-01-01T00:00:00Z"
    },
    "score": {
      "id": 1,
      "project_id": 1,
      "verification_id": 1,
      "extraction_score": 92.0,
      "planting_score": 83.5,
      "permanence_score": 95,
      "credit_math_score": 95,
      "composite_score": 90.5,
      "risk_flag": "low",
      "flag_reasons": {},
      "created_at": "2026-01-01T00:00:00Z"
    }
  },
  "2": {
    "project": {
      "id": 2,
      "verra_id": "VCS-0045",
      "name": "Mai Ndombe REDD+ Project",
      "registry": "Verra",
      "country": "DRC",
      "status": "scored",
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-01T00:00:00Z"
    },
    "claim": {
      "id": 2,
      "project_id": 2,
      "coordinates_raw": "2.05°S, 18.31°E, Mai-Ndombe, DRC",
      "geometry_wkt": null,
      "geocoding_method": "doc",
      "claimed_hectares": 248000,
      "start_year": 2020,
      "species": "mixed tropical",
      "baseline_method": "VM0009",
      "claimed_tco2": 24944000,
      "claimed_tco2_per_ha": 100.6,
      "monitoring_period": "2020-2040",
      "extraction_confidence": 0.88,
      "uncertainty_flags": {
        "claimed_tco2": "Figure spans the full project crediting period"
      },
      "requires_review": true,
      "created_at": "2026-01-01T00:00:00Z"
    },
    "verification": {
      "id": 2,
      "claim_id": 2,
      "ndvi_before": 0.62,
      "ndvi_after_1yr": 0.68,
      "ndvi_after_3yr": 0.55,
      "ndvi_control": 0.66,
      "ndvi_trend": "declining",
      "planting_verified": "partial",
      "planting_confidence": 0.5,
      "ndvi_current": 0.48,
      "still_standing": "partial",
      "decline_detected_since": "2023",
      "likely_cause": "fire",
      "fire_events_detected": 3,
      "estimated_biomass_tha": 143.7,
      "estimated_tco2": 35634500.0,
      "estimated_tco2_low": 17817250.0,
      "estimated_tco2_high": 53451750.0,
      "credit_delta_pct": -42.9,
      "credit_flag": "under_claimed",
      "ndvi_time_series": {
        "2020": 0.62,
        "2021": 0.68,
        "2022": 0.7,
        "2023": 0.55,
        "2024": 0.48
      },
      "gee_run_at": "2026-01-01T00:00:00Z"
    },
    "score": {
      "id": 2,
      "project_id": 2,
      "verification_id": 2,
      "extraction_score": 61.6,
      "planting_score": 44.0,
      "permanence_score": 40,
      "credit_math_score": 80,
      "composite_score": 50.6,
      "risk_flag": "medium",
      "flag_reasons": {
        "planting": "Satellite NDVI does not support claimed reforestation",
        "permanence": "Forest loss or fire events detected post-planting"
      },
      "created_at": "2026-01-01T00:00:00Z"
    }
  },
  "3": {
    "project": {
      "id": 3,
      "verra_id": "GS-5984",
      "name": "Eden Reforestation Madagascar",
      "registry": "Gold Standard",
      "country": "Madagascar",
      "status": "scored",
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-01T00:00:00Z"
    },
    "claim": {
      "id": 3,
      "project_id": 3,
      "coordinates_raw": "15.72°S, 46.31°E, Mahajanga, Madagascar",
      "geometry_wkt": null,
      "geocoding_method": "doc",
      "claimed_hectares": 1200,
      "start_year": 2018,
      "species": "eucalyptus, acacia",
      "baseline_method": "GS-ARR",
      "claimed_tco2": 219000,
      "claimed_tco2_per_ha": 182.5,
      "monitoring_period": "2018-2028",
      "extraction_confidence": 0.95,
      "uncertainty_flags": null,
      "requires_review": false,
      "created_at": "2026-01-01T00:00:00Z"
    },
    "verification": {
      "id": 3,
      "claim_id": 3,
      "ndvi_before": 0.18,
      "ndvi_after_1yr": 0.29,
      "ndvi_after_3yr": 0.58,
      "ndvi_control": 0.22,
      "ndvi_trend": "rising",
      "planting_verified": "yes",
      "planting_confidence": 0.86,
      "ndvi_current": 0.71,
      "still_standing": "yes",
      "decline_detected_since": null,
      "likely_cause": "unclear",
      "fire_events_detected": 0,
      "estimated_biomass_tha": 174.2,
      "estimated_tco2": 209000.0,
      "estimated_tco2_low": 104500.0,
      "estimated_tco2_high": 313500.0,
      "credit_delta_pct": 4.6,
      "credit_flag": "ok",
      "ndvi_time_series": {
        "2018": 0.18,
        "2019": 0.29,
        "2020": 0.44,
        "2021": 0.58,
        "2022": 0.66,
        "2023": 0.69,
        "2024": 0.71
      },
      "gee_run_at": "2026-01-01T00:00:00Z"
    },
    "score": {
      "id": 3,
      "project_id": 3,
      "verification_id": 3,
      "extraction_score": 95.0,
      "planting_score": 85.0,
      "permanence_score": 95,
      "credit_math_score": 95,
      "composite_score": 91.5,
      "risk_flag": "low",
      "flag_reasons": {},
      "created_at": "2026-01-01T00:00:00Z"
    }
  },
  "4": {
    "project": {
      "id": 4,
      "verra_id": "VCS-1477",
      "name": "Rimba Raya Biodiversity Reserve",
      "registry": "Verra",
      "country": "Indonesia",
      "status": "scored",
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-01T00:00:00Z"
    },
    "claim": {
      "id": 4,
      "project_id": 4,
      "coordinates_raw": "2.85°S, 111.90°E, Central Kalimantan, Indonesia",
      "geometry_wkt": null,
      "geocoding_method": "doc",
      "claimed_hectares": 64000,
      "start_year": 2018,
      "species": "mixed tropical",
      "baseline_method": "VM0007",
      "claimed_tco2": 27588000,
      "claimed_tco2_per_ha": 431.1,
      "monitoring_period": "2018-2048",
      "extraction_confidence": 0.9,
      "uncertainty_flags": null,
      "requires_review": false,
      "created_at": "2026-01-01T00:00:00Z"
    },
    "verification": {
      "id": 4,
      "claim_id": 4,
      "ndvi_before": 0.7,
      "ndvi_after_1yr": 0.72,
      "ndvi_after_3yr": 0.73,
      "ndvi_control": 0.69,
      "ndvi_trend": "rising",
      "planting_verified": "yes",
      "planting_confidence": 0.72,
      "ndvi_current": 0.73,
      "still_standing": "yes",
      "decline_detected_since": null,
      "likely_cause": "unclear",
      "fire_events_detected": 0,
      "estimated_biomass_tha": 239.5,
      "estimated_tco2": 15326666.7,
      "estimated_tco2_low": 7663333.3,
      "estimated_tco2_high": 22990000.0,
      "credit_delta_pct": 44.4,
      "credit_flag": "over_claimed",
      "ndvi_time_series": {
        "2018": 0.7,
        "2019": 0.72,
        "2020": 0.71,
        "2021": 0.73,
        "2022": 0.72,
        "2023": 0.74,
        "2024": 0.73
      },
      "gee_run_at": "2026-01-01T00:00:00Z"
    },
    "score": {
      "id": 4,
      "project_id": 4,
      "verification_id": 4,
      "extraction_score": 90.0,
      "planting_score": 79.9,
      "permanence_score": 95,
      "credit_math_score": 45,
      "composite_score": 81.5,
      "risk_flag": "low",
      "flag_reasons": {
        "credit_math": "Satellite estimate diverges >30% from claimed tCO2"
      },
      "created_at": "2026-01-01T00:00:00Z"
    }
  },
  "5": {
    "project": {
      "id": 5,
      "verra_id": "VCS-934",
      "name": "Cordillera Azul National Park",
      "registry": "Verra",
      "country": "Peru",
      "status": "scored",
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-01T00:00:00Z"
    },
    "claim": {
      "id": 5,
      "project_id": 5,
      "coordinates_raw": "8.00°S, 76.00°W, Loreto, Peru",
      "geometry_wkt": null,
      "geocoding_method": "doc",
      "claimed_hectares": 1350000,
      "start_year": 2017,
      "species": "mixed broadleaf",
      "baseline_method": "VM0007",
      "claimed_tco2": 238064000,
      "claimed_tco2_per_ha": 176.3,
      "monitoring_period": "2017-2037",
      "extraction_confidence": 0.85,
      "uncertainty_flags": {
        "species": "Species mix not enumerated in summary"
      },
      "requires_review": true,
      "created_at": "2026-01-01T00:00:00Z"
    },
    "verification": {
      "id": 5,
      "claim_id": 5,
      "ndvi_before": 0.75,
      "ndvi_after_1yr": 0.77,
      "ndvi_after_3yr": 0.6,
      "ndvi_control": 0.74,
      "ndvi_trend": "declining",
      "planting_verified": "no",
      "planting_confidence": 0.2,
      "ndvi_current": 0.28,
      "still_standing": "partial",
      "decline_detected_since": "2020",
      "likely_cause": "fire",
      "fire_events_detected": 2,
      "estimated_biomass_tha": 58.8,
      "estimated_tco2": 79354687.5,
      "estimated_tco2_low": 39677343.8,
      "estimated_tco2_high": 119032031.2,
      "credit_delta_pct": 66.7,
      "credit_flag": "major_discrepancy",
      "ndvi_time_series": {
        "2017": 0.75,
        "2018": 0.77,
        "2019": 0.74,
        "2020": 0.6,
        "2021": 0.52,
        "2022": 0.4,
        "2023": 0.31,
        "2024": 0.28
      },
      "gee_run_at": "2026-01-01T00:00:00Z"
    },
    "score": {
      "id": 5,
      "project_id": 5,
      "verification_id": 5,
      "extraction_score": 59.5,
      "planting_score": 6.8,
      "permanence_score": 40,
      "credit_math_score": 10,
      "composite_score": 26.8,
      "risk_flag": "critical",
      "flag_reasons": {
        "planting": "Satellite NDVI does not support claimed reforestation",
        "permanence": "Forest loss or fire events detected post-planting",
        "credit_math": "Satellite estimate diverges >30% from claimed tCO2"
      },
      "created_at": "2026-01-01T00:00:00Z"
    }
  }
};

export function demoDetail(projectId: string): ProjectDetail | null {
  return DEMO_DETAILS[projectId] ?? null;
}
