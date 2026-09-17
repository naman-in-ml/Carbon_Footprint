"""Stage 2-4 verification endpoints (GEE + FIRMS + allometric)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from db.session import get_db
from models.project import Project
from pipeline.orchestrator import run_stage_verify

router = APIRouter()


@router.post("/{project_id}")
async def verify_project(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    if project.status not in ("extracted", "verified", "scored"):
        raise HTTPException(409, f"Project not ready for verification (status={project.status})")
    try:
        verif = await run_stage_verify(project, db)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - GEE/network failures surface to caller
        project.status = "failed"
        db.add(project)
        await db.commit()
        raise HTTPException(502, f"Verification failed: {exc}") from exc
    return {
        "project_id": project.id,
        "status": project.status,
        "verification_id": verif.id,
        "next": f"/api/scores/score/{project.id}",
    }