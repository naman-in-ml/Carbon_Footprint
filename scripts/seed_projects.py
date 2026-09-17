"""Seed 5 real Verra/Gold Standard projects with precomputed pipeline results.

The demo must never wait on live GEE / Nugen calls (Vercel kills functions at
60s). This script writes projects, claims, verifications and scores directly so
the dashboard renders instantly.

Usage:
    cd carbonproof
    python scripts/seed_projects.py

Requires DATABASE_URL in .env and the Phase-2 migration already applied.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

from sqlmodel import select  # noqa: E402

from db.session import AsyncSessionLocal  # noqa: E402
from models.claim import ExtractedClaim  # noqa: E402
from models.project import Project  # noqa: E402
from models.score import CredibilityScore  # noqa: E402
from models.verification import SatelliteVerification  # noqa: E402
from services.allometric import estimate_tco2, reconcile_credits  # noqa: E402
from services.scorer import compute_composite  # noqa: E402

# Approximate coordinates — good enough for a demo overlay/NDVI lookup.
DEMO_PROJECTS = [
    {
        "project": {
            "verra_id": "VCS-1566",
            "name": "Khasi Hills Community REDD Project",
            "country": "India",
            "registry": "Verra",
        },
        "claim": {
            "coordinates_raw": "25.55°N, 91.42°E, Meghalaya, India",
            "claimed_hectares": 2500,
            "start_year": 2019,
            "species": "mixed broadleaf",
            "baseline_method": "VM0007",
            "monitoring_period": "2019-2030",
            "extraction_confidence": 0.92,
            "uncertainty_flags": None,
        },
        "series": {2019: 0.42, 2020: 0.51, 2021: 0.63, 2022: 0.71, 2023: 0.74, 2024: 0.76},
        "control": 0.40,
        "planting_verified": "yes",
        "planting_confidence": 0.82,
        "fires": 0,
        "credit_factor": 1.0,  # claimed == estimated -> ok
    },
    {
        "project": {
            "verra_id": "VCS-0045",
            "name": "Mai Ndombe REDD+ Project",
            "country": "DRC",
            "registry": "Verra",
        },
        "claim": {
            "coordinates_raw": "2.05°S, 18.31°E, Mai-Ndombe, DRC",
            "claimed_hectares": 248000,
            "start_year": 2020,
            "species": "mixed tropical",
            "baseline_method": "VM0009",
            "monitoring_period": "2020-2040",
            "extraction_confidence": 0.88,
            "uncertainty_flags": {"claimed_tco2": "Figure spans the full project crediting period"},
        },
        "series": {2020: 0.62, 2021: 0.68, 2022: 0.70, 2023: 0.55, 2024: 0.48},
        "control": 0.66,
        "planting_verified": "partial",
        "planting_confidence": 0.50,
        "fires": 3,
        "credit_factor": 0.7,  # claimed < estimated -> under_claimed
    },
    {
        "project": {
            "verra_id": "GS-5984",
            "name": "Eden Reforestation Madagascar",
            "country": "Madagascar",
            "registry": "Gold Standard",
        },
        "claim": {
            "coordinates_raw": "15.72°S, 46.31°E, Mahajanga, Madagascar",
            "claimed_hectares": 1200,
            "start_year": 2018,
            "species": "eucalyptus, acacia",
            "baseline_method": "GS-ARR",
            "monitoring_period": "2018-2028",
            "extraction_confidence": 0.95,
            "uncertainty_flags": None,
        },
        "series": {2018: 0.18, 2019: 0.29, 2020: 0.44, 2021: 0.58, 2022: 0.66, 2023: 0.69, 2024: 0.71},
        "control": 0.22,
        "planting_verified": "yes",
        "planting_confidence": 0.86,
        "fires": 0,
        "credit_factor": 1.05,  # within band -> ok
    },
    {
        "project": {
            "verra_id": "VCS-1477",
            "name": "Rimba Raya Biodiversity Reserve",
            "country": "Indonesia",
            "registry": "Verra",
        },
        "claim": {
            "coordinates_raw": "2.85°S, 111.90°E, Central Kalimantan, Indonesia",
            "claimed_hectares": 64000,
            "start_year": 2018,
            "species": "mixed tropical",
            "baseline_method": "VM0007",
            "monitoring_period": "2018-2048",
            "extraction_confidence": 0.90,
            "uncertainty_flags": None,
        },
        "series": {2018: 0.70, 2019: 0.72, 2020: 0.71, 2021: 0.73, 2022: 0.72, 2023: 0.74, 2024: 0.73},
        "control": 0.69,
        "planting_verified": "yes",
        "planting_confidence": 0.72,
        "fires": 0,
        "credit_factor": 1.8,  # claimed >> estimated -> over_claimed
    },
    {
        "project": {
            "verra_id": "VCS-934",
            "name": "Cordillera Azul National Park",
            "country": "Peru",
            "registry": "Verra",
        },
        "claim": {
            "coordinates_raw": "8.00°S, 76.00°W, Loreto, Peru",
            "claimed_hectares": 1350000,
            "start_year": 2017,
            "species": "mixed broadleaf",
            "baseline_method": "VM0007",
            "monitoring_period": "2017-2037",
            "extraction_confidence": 0.85,
            "uncertainty_flags": {"species": "Species mix not enumerated in summary"},
        },
        "series": {2017: 0.75, 2018: 0.77, 2019: 0.74, 2020: 0.60, 2021: 0.52, 2022: 0.40, 2023: 0.31, 2024: 0.28},
        "control": 0.74,
        "planting_verified": "no",
        "planting_confidence": 0.20,
        "fires": 2,
        "credit_factor": 3.0,  # gross over-claim -> major_discrepancy
    },
]


def _derive_ndvi_fields(series: dict, control_start_value: float):
    years = sorted(series)
    values = [series[y] for y in years]
    return {
        "ndvi_before": values[0],
        "ndvi_after_1yr": values[1] if len(values) > 1 else None,
        "ndvi_after_3yr": values[3] if len(values) > 3 else values[-1],
        "ndvi_control": control_start_value,
        "ndvi_current": values[-1],
    }


def _decline_year(series: dict):
    years = sorted(series)
    for i in range(1, len(years)):
        if series[years[i - 1]] - series[years[i]] > 0.10:
            return years[i]
    return None


async def seed():
    async with AsyncSessionLocal() as db:
        for entry in DEMO_PROJECTS:
            verra_id = entry["project"]["verra_id"]
            existing = (
                await db.execute(select(Project).where(Project.verra_id == verra_id))
            ).scalars().first()
            if existing:
                print(f"Skip (exists): {verra_id}")
                continue

            claim_data = entry["claim"]
            series = entry["series"]

            project = Project(status="scored", **entry["project"])
            db.add(project)
            await db.commit()
            await db.refresh(project)

            claim = ExtractedClaim(
                project_id=project.id,
                geometry_wkt=None,
                geocoding_method="doc",
                claimed_tco2_per_ha=None,
                requires_review=bool(claim_data.get("uncertainty_flags")),
                raw_nugen_response={"source": "seed"},
                **claim_data,
            )
            db.add(claim)
            await db.commit()
            await db.refresh(claim)

            ndvi = _derive_ndvi_fields(series, entry["control"])
            allometric = estimate_tco2(
                verified_hectares=claim.claimed_hectares or 100,
                ndvi_current=ndvi["ndvi_current"],
                species_text=claim.species,
            )
            estimated = allometric["estimated_tco2"]
            claimed_tco2 = round(estimated * entry["credit_factor"] / 1000) * 1000
            recon = reconcile_credits(claimed_tco2=claimed_tco2, estimated_tco2=estimated)

            # Keep the stored claim consistent with the figure used for reconciliation.
            claim.claimed_tco2 = claimed_tco2
            claim.claimed_tco2_per_ha = round(
                claimed_tco2 / max(claim.claimed_hectares or 1, 1), 1
            )
            db.add(claim)
            await db.commit()

            decline_year = _decline_year(series)
            still_standing = "yes"
            if decline_year:
                still_standing = "no" if ndvi["ndvi_current"] < 0.25 else "partial"

            verif = SatelliteVerification(
                claim_id=claim.id,
                ndvi_before=ndvi["ndvi_before"],
                ndvi_after_1yr=ndvi["ndvi_after_1yr"],
                ndvi_after_3yr=ndvi["ndvi_after_3yr"],
                ndvi_control=ndvi["ndvi_control"],
                ndvi_trend="rising" if ndvi["ndvi_current"] >= ndvi["ndvi_before"] else "declining",
                planting_verified=entry["planting_verified"],
                planting_confidence=entry["planting_confidence"],
                ndvi_current=ndvi["ndvi_current"],
                still_standing=still_standing,
                decline_detected_since=str(decline_year) if decline_year else None,
                likely_cause="fire" if entry["fires"] else "unclear",
                fire_events_detected=entry["fires"],
                fire_dates={"dates": []},
                estimated_biomass_tha=round(estimated / max(claim.claimed_hectares or 1, 1), 1),
                estimated_tco2=estimated,
                estimated_tco2_low=allometric["low_estimate"],
                estimated_tco2_high=allometric["high_estimate"],
                credit_delta_pct=recon["credit_delta_pct"],
                credit_flag=recon["credit_flag"],
                ndvi_time_series={str(y): series[y] for y in sorted(series)},
                firms_raw={"fire_events_detected": entry["fires"], "source": "seed"},
            )
            db.add(verif)
            await db.commit()
            await db.refresh(verif)

            score_data = compute_composite(
                extraction_confidence=claim.extraction_confidence or 0.5,
                requires_review=claim.requires_review,
                planting_verified=verif.planting_verified or "unknown",
                planting_confidence=verif.planting_confidence or 0.5,
                still_standing=verif.still_standing or "yes",
                fire_events_detected=verif.fire_events_detected or 0,
                decline_detected=bool(verif.decline_detected_since),
                credit_flag=verif.credit_flag,
            )
            db.add(CredibilityScore(project_id=project.id, verification_id=verif.id, **score_data))
            await db.commit()

            print(
                f"Seeded {verra_id}: composite={score_data['composite_score']} "
                f"risk={score_data['risk_flag']} credit={recon['credit_flag']}"
            )

    print("\nDone. Start the API and open the dashboard.")


if __name__ == "__main__":
    asyncio.run(seed())