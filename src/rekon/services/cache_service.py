"""Cache service for Redis-based caching."""

import json
import logging
from typing import Optional, Any
from datetime import timedelta

import redis

logger = logging.getLogger(__name__)


class CacheService:
    """Service for Redis caching operations."""

    DEFAULT_TTL = timedelta(hours=24)
    REGULATION_PREFIX = "regulation:"
    FRAMEWORK_PREFIX = "framework:"

    def __init__(self, redis_client: redis.Redis):
        """Initialize cache service.

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client

    def set_regulation(
        self,
        regulation_id: str,
        data: dict,
        ttl: Optional[timedelta] = None,
    ) -> bool:
        """Cache regulation data.

        Args:
            regulation_id: Regulation ID
            data: Regulation data to cache
            ttl: Time to live (default: 24 hours)

        Returns:
            True if successful, False otherwise
        """
        try:
            key = f"{self.REGULATION_PREFIX}{regulation_id}"
            ttl_seconds = int((ttl or self.DEFAULT_TTL).total_seconds())

            self.redis.setex(
                key,
                ttl_seconds,
                json.dumps(data),
            )

            logger.debug(f"Cached regulation: {regulation_id}")
            return True

        except redis.RedisError as e:
            logger.error(f"Error caching regulation: {str(e)}")
            return False

    def get_regulation(self, regulation_id: str) -> Optional[dict]:
        """Retrieve cached regulation data.

        Args:
            regulation_id: Regulation ID

        Returns:
            Cached regulation data or None if not found
        """
        try:
            key = f"{self.REGULATION_PREFIX}{regulation_id}"
            data = self.redis.get(key)

            if data:
                logger.debug(f"Cache hit for regulation: {regulation_id}")
                return json.loads(data)

            logger.debug(f"Cache miss for regulation: {regulation_id}")
            return None

        except redis.RedisError as e:
            logger.error(f"Error retrieving from cache: {str(e)}")
            return None

    def delete_regulation(self, regulation_id: str) -> bool:
        """Delete cached regulation data.

        Args:
            regulation_id: Regulation ID

        Returns:
            True if successful, False otherwise
        """
        try:
            key = f"{self.REGULATION_PREFIX}{regulation_id}"
            self.redis.delete(key)

            logger.debug(f"Deleted cached regulation: {regulation_id}")
            return True

        except redis.RedisError as e:
            logger.error(f"Error deleting from cache: {str(e)}")
            return False

    def set_framework_regulations(
        self,
        framework: str,
        regulations: list,
        ttl: Optional[timedelta] = None,
    ) -> bool:
        """Cache regulations for a framework.

        Args:
            framework: Framework name
            regulations: List of regulations
            ttl: Time to live (default: 24 hours)

        Returns:
            True if successful, False otherwise
        """
        try:
            key = f"{self.FRAMEWORK_PREFIX}{framework}"
            ttl_seconds = int((ttl or self.DEFAULT_TTL).total_seconds())

            self.redis.setex(
                key,
                ttl_seconds,
                json.dumps(regulations),
            )

            logger.debug(f"Cached {len(regulations)} regulations for framework: {framework}")
            return True

        except redis.RedisError as e:
            logger.error(f"Error caching framework regulations: {str(e)}")
            return False

    def get_framework_regulations(self, framework: str) -> Optional[list]:
        """Retrieve cached regulations for a framework.

        Args:
            framework: Framework name

        Returns:
            Cached regulations or None if not found
        """
        try:
            key = f"{self.FRAMEWORK_PREFIX}{framework}"
            data = self.redis.get(key)

            if data:
                logger.debug(f"Cache hit for framework: {framework}")
                return json.loads(data)

            logger.debug(f"Cache miss for framework: {framework}")
            return None

        except redis.RedisError as e:
            logger.error(f"Error retrieving framework from cache: {str(e)}")
            return None

    def invalidate_framework_cache(self, framework: str) -> bool:
        """Invalidate cached regulations for a framework.

        Args:
            framework: Framework name

        Returns:
            True if successful, False otherwise
        """
        try:
            key = f"{self.FRAMEWORK_PREFIX}{framework}"
            self.redis.delete(key)

            logger.debug(f"Invalidated cache for framework: {framework}")
            return True

        except redis.RedisError as e:
            logger.error(f"Error invalidating framework cache: {str(e)}")
            return False

    def clear_all_regulation_cache(self) -> bool:
        """Clear all regulation-related cache.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all regulation keys
            pattern = f"{self.REGULATION_PREFIX}*"
            keys = self.redis.keys(pattern)

            if keys:
                self.redis.delete(*keys)
                logger.debug(f"Cleared {len(keys)} regulation cache entries")

            # Get all framework keys
            pattern = f"{self.FRAMEWORK_PREFIX}*"
            keys = self.redis.keys(pattern)

            if keys:
                self.redis.delete(*keys)
                logger.debug(f"Cleared {len(keys)} framework cache entries")

            return True

        except redis.RedisError as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False

    def get_cache_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        try:
            regulation_keys = self.redis.keys(f"{self.REGULATION_PREFIX}*")
            framework_keys = self.redis.keys(f"{self.FRAMEWORK_PREFIX}*")

            return {
                "regulation_entries": len(regulation_keys),
                "framework_entries": len(framework_keys),
                "total_entries": len(regulation_keys) + len(framework_keys),
            }

        except redis.RedisError as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {}
