from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import JSONB


class ExtractedClaim(SQLModel, table=True):
    __tablename__ = "extracted_claims"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id", index=True)
    coordinates_raw: Optional[str] = Field(default=None, sa_column=Column(Text))
    geometry_wkt: Optional[str] = Field(default=None, sa_column=Column(Text))
    geocoding_method: Optional[str] = Field(default=None, max_length=32)
    claimed_hectares: Optional[float] = None
    start_year: Optional[int] = None
    species: Optional[str] = Field(default=None, sa_column=Column(Text))
    baseline_method: Optional[str] = Field(default=None, max_length=64)
    claimed_tco2: Optional[float] = None
    claimed_tco2_per_ha: Optional[float] = None
    monitoring_period: Optional[str] = Field(default=None, max_length=64)
    extraction_confidence: Optional[float] = None
    uncertainty_flags: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    requires_review: bool = Field(default=False)
    raw_nugen_response: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)