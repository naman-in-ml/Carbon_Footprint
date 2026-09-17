from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class GeocodeCache(SQLModel, table=True):
    __tablename__ = "geocode_cache"

    id: Optional[int] = Field(default=None, primary_key=True)
    query: str = Field(unique=True, index=True, max_length=512)
    lat: float
    lon: float
    method: str = Field(default="nominatim", max_length=32)
    created_at: datetime = Field(default_factory=datetime.utcnow)