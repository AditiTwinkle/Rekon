"""Change detection service for regulatory updates."""

import logging
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class ChangeDetectionService:
    """Service for detecting regulatory content changes."""

    def __init__(self, regulation_service, cache_service):
        """Initialize change detection service.

        Args:
            regulation_service: Regulation service instance
            cache_service: Cache service instance
        """
        self.regulation_service = regulation_service
        self.cache_service = cache_service

    def detect_change(self, framework: str, content_hash: str) -> bool:
        """Detect if regulation content has changed.

        Args:
            framework: Framework identifier
            content_hash: New content hash

        Returns:
            True if content has changed, False otherwise
        """
        existing = self.regulation_service.get_regulation_by_hash(content_hash)
        return existing is None

    def emit_change_event(self, framework: str, change_data: Dict) -> bool:
        """Emit change event for downstream processing.

        Args:
            framework: Framework identifier
            change_data: Change details

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Regulation change detected for {framework}")
        return True
