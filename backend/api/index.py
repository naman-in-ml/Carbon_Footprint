"""Vercel Python entry point. Tables are created via Supabase migrations only."""
import os
import sys

# Ensure `backend/` (parent of api/) is importable both locally and on Vercel.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from routers import ingest, projects, scores, verify

app = FastAPI(title="CarbonProof — AI-Verified Carbon Auditing")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.allowed_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["Ingestion"])
app.include_router(verify.router, prefix="/api/verify", tags=["Verification"])
app.include_router(scores.router, prefix="/api/scores", tags=["Scores"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}