"""PDF / text ingestion -> Stage 1 extraction. One bounded stage per request."""
import io

import pdfplumber
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.session import get_db
from models.project import Project
from pipeline.orchestrator import run_stage_extract

router = APIRouter()


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF bytes using pdfplumber (no subprocess)."""
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "".join((page.extract_text() or "") for page in pdf.pages)[:50_000]
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(400, f"Could not read PDF: {exc}") from exc


async def _existing(db: AsyncSession, verra_id: str):
    return (
        await db.execute(select(Project).where(Project.verra_id == verra_id))
    ).scalars().first()


@router.post("/")
async def ingest_pdd(
    verra_id: str = Form(...),
    name: str = Form(...),
    country: str = Form(default="India"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if await _existing(db, verra_id):
        raise HTTPException(409, f"Project {verra_id} already exists")

    content = await file.read()
    pdf_text = extract_text_from_pdf(content)
    if not pdf_text.strip():
        raise HTTPException(400, "No extractable text found in PDF (scanned image?)")

    project = Project(verra_id=verra_id, name=name, country=country)
    db.add(project)
    await db.commit()
    await db.refresh(project)

    claim = await run_stage_extract(project, pdf_text, db)
    return {
        "project_id": project.id,
        "status": project.status,
        "claim_id": claim.id,
        "next": f"/api/verify/{project.id}",
    }


@router.post("/text")
async def ingest_text(
    verra_id: str = Form(...),
    name: str = Form(...),
    country: str = Form(default="India"),
    text: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Paste raw PDD text directly (useful for the demo)."""
    if await _existing(db, verra_id):
        raise HTTPException(409, f"Project {verra_id} already exists")

    project = Project(verra_id=verra_id, name=name, country=country)
    db.add(project)
    await db.commit()
    await db.refresh(project)

    claim = await run_stage_extract(project, text, db)
    return {
        "project_id": project.id,
        "status": project.status,
        "claim_id": claim.id,
        "next": f"/api/verify/{project.id}",
    }