"""Dashboard API endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from rekon.api.dependencies import get_session
from rekon.api.auth import get_current_user, User

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get dashboard data.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dashboard data
    """
    # Implementation will be added in Phase 9
    return {
        "compliance_scores": {},
        "open_gaps": 0,
        "upcoming_deadlines": [],
        "remediation_tasks": [],
    }


@router.get("/trends")
def get_trend_data(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get trend data.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Trend data
    """
    # Implementation will be added in Phase 9
    return {"trends": []}


@router.get("/alerts")
def get_active_alerts(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get active alerts.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Active alerts
    """
    # Implementation will be added in Phase 9
    return {"alerts": []}
