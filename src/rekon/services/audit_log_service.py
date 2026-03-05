"""Audit logging service for compliance operations."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class AuditLogService:
    """Service for audit logging operations."""

    def __init__(self, db: Session):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db

    def log_evidence_access(
        self,
        evidence_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        action: str,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log evidence access.

        Args:
            evidence_id: Evidence ID
            organization_id: Organization ID
            user_id: User ID
            action: Action performed (VIEW, DOWNLOAD, DELETE)
            ip_address: IP address of user
            details: Additional details
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "evidence_id": str(evidence_id),
            "organization_id": str(organization_id),
            "user_id": str(user_id),
            "action": action,
            "ip_address": ip_address,
            "details": details or {},
        }

        # Log to CloudWatch
        logger.info(
            "AUDIT_LOG",
            extra={
                "audit_data": json.dumps(log_entry),
            },
        )

    def log_evidence_upload(
        self,
        evidence_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        file_name: str,
        file_size: int,
        file_hash: str,
        ip_address: Optional[str] = None,
    ) -> None:
        """Log evidence upload.

        Args:
            evidence_id: Evidence ID
            organization_id: Organization ID
            user_id: User ID
            file_name: File name
            file_size: File size in bytes
            file_hash: File hash
            ip_address: IP address of user
        """
        details = {
            "file_name": file_name,
            "file_size": file_size,
            "file_hash": file_hash,
        }

        self.log_evidence_access(
            evidence_id,
            organization_id,
            user_id,
            "UPLOAD",
            ip_address,
            details,
        )

    def log_evidence_deletion(
        self,
        evidence_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        file_name: str,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        """Log evidence deletion.

        Args:
            evidence_id: Evidence ID
            organization_id: Organization ID
            user_id: User ID
            file_name: File name
            reason: Reason for deletion
            ip_address: IP address of user
        """
        details = {
            "file_name": file_name,
            "reason": reason,
        }

        self.log_evidence_access(
            evidence_id,
            organization_id,
            user_id,
            "DELETE",
            ip_address,
            details,
        )

    def log_evidence_modification(
        self,
        evidence_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        modifications: Dict[str, Any],
        ip_address: Optional[str] = None,
    ) -> None:
        """Log evidence modification.

        Args:
            evidence_id: Evidence ID
            organization_id: Organization ID
            user_id: User ID
            modifications: Dictionary of modifications
            ip_address: IP address of user
        """
        self.log_evidence_access(
            evidence_id,
            organization_id,
            user_id,
            "MODIFY",
            ip_address,
            modifications,
        )

    def log_compliance_operation(
        self,
        organization_id: UUID,
        user_id: UUID,
        operation: str,
        resource_type: str,
        resource_id: UUID,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        """Log compliance operation.

        Args:
            organization_id: Organization ID
            user_id: User ID
            operation: Operation name
            resource_type: Type of resource
            resource_id: Resource ID
            status: Operation status (SUCCESS, FAILURE)
            details: Additional details
            ip_address: IP address of user
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "organization_id": str(organization_id),
            "user_id": str(user_id),
            "operation": operation,
            "resource_type": resource_type,
            "resource_id": str(resource_id),
            "status": status,
            "ip_address": ip_address,
            "details": details or {},
        }

        logger.info(
            "COMPLIANCE_OPERATION",
            extra={
                "audit_data": json.dumps(log_entry),
            },
        )

    def log_checklist_generation(
        self,
        organization_id: UUID,
        user_id: UUID,
        framework: str,
        item_count: int,
        status: str,
        ip_address: Optional[str] = None,
    ) -> None:
        """Log checklist generation.

        Args:
            organization_id: Organization ID
            user_id: User ID
            framework: Regulatory framework
            item_count: Number of items generated
            status: Generation status
            ip_address: IP address of user
        """
        details = {
            "framework": framework,
            "item_count": item_count,
        }

        self.log_compliance_operation(
            organization_id,
            user_id,
            "CHECKLIST_GENERATION",
            "CHECKLIST",
            organization_id,
            status,
            details,
            ip_address,
        )

    def log_gap_analysis(
        self,
        organization_id: UUID,
        user_id: UUID,
        gap_count: int,
        status: str,
        ip_address: Optional[str] = None,
    ) -> None:
        """Log gap analysis.

        Args:
            organization_id: Organization ID
            user_id: User ID
            gap_count: Number of gaps identified
            status: Analysis status
            ip_address: IP address of user
        """
        details = {
            "gap_count": gap_count,
        }

        self.log_compliance_operation(
            organization_id,
            user_id,
            "GAP_ANALYSIS",
            "GAP",
            organization_id,
            status,
            details,
            ip_address,
        )

    def log_report_generation(
        self,
        organization_id: UUID,
        user_id: UUID,
        report_type: str,
        framework: Optional[str] = None,
        status: str = "SUCCESS",
        ip_address: Optional[str] = None,
    ) -> None:
        """Log report generation.

        Args:
            organization_id: Organization ID
            user_id: User ID
            report_type: Type of report
            framework: Regulatory framework (optional)
            status: Generation status
            ip_address: IP address of user
        """
        details = {
            "report_type": report_type,
            "framework": framework,
        }

        self.log_compliance_operation(
            organization_id,
            user_id,
            "REPORT_GENERATION",
            "REPORT",
            organization_id,
            status,
            details,
            ip_address,
        )

    def log_unauthorized_access_attempt(
        self,
        organization_id: UUID,
        user_id: UUID,
        resource_type: str,
        resource_id: UUID,
        reason: str,
        ip_address: Optional[str] = None,
    ) -> None:
        """Log unauthorized access attempt.

        Args:
            organization_id: Organization ID
            user_id: User ID
            resource_type: Type of resource
            resource_id: Resource ID
            reason: Reason for denial
            ip_address: IP address of user
        """
        details = {
            "reason": reason,
        }

        self.log_compliance_operation(
            organization_id,
            user_id,
            "UNAUTHORIZED_ACCESS",
            resource_type,
            resource_id,
            "FAILURE",
            details,
            ip_address,
        )
