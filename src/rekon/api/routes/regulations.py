"""Regulation API endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from rekon.api.dependencies import get_session
from rekon.domain.models.regulation import RegulationResponse, FrameworkEnum
from rekon.db.schemas.regulation import Regulation

router = APIRouter(prefix="/api/v1/regulations", tags=["regulations"])


@router.get("", response_model=List[RegulationResponse])
def list_regulations(
    framework: FrameworkEnum | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
) -> List[RegulationResponse]:
    """List all regulations.

    Args:
        framework: Filter by framework
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of regulations
    """
    query = db.query(Regulation)

    if framework:
        query = query.filter(Regulation.framework == framework)

    regulations = query.offset(skip).limit(limit).all()
    return [RegulationResponse.from_orm(r) for r in regulations]


@router.get("/{regulation_id}", response_model=RegulationResponse)
def get_regulation(
    regulation_id: UUID,
    db: Session = Depends(get_session),
) -> RegulationResponse:
    """Get regulation by ID.

    Args:
        regulation_id: Regulation ID
        db: Database session

    Returns:
        Regulation details

    Raises:
        HTTPException: If regulation not found
    """
    regulation = db.query(Regulation).filter(Regulation.id == regulation_id).first()

    if not regulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regulation not found",
        )

    return RegulationResponse.from_orm(regulation)


@router.post("/sync", status_code=status.HTTP_202_ACCEPTED)
def sync_regulations(db: Session = Depends(get_session)) -> dict:
    """Trigger regulation synchronization.

    Args:
        db: Database session

    Returns:
        Sync status
    """
    # This will be implemented in Phase 3 with the Regulation Puller Lambda
    return {"status": "sync_initiated", "message": "Regulation synchronization started"}
