"""Regulation database schema."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, Integer, Index
from sqlalchemy.dialects.postgresql import UUID, ENUM

from rekon.db.schemas.base import BaseModel
from rekon.domain.models.regulation import FrameworkEnum


class Regulation(BaseModel):
    """Regulation database model."""

    __tablename__ = "regulations"

    framework = Column(ENUM(FrameworkEnum), nullable=False, index=True)
    requirement_number = Column(String(255), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    raw_content = Column(Text, nullable=False)
    source_url = Column(String(2048), nullable=False)
    content_hash = Column(String(64), nullable=False, unique=True, index=True)
    fetch_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    version = Column(Integer, nullable=False, default=1)
    effective_date = Column(DateTime, nullable=True)
    sunset_date = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_framework_requirement", "framework", "requirement_number"),
        Index("idx_framework_version", "framework", "version"),
    )
