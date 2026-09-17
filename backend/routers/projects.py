from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.session import get_db
from models.project import Project

router = APIRouter()


@router.get("/")
async def list_projects(db: AsyncSession = Depends(get_db)):
    projects = (await db.execute(select(Project).order_by(Project.id))).scalars().all()
    return projects


@router.get("/{project_id}")
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project