"""Seed the four fictional ARR demo projects with precomputed pipeline results.

Usage:
    cd carbonproof
    python scripts/seed_projects.py

Requires DATABASE_URL and the satellite-area migration already applied.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

from sqlmodel import select  # noqa: E402

from db.session import AsyncSessionLocal  # noqa: E402
from demo_projects import build_all  # noqa: E402
from models.claim import ExtractedClaim  # noqa: E402
from models.project import Project  # noqa: E402
from models.score import CredibilityScore  # noqa: E402
from models.verification import SatelliteVerification  # noqa: E402


def _without(data: dict, *keys: str) -> dict:
    return {key: value for key, value in data.items() if key not in keys}


async def seed():
    async with AsyncSessionLocal() as db:
        for record in build_all():
            verra_id = record["project"]["verra_id"]
            existing = (
                await db.execute(select(Project).where(Project.verra_id == verra_id))
            ).scalars().first()
            if existing:
                print(f"Skip (exists): {verra_id}")
                continue

            project = Project(
                **_without(record["project"], "id", "created_at", "updated_at")
            )
            db.add(project)
            await db.commit()
            await db.refresh(project)

            claim = ExtractedClaim(
                project_id=project.id,
                raw_nugen_response={"source": "illustrative_demo"},
                **_without(record["claim"], "id", "project_id", "created_at"),
            )
            db.add(claim)
            await db.commit()
            await db.refresh(claim)

            verification = SatelliteVerification(
                claim_id=claim.id,
                firms_raw={
                    "fire_events_detected": record["verification"]["fire_events_detected"],
                    "source": "illustrative_demo",
                },
                **_without(
                    record["verification"],
                    "id",
                    "claim_id",
                    "created_at",
                    "gee_run_at",
                ),
            )
            db.add(verification)
            await db.commit()
            await db.refresh(verification)

            score = CredibilityScore(
                project_id=project.id,
                verification_id=verification.id,
                **_without(
                    record["score"],
                    "id",
                    "project_id",
                    "verification_id",
                    "created_at",
                ),
            )
            db.add(score)
            await db.commit()
            print(
                f"Seeded {verra_id}: composite={score.composite_score} "
                f"risk={score.risk_flag} credit={verification.credit_flag}"
            )

    print("\nDone. Start the API and open the dashboard.")


if __name__ == "__main__":
    asyncio.run(seed())
