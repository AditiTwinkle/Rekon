"""Evidence database schema."""

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSON, ARRAY
from sqlalchemy.orm import relationship

from rekon.db.schemas.base import BaseModel
from rekon.domain.models.evidence import EvidenceTypeEnum, EvidenceAccessActionEnum


class Evidence(BaseModel):
    """Evidence database model."""

    __tablename__ = "evidence"

    evidence_id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    checklist_item_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(ENUM(EvidenceTypeEnum), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False, unique=True)
    file_size = Column(Integer, nullable=False)
    upload_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    uploaded_by = Column(UUID(as_uuid=True), nullable=False)
    expiration_date = Column(DateTime, nullable=True, index=True)
    retention_policy = Column(String(255), nullable=True)
    access_log = Column(JSON, nullable=False, default=[])
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        # Index for common queries
        ("ix_evidence_org_checklist", "organization_id", "checklist_item_id"),
        ("ix_evidence_expiration", "expiration_date"),
    )
