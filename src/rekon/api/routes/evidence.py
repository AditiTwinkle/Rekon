"""Evidence management API endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from rekon.api.dependencies import get_session, get_organization_id
from rekon.api.auth import get_current_user, User
from rekon.services.evidence_service import EvidenceService
from rekon.domain.models.evidence import EvidenceResponse, EvidenceUpdate

router = APIRouter(prefix="/api/v1/evidence", tags=["evidence"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    checklist_item_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_id),
) -> EvidenceResponse:
    """Upload evidence file.

    Args:
        checklist_item_id: Checklist item ID
        file: File to upload
        db: Database session
        current_user: Current authenticated user
        organization_id: Organization ID

    Returns:
        Evidence response

    Raises:
        HTTPException: If upload fails
    """
    try:
        service = EvidenceService(db)
        file_content = await file.read()

        evidence = service.upload_evidence(
            organization_id=organization_id,
            checklist_item_id=checklist_item_id,
            file_name=file.filename,
            file_type=file.content_type or "OTHER",
            file_content=file_content,
            uploaded_by=current_user.user_id,
        )
        return evidence
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload evidence",
        )


@router.get("")
def list_evidence(
    skip: int = 0,
    limit: int = 100,
    checklist_item_id: UUID = None,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_id),
) -> dict:
    """List evidence.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        checklist_item_id: Optional checklist item ID to filter by
        db: Database session
        current_user: Current authenticated user
        organization_id: Organization ID

    Returns:
        List of evidence with total count
    """
    try:
        service = EvidenceService(db)

        if checklist_item_id:
            evidence_list, total = service.list_evidence_by_checklist_item(
                checklist_item_id,
                organization_id,
                skip,
                limit,
            )
        else:
            evidence_list, total = service.list_evidence_by_organization(
                organization_id,
                skip,
                limit,
            )

        return {
            "evidence": evidence_list,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list evidence",
        )


@router.get("/{evidence_id}")
def get_evidence(
    evidence_id: UUID,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_id),
) -> EvidenceResponse:
    """Get evidence by ID.

    Args:
        evidence_id: Evidence ID
        db: Database session
        current_user: Current authenticated user
        organization_id: Organization ID

    Returns:
        Evidence response

    Raises:
        HTTPException: If evidence not found
    """
    try:
        service = EvidenceService(db)
        evidence = service.get_evidence(evidence_id, organization_id, current_user.user_id)
        return evidence
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get evidence",
        )


@router.patch("/{evidence_id}")
def update_evidence(
    evidence_id: UUID,
    update_data: EvidenceUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_id),
) -> EvidenceResponse:
    """Update evidence record.

    Args:
        evidence_id: Evidence ID
        update_data: Update data
        db: Database session
        current_user: Current authenticated user
        organization_id: Organization ID

    Returns:
        Updated evidence response

    Raises:
        HTTPException: If evidence not found
    """
    try:
        service = EvidenceService(db)
        evidence = service.update_evidence(evidence_id, organization_id, update_data)
        return evidence
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update evidence",
        )


@router.delete("/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evidence(
    evidence_id: UUID,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_id),
) -> None:
    """Delete evidence.

    Args:
        evidence_id: Evidence ID
        db: Database session
        current_user: Current authenticated user
        organization_id: Organization ID

    Raises:
        HTTPException: If evidence not found
    """
    try:
        service = EvidenceService(db)
        deleted = service.delete_evidence(evidence_id, organization_id, current_user.user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evidence {evidence_id} not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete evidence",
        )


@router.get("/expiring/soon")
def get_expiring_soon_evidence(
    days_threshold: int = 30,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_id),
) -> dict:
    """Get evidence expiring soon.

    Args:
        days_threshold: Number of days to look ahead
        db: Database session
        current_user: Current authenticated user
        organization_id: Organization ID

    Returns:
        List of evidence expiring soon
    """
    try:
        service = EvidenceService(db)
        evidence_list = service.get_expiring_soon_evidence(organization_id, days_threshold)
        return {
            "evidence": evidence_list,
            "total": len(evidence_list),
            "days_threshold": days_threshold,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get expiring evidence",
        )


@router.get("/collection-package/{checklist_item_id}")
def get_evidence_collection_package(
    checklist_item_id: UUID,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_id),
) -> dict:
    """Get evidence collection package for a requirement.

    Args:
        checklist_item_id: Checklist item ID
        db: Database session
        current_user: Current authenticated user
        organization_id: Organization ID

    Returns:
        Evidence collection package

    Raises:
        HTTPException: If no evidence found
    """
    try:
        service = EvidenceService(db)
        package = service.generate_evidence_collection_package(
            checklist_item_id,
            organization_id,
        )
        return package
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate evidence collection package",
        )


@router.get("/search")
def search_evidence(
    file_type: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    organization_id: UUID = Depends(get_organization_id),
) -> dict:
    """Search evidence by criteria.

    Args:
        file_type: Optional file type to filter
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        organization_id: Organization ID

    Returns:
        Search results
    """
    try:
        service = EvidenceService(db)
        evidence_list, total = service.search_evidence_by_requirement(
            organization_id,
            file_type=file_type,
            skip=skip,
            limit=limit,
        )
        return {
            "evidence": evidence_list,
            "total": total,
            "skip": skip,
            "limit": limit,
            "filters": {"file_type": file_type},
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search evidence",
        )
