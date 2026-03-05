"""Regulation domain models."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FrameworkEnum(str, Enum):
    """Supported regulatory frameworks."""

    DORA_A = "DORA_A"
    DORA_B = "DORA_B"
    SOX = "SOX"
    BMR = "BMR"
    IOSCO = "IOSCO"
    NIST = "NIST"
    APPHEALTH = "APPHEALTH"


class RegulationBase(BaseModel):
    """Base regulation model."""

    framework: FrameworkEnum
    requirement_number: str
    title: str
    description: str
    source_url: str


class RegulationCreate(RegulationBase):
    """Model for creating regulations."""

    raw_content: str
    content_hash: str


class RegulationResponse(RegulationBase):
    """Model for regulation API responses."""

    regulation_id: UUID
    content_hash: str
    fetch_timestamp: datetime
    version: int
    effective_date: Optional[datetime] = None
    sunset_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
