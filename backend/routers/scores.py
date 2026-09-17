"""Stage 5 scoring + read endpoints used for polling."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.session import get_db
from models.claim import ExtractedClaim
from models.project import Project
from models.score import CredibilityScore
from models.verification import SatelliteVerification
from pipeline.orchestrator import run_stage_score

router = APIRouter()


@router.get("/")
async def list_all_scores(db: AsyncSession = Depends(get_db)):
    projects = (await db.execute(select(Project).order_by(Project.id))).scalars().all()
    results = []
    for p in projects:
        score = (
            await db.execute(
                select(CredibilityScore).where(CredibilityScore.project_id == p.id)
            )
        ).scalars().first()
        results.append(
            {
                "project_id": p.id,
                "verra_id": p.verra_id,
                "name": p.name,
                "country": p.country,
                "registry": p.registry,
                "status": p.status,
                "composite_score": score.composite_score if score else None,
                "risk_flag": score.risk_flag if score else None,
            }
        )
    return results


@router.get("/{project_id}")
async def get_project_score(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    claim = (
        await db.execute(
            select(ExtractedClaim).where(ExtractedClaim.project_id == project_id)
        )
    ).scalars().first()

    verif = None
    if claim:
        verif = (
            await db.execute(
                select(SatelliteVerification).where(
                    SatelliteVerification.claim_id == claim.id
                )
            )
        ).scalars().first()

    score = (
        await db.execute(
            select(CredibilityScore).where(CredibilityScore.project_id == project_id)
        )
    ).scalars().first()

    return {"project": project, "claim": claim, "verification": verif, "score": score}


@router.post("/score/{project_id}")
async def score_project(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    if project.status not in ("verified", "scored"):
        raise HTTPException(409, f"Project not ready for scoring (status={project.status})")
    try:
        score = await run_stage_score(project, db)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"project_id": project.id, "status": project.status, "score": score}