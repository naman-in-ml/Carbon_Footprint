from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: Optional[int] = Field(default=None, primary_key=True)
    verra_id: str = Field(unique=True, index=True, max_length=32)
    name: str
    registry: str = Field(default="Verra", max_length=32)
    pdd_url: Optional[str] = None
    pdd_storage_path: Optional[str] = None
    status: str = Field(default="pending", max_length=32)
    country: Optional[str] = Field(default=None, max_length=64)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)