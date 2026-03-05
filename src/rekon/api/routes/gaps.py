"""Gap assessment API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from rekon.api.dependencies import get_session
from rekon.api.auth import get_current_user, User

router = APIRouter(prefix="/api/v1/gaps", tags=["gaps"])


@router.post("/assess", status_code=status.HTTP_202_ACCEPTED)
def start_gap_assessment(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Start interactive gap assessment.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Assessment status
    """
    # Implementation will be added in Phase 6
    return {"status": "assessment_initiated"}


@router.get("/{gap_id}")
def get_gap_details(
    gap_id: UUID,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get gap details.

    Args:
        gap_id: Gap ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Gap details
    """
    # Implementation will be added in Phase 6
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Gap not found",
    )


@router.post("/{gap_id}/respond", status_code=status.HTTP_200_OK)
def submit_assessment_response(
    gap_id: UUID,
    response: dict,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Submit assessment response.

    Args:
        gap_id: Gap ID
        response: Assessment response
        db: Database session
        current_user: Current authenticated user

    Returns:
        Response status
    """
    # Implementation will be added in Phase 6
    return {"status": "response_recorded"}
