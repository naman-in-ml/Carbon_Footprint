from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class SatelliteVerification(SQLModel, table=True):
    __tablename__ = "satellite_verifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    claim_id: int = Field(foreign_key="extracted_claims.id", index=True)
    ndvi_before: Optional[float] = None
    ndvi_after_1yr: Optional[float] = None
    ndvi_after_3yr: Optional[float] = None
    ndvi_control: Optional[float] = None
    ndvi_trend: Optional[str] = Field(default=None, max_length=32)
    planting_verified: Optional[str] = Field(default=None, max_length=16)
    planting_confidence: Optional[float] = None
    ndvi_current: Optional[float] = None
    still_standing: Optional[str] = Field(default=None, max_length=8)
    decline_detected_since: Optional[str] = Field(default=None, max_length=16)
    likely_cause: Optional[str] = Field(default=None, max_length=32)
    fire_events_detected: Optional[int] = None
    fire_dates: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    estimated_biomass_tha: Optional[float] = None
    estimated_tco2: Optional[float] = None
    estimated_tco2_low: Optional[float] = None
    estimated_tco2_high: Optional[float] = None
    credit_delta_pct: Optional[float] = None
    credit_flag: Optional[str] = Field(default=None, max_length=32)
    ndvi_time_series: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    firms_raw: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    gee_run_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)