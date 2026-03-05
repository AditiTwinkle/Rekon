"""API dependencies."""

from fastapi import Depends
from sqlalchemy.orm import Session

from rekon.db.session import get_db


def get_session(db: Session = Depends(get_db)) -> Session:
    """Get database session.

    Args:
        db: Database session

    Returns:
        Database session
    """
    return db
