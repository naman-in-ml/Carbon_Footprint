"""Pipeline orchestration — one function per stage.

Vercel kills a serverless function at 60s and BackgroundTasks do not survive
the response. Instead of a single long-running background job, each stage is a
separate endpoint call and progress is tracked via `project.status`:

    pending -> extracting -> extracted -> verifying -> verified -> scored

The frontend polls GET /api/scores/{id} and calls the next stage endpoint.
Pre-seeded demo projects ship with every stage already computed (see
scripts/seed_projects.py), so the demo never waits on live GEE / Nugen calls.
"""
import asyncio
import logging
import re
from datetime import datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.config import settings
from models.claim import ExtractedClaim
from models.project import Project
from models.score import CredibilityScore
from models.verification import SatelliteVerification
from services import nugen
from services.allometric import estimate_tco2, reconcile_credits
from services.fallback_parser import extract_claims_fallback
from services.gee_ndvi import compute_ndvi_stats
from services.gee_permanence import check_fire_events, compute_ndvi_time_series
from services.geocoder import resolve_geometry
from services.scorer import compute_composite

logger = logging.getLogger(__name__)


def _has_nugen() -> bool:
    return bool(settings.nugen_api_key)


def _parse_point_wkt(wkt: str) -> tuple[float, float]:
    """Parse 'POINT(lon lat)' -> (lat, lon)."""
    m = re.match(r"POINT\s*\(\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*\)", wkt)
    if not m:
        raise ValueError(f"Unparseable geometry WKT: {wkt!r}")
    lon, lat = float(m.group(1)), float(m.group(2))
    return lat, lon


async def _load_claim(db: AsyncSession, project_id: int) -> ExtractedClaim | None:
    return (
        await db.execute(
            select(ExtractedClaim).where(ExtractedClaim.project_id == project_id)
        )
    ).scalars().first()


async def run_stage_extract(project: Project, text: str, db: AsyncSession) -> ExtractedClaim:
    """Stage 1: document -> structured claim. Bounded (one model call)."""
    project.status = "extracting"
    db.add(project)
    await db.commit()

    if _has_nugen():
        try:
            result = await nugen.extract_claims(text, project.id)
        except Exception as exc:  # noqa: BLE001 - fall back rather than fail the demo
            logger.warning("Nugen extraction failed, using fallback parser: %s", exc)
            result = extract_claims_fallback(text, project.id)
    else:
        result = extract_claims_fallback(text, project.id)

    geometry = await resolve_geometry(
        db, result.get("coordinates_raw", ""), project.country or "India"
    )

    claim = ExtractedClaim(
        project_id=project.id,
        coordinates_raw=result.get("coordinates_raw"),
        geometry_wkt=(
            f"POINT({geometry.get('lon')} {geometry.get('lat')})"
            if geometry["method"] != "failed"
            else None
        ),
        geocoding_method=geometry["method"],
        claimed_hectares=result.get("claimed_hectares"),
        start_year=result.get("start_year"),
        species=result.get("species"),
        baseline_method=result.get("baseline_method"),
        claimed_tco2=result.get("claimed_tco2"),
        claimed_tco2_per_ha=result.get("claimed_tco2_per_ha"),
        monitoring_period=result.get("monitoring_period"),
        extraction_confidence=result.get("extraction_confidence", 0.5),
        uncertainty_flags=result.get("uncertainty_flags"),
        requires_review=bool(result.get("uncertainty_flags")),
        raw_nugen_response=result,
    )
    db.add(claim)
    project.status = "extracted" if geometry["method"] != "failed" else "failed"
    project.updated_at = datetime.utcnow()
    db.add(project)
    await db.commit()
    await db.refresh(claim)
    return claim


async def run_stage_verify(project: Project, db: AsyncSession) -> SatelliteVerification:
    """Stages 2-4: GEE NDVI + permanence + FIRMS + allometric, in one bounded call."""
    claim = await _load_claim(db, project.id)
    if claim is None:
        raise ValueError("No extracted claim for project; run extract stage first.")

    if claim.geocoding_method == "failed":
        project.status = "failed"
        db.add(project)
        await db.commit()
        raise ValueError("Could not resolve project coordinates.")

    project.status = "verifying"
    db.add(project)
    await db.commit()

    lat, lon = _parse_point_wkt(claim.geometry_wkt)
    start_year = claim.start_year or 2020

    loop = asyncio.get_event_loop()
    ndvi_stats, ndvi_ts, fire_data = await asyncio.gather(
        loop.run_in_executor(None, compute_ndvi_stats, lat, lon, start_year),
        loop.run_in_executor(None, compute_ndvi_time_series, lat, lon, start_year),
        check_fire_events(lat, lon, start_year),
    )

    ndvi_current = ndvi_ts.get("ndvi_current") or ndvi_stats.get("ndvi_after_3yr") or 0
    allometric = estimate_tco2(
        verified_hectares=claim.claimed_hectares or 100,
        ndvi_current=ndvi_current,
        species_text=claim.species,
    )
    credit_reconciliation = reconcile_credits(
        claimed_tco2=claim.claimed_tco2 or 0,
        estimated_tco2=allometric["estimated_tco2"],
    )

    verif = SatelliteVerification(
        claim_id=claim.id,
        ndvi_before=ndvi_stats.get("ndvi_before"),
        ndvi_after_1yr=ndvi_stats.get("ndvi_after_1yr"),
        ndvi_after_3yr=ndvi_stats.get("ndvi_after_3yr"),
        ndvi_control=ndvi_stats.get("ndvi_control"),
        ndvi_trend=ndvi_stats.get("ndvi_trend"),
        planting_verified=ndvi_stats.get("planting_verified"),
        planting_confidence=ndvi_stats.get("planting_confidence"),
        ndvi_current=ndvi_ts.get("ndvi_current"),
        still_standing=ndvi_ts.get("still_standing"),
        decline_detected_since=ndvi_ts.get("decline_detected_since"),
        fire_events_detected=fire_data.get("fire_events_detected"),
        fire_dates={"dates": fire_data.get("fire_dates")},
        likely_cause=fire_data.get("likely_cause"),
        estimated_biomass_tha=round(
            allometric.get("estimated_tco2", 0) / max(claim.claimed_hectares or 1, 1), 1
        ),
        estimated_tco2=allometric.get("estimated_tco2"),
        estimated_tco2_low=allometric.get("low_estimate"),
        estimated_tco2_high=allometric.get("high_estimate"),
        credit_delta_pct=credit_reconciliation.get("credit_delta_pct"),
        credit_flag=credit_reconciliation.get("credit_flag"),
        ndvi_time_series=ndvi_ts.get("ndvi_time_series"),
        firms_raw=fire_data,
        gee_run_at=datetime.utcnow(),
    )
    db.add(verif)
    project.status = "verified"
    project.updated_at = datetime.utcnow()
    db.add(project)
    await db.commit()
    await db.refresh(verif)
    return verif


async def run_stage_score(project: Project, db: AsyncSession) -> CredibilityScore:
    """Stage 5: composite credibility score."""
    claim = await _load_claim(db, project.id)
    verif = (
        await db.execute(
            select(SatelliteVerification).where(SatelliteVerification.claim_id == claim.id)
        )
    ).scalars().first() if claim else None
    if claim is None or verif is None:
        raise ValueError("Verification missing; run verify stage first.")

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
    score = CredibilityScore(project_id=project.id, verification_id=verif.id, **score_data)
    db.add(score)
    project.status = "scored"
    project.updated_at = datetime.utcnow()
    db.add(project)
    await db.commit()
    await db.refresh(score)
    return score