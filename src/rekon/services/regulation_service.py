"""Regulation service for business logic."""

import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from rekon.db.repositories.regulation import RegulationRepository
from rekon.domain.models.regulation import RegulationCreate, RegulationResponse, FrameworkEnum

logger = logging.getLogger(__name__)


class RegulationService:
    """Service for regulation operations."""

    def __init__(self, db: Session):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db
        self.repository = RegulationRepository(db)

    def create_regulation(self, regulation: RegulationCreate) -> RegulationResponse:
        """Create a new regulation.

        Args:
            regulation: Regulation data to create

        Returns:
            Created regulation response

        Raises:
            ValueError: If regulation with same content_hash already exists
        """
        try:
            db_regulation = self.repository.create(regulation)
            logger.info(f"Created regulation: {regulation.framework} - {regulation.requirement_number}")
            return RegulationResponse.from_orm(db_regulation)
        except ValueError as e:
            logger.warning(f"Failed to create regulation: {str(e)}")
            raise

    def get_regulation(self, regulation_id: UUID) -> Optional[RegulationResponse]:
        """Get regulation by ID.

        Args:
            regulation_id: Regulation ID

        Returns:
            Regulation response or None if not found
        """
        regulation = self.repository.get_by_id(regulation_id)

        if not regulation:
            logger.warning(f"Regulation not found: {regulation_id}")
            return None

        return RegulationResponse.from_orm(regulation)

    def get_regulation_by_hash(self, content_hash: str) -> Optional[RegulationResponse]:
        """Get regulation by content hash.

        Args:
            content_hash: Content hash

        Returns:
            Regulation response or None if not found
        """
        regulation = self.repository.get_by_hash(content_hash)

        if not regulation:
            return None

        return RegulationResponse.from_orm(regulation)

    def list_regulations_by_framework(
        self,
        framework: FrameworkEnum,
        skip: int = 0,
        limit: int = 100,
    ) -> List[RegulationResponse]:
        """List regulations by framework.

        Args:
            framework: Framework to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of regulation responses
        """
        regulations = self.repository.list_by_framework(framework, skip, limit)
        return [RegulationResponse.from_orm(r) for r in regulations]

    def list_all_regulations(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[RegulationResponse]:
        """List all regulations.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of regulation responses
        """
        regulations = self.repository.list_all(skip, limit)
        return [RegulationResponse.from_orm(r) for r in regulations]

    def check_regulation_exists_by_hash(self, content_hash: str) -> bool:
        """Check if regulation exists by content hash.

        Args:
            content_hash: Content hash

        Returns:
            True if regulation exists, False otherwise
        """
        return self.repository.get_by_hash(content_hash) is not None

    def get_framework_count(self, framework: FrameworkEnum) -> int:
        """Get count of regulations for a framework.

        Args:
            framework: Framework to count

        Returns:
            Number of regulations
        """
        return self.repository.count_by_framework(framework)

    def get_total_count(self) -> int:
        """Get total count of all regulations.

        Returns:
            Total number of regulations
        """
        return self.repository.count_all()
