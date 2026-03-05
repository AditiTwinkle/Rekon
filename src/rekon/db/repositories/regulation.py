"""Regulation repository for database operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from rekon.db.schemas.regulation import Regulation
from rekon.domain.models.regulation import RegulationCreate, FrameworkEnum


class RegulationRepository:
    """Repository for regulation database operations."""

    def __init__(self, db: Session):
        """Initialize repository.

        Args:
            db: Database session
        """
        self.db = db

    def create(self, regulation: RegulationCreate) -> Regulation:
        """Create a new regulation.

        Args:
            regulation: Regulation data to create

        Returns:
            Created regulation

        Raises:
            ValueError: If regulation with same content_hash already exists
        """
        # Check if regulation with same content_hash already exists
        existing = self.db.query(Regulation).filter(
            Regulation.content_hash == regulation.content_hash
        ).first()

        if existing:
            raise ValueError(f"Regulation with hash {regulation.content_hash} already exists")

        db_regulation = Regulation(
            framework=regulation.framework,
            requirement_number=regulation.requirement_number,
            title=regulation.title,
            description=regulation.description,
            raw_content=regulation.raw_content,
            source_url=regulation.source_url,
            content_hash=regulation.content_hash,
        )

        self.db.add(db_regulation)
        self.db.commit()
        self.db.refresh(db_regulation)

        return db_regulation

    def get_by_id(self, regulation_id: UUID) -> Optional[Regulation]:
        """Get regulation by ID.

        Args:
            regulation_id: Regulation ID

        Returns:
            Regulation or None if not found
        """
        return self.db.query(Regulation).filter(
            Regulation.id == regulation_id
        ).first()

    def get_by_hash(self, content_hash: str) -> Optional[Regulation]:
        """Get regulation by content hash.

        Args:
            content_hash: Content hash

        Returns:
            Regulation or None if not found
        """
        return self.db.query(Regulation).filter(
            Regulation.content_hash == content_hash
        ).first()

    def list_by_framework(
        self,
        framework: FrameworkEnum,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Regulation]:
        """List regulations by framework.

        Args:
            framework: Framework to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of regulations
        """
        return self.db.query(Regulation).filter(
            Regulation.framework == framework
        ).offset(skip).limit(limit).all()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Regulation]:
        """List all regulations.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of regulations
        """
        return self.db.query(Regulation).offset(skip).limit(limit).all()

    def update_version(self, regulation_id: UUID, new_version: int) -> Optional[Regulation]:
        """Update regulation version.

        Args:
            regulation_id: Regulation ID
            new_version: New version number

        Returns:
            Updated regulation or None if not found
        """
        regulation = self.get_by_id(regulation_id)

        if not regulation:
            return None

        regulation.version = new_version
        self.db.commit()
        self.db.refresh(regulation)

        return regulation

    def delete(self, regulation_id: UUID) -> bool:
        """Delete regulation.

        Args:
            regulation_id: Regulation ID

        Returns:
            True if deleted, False if not found
        """
        regulation = self.get_by_id(regulation_id)

        if not regulation:
            return False

        self.db.delete(regulation)
        self.db.commit()

        return True

    def count_by_framework(self, framework: FrameworkEnum) -> int:
        """Count regulations by framework.

        Args:
            framework: Framework to count

        Returns:
            Number of regulations
        """
        return self.db.query(Regulation).filter(
            Regulation.framework == framework
        ).count()

    def count_all(self) -> int:
        """Count all regulations.

        Returns:
            Total number of regulations
        """
        return self.db.query(Regulation).count()
