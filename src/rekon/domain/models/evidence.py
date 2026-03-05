"""Evidence domain models."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class EvidenceTypeEnum(str, Enum):
    """Supported evidence types."""

    DOCUMENT = "DOCUMENT"
    SCREENSHOT = "SCREENSHOT"
    LOG = "LOG"
    TEST_RESULT = "TEST_RESULT"
    OTHER = "OTHER"


class EvidenceAccessActionEnum(str, Enum):
    """Evidence access actions for audit trail."""

    VIEW = "VIEW"
    DOWNLOAD = "DOWNLOAD"
    DELETE = "DELETE"


class EvidenceAccessLog(BaseModel):
    """Evidence access log entry."""

    user_id: UUID
    access_time: datetime
    action: EvidenceAccessActionEnum


class EvidenceBase(BaseModel):
    """Base evidence model."""

    checklist_item_id: UUID
    file_name: str
    file_type: EvidenceTypeEnum
    file_size: int
    expiration_date: Optional[datetime] = None
    retention_policy: Optional[str] = None


class EvidenceCreate(EvidenceBase):
    """Model for creating evidence."""

    file_path: str
    file_hash: str
    uploaded_by: UUID


class EvidenceUpdate(BaseModel):
    """Model for updating evidence."""

    expiration_date: Optional[datetime] = None
    retention_policy: Optional[str] = None


class EvidenceResponse(EvidenceBase):
    """Model for evidence API responses."""

    evidence_id: UUID
    organization_id: UUID
    file_path: str
    file_hash: str
    upload_timestamp: datetime
    uploaded_by: UUID
    access_log: List[EvidenceAccessLog] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
