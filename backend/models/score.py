from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class CredibilityScore(SQLModel, table=True):
    __tablename__ = "credibility_scores"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id", unique=True)
    verification_id: int = Field(foreign_key="satellite_verifications.id")
    extraction_score: float
    planting_score: float
    permanence_score: float
    credit_math_score: float
    composite_score: float
    risk_flag: str = Field(max_length=32)
    flag_reasons: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)