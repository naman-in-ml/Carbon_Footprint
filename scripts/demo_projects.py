"""Illustrative ARR demo projects (fictional names, real coordinates).

These are NOT real carbon projects. Numbers are synthetic but are pushed through
the real allometric + scoring functions, so every score is internally consistent.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from services.allometric import estimate_tco2, reconcile_credits  # noqa: E402
from services.scorer import compute_composite  # noqa: E402

DEMO_PROJECTS = [
    {
        "project": {"verra_id": "DEMO-ARR-001", "name": "Sahyadri Teak Restoration (Demo)",
                    "country": "India", "registry": "Illustrative"},
        "lat": 17.75, "lon": 73.65,
        "claim": {"coordinates_raw": "17.75°N, 73.65°E, Satara district, Maharashtra",
                  "claimed_hectares": 800, "start_year": 2019, "species": "teak",
                  "baseline_method": "AR-ACM0003", "monitoring_period": "2019-2049",
                  "extraction_confidence": 0.93, "uncertainty_flags": None,
                  "claimed_tco2": 190000},
        "series": {2018: 0.38, 2019: 0.40, 2020: 0.47, 2021: 0.55, 2022: 0.63, 2023: 0.69, 2024: 0.72},
        "control": 0.41,
        "planting_verified": "yes", "planting_confidence": 0.85,
        "tree_cover_ha": 690.0, "aoi_ha": 800.0, "forest_loss_ha": 5.0,
        "fire_dates": [],
    },
    {
        "project": {"verra_id": "DEMO-ARR-002", "name": "Deccan Agroforestry Belt (Demo)",
                    "country": "India", "registry": "Illustrative"},
        "lat": 18.45, "lon": 76.55,
        "claim": {"coordinates_raw": "Latur district, Maharashtra (village list in Annex 3)",
                  "claimed_hectares": 1500, "start_year": 2020, "species": "mixed broadleaf",
                  "baseline_method": "AR-AMS0007", "monitoring_period": "2020-2050",
                  "extraction_confidence": 0.88,
                  "uncertainty_flags": {"coordinates_raw": "Only district-level location given; parcels listed in an annex not included in the PDD"},
                  "claimed_tco2": 195000},
        "series": {2019: 0.27, 2020: 0.28, 2021: 0.31, 2022: 0.35, 2023: 0.39, 2024: 0.41},
        "control": 0.30,
        "planting_verified": "partial", "planting_confidence": 0.5,
        "tree_cover_ha": 520.0, "aoi_ha": 1500.0, "forest_loss_ha": 0.0,
        "fire_dates": [],
    },
    {
        "project": {"verra_id": "DEMO-ARR-003", "name": "Aravalli Dryland Plantation (Demo)",
                    "country": "India", "registry": "Illustrative"},
        "lat": 27.45, "lon": 76.15,
        "claim": {"coordinates_raw": "27.45°N, 76.15°E, Alwar district, Rajasthan",
                  "claimed_hectares": 2000, "start_year": 2018, "species": "eucalyptus",
                  "baseline_method": "AR-ACM0003", "monitoring_period": "2018-2048",
                  "extraction_confidence": 0.90, "uncertainty_flags": None,
                  "claimed_tco2": 220000},
        "series": {2017: 0.20, 2018: 0.19, 2019: 0.21, 2020: 0.20, 2021: 0.22, 2022: 0.20, 2023: 0.21, 2024: 0.20},
        "control": 0.21,
        "planting_verified": "no", "planting_confidence": 0.2,
        "tree_cover_ha": 60.0, "aoi_ha": 2000.0, "forest_loss_ha": 0.0,
        "fire_dates": [],
    },
    {
        "project": {"verra_id": "DEMO-ARR-004", "name": "Satpura Dry Forest Restoration (Demo)",
                    "country": "India", "registry": "Illustrative"},
        "lat": 22.45, "lon": 78.35,
        "claim": {"coordinates_raw": "22.45°N, 78.35°E, Betul district, Madhya Pradesh",
                  "claimed_hectares": 1200, "start_year": 2018, "species": "teak",
                  "baseline_method": "AR-ACM0003", "monitoring_period": "2018-2048",
                  "extraction_confidence": 0.90, "uncertainty_flags": None,
                  "claimed_tco2": 300000},
        "series": {2017: 0.30, 2018: 0.31, 2019: 0.42, 2020: 0.55, 2021: 0.62, 2022: 0.48, 2023: 0.33, 2024: 0.30},
        "control": 0.32,
        "planting_verified": "yes", "planting_confidence": 0.8,
        "tree_cover_ha": 780.0, "aoi_ha": 1200.0, "forest_loss_ha": 310.0,
        "fire_dates": ["2022-03-14", "2022-03-15", "2022-03-21", "2023-04-02"],
    },
]


def build_demo_record(entry: dict, idx: int) -> dict:
    """Return API-shaped project, claim, verification, and score dictionaries."""
    timestamp = "2026-11-01T00:00:00Z"
    years = sorted(entry["series"])
    values = [entry["series"][year] for year in years]
    ndvi_before = values[0]
    ndvi_after_1yr = values[1] if len(values) > 1 else None
    ndvi_after_3yr = values[3] if len(values) > 3 else values[-1]
    ndvi_current = values[-1]
    decline = None
    for index in range(1, len(values)):
        if values[index - 1] - values[index] > 0.10:
            decline = str(years[index])
            break
    still_standing = "yes" if decline is None else ("no" if ndvi_current < 0.25 else "partial")
    ndvi_trend = "rising" if ndvi_current >= ndvi_before + 0.05 else "declining" if ndvi_current <= ndvi_before - 0.05 else "flat"

    claim_input = entry["claim"]
    allometric = estimate_tco2(
        verified_hectares=entry["tree_cover_ha"],
        ndvi_current=ndvi_current,
        species_text=claim_input["species"],
        apply_canopy_fraction=False,
    )
    recon = reconcile_credits(claim_input["claimed_tco2"], allometric["estimated_tco2"])
    requires_review = bool(claim_input["uncertainty_flags"])
    score_fields = compute_composite(
        extraction_confidence=claim_input["extraction_confidence"],
        requires_review=requires_review,
        planting_verified=entry["planting_verified"],
        planting_confidence=entry["planting_confidence"],
        still_standing=still_standing,
        fire_events_detected=len(entry["fire_dates"]),
        decline_detected=bool(decline),
        credit_flag=recon["credit_flag"],
        claimed_hectares=claim_input["claimed_hectares"],
        tree_cover_ha=entry["tree_cover_ha"],
        aoi_ha=entry["aoi_ha"],
        forest_loss_ha=entry["forest_loss_ha"],
    )
    project = {
        "id": idx,
        **entry["project"],
        "status": "scored",
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    claim = {
        "id": idx,
        "project_id": idx,
        **claim_input,
        "geometry_wkt": f"POINT({entry['lon']} {entry['lat']})",
        "boundary_geojson": None,
        "geocoding_method": "doc",
        "claimed_tco2_per_ha": round(
            claim_input["claimed_tco2"] / claim_input["claimed_hectares"], 1
        ),
        "requires_review": requires_review,
        "created_at": timestamp,
    }
    verification = {
        "id": idx,
        "claim_id": idx,
        "ndvi_before": ndvi_before,
        "ndvi_after_1yr": ndvi_after_1yr,
        "ndvi_after_3yr": ndvi_after_3yr,
        "ndvi_control": entry["control"],
        "ndvi_trend": ndvi_trend,
        "planting_verified": entry["planting_verified"],
        "planting_confidence": entry["planting_confidence"],
        "ndvi_current": ndvi_current,
        "still_standing": still_standing,
        "decline_detected_since": decline,
        "likely_cause": "fire" if entry["fire_dates"] else "unclear",
        "fire_events_detected": len(entry["fire_dates"]),
        "fire_dates": {"dates": entry["fire_dates"]},
        "estimated_biomass_tha": round(allometric["estimated_tco2"] / entry["tree_cover_ha"], 1),
        "estimated_tco2": allometric["estimated_tco2"],
        "estimated_tco2_low": allometric["low_estimate"],
        "estimated_tco2_high": allometric["high_estimate"],
        "credit_delta_pct": recon["credit_delta_pct"],
        "credit_flag": recon["credit_flag"],
        "tree_cover_ha": entry["tree_cover_ha"],
        "aoi_ha": entry["aoi_ha"],
        "forest_loss_ha": entry["forest_loss_ha"],
        "ndvi_time_series": {str(year): entry["series"][year] for year in years},
        "gee_run_at": timestamp,
    }
    score = {
        "id": idx,
        "project_id": idx,
        "verification_id": idx,
        **score_fields,
        "created_at": timestamp,
    }
    return {"project": project, "claim": claim, "verification": verification, "score": score}


def build_all() -> list[dict]:
    return [build_demo_record(entry, index + 1) for index, entry in enumerate(DEMO_PROJECTS)]
