"""Unit tests for cache service."""

import pytest
import json
from datetime import timedelta
from unittest.mock import Mock, patch

from rekon.services.cache_service import CacheService


@pytest.fixture
def mock_redis():
    """Create mock Redis client."""
    return Mock()


@pytest.fixture
def cache_service(mock_redis):
    """Create cache service instance."""
    return CacheService(mock_redis)


@pytest.fixture
def sample_regulation():
    """Create sample regulation data."""
    return {
        "regulation_id": "123",
        "framework": "DORA_A",
        "title": "Test Regulation",
        "content_hash": "abc123",
    }


class TestCacheServiceSetRegulation:
    """Tests for setting regulation cache."""

    def test_set_regulation_success(self, cache_service, mock_redis, sample_regulation):
        """Test successful regulation caching."""
        result = cache_service.set_regulation("123", sample_regulation)

        assert result is True
        mock_redis.setex.assert_called_once()

        # Verify the call arguments
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "regulation:123"
        assert json.loads(call_args[0][2]) == sample_regulation

    def test_set_regulation_with_custom_ttl(self, cache_service, mock_redis, sample_regulation):
        """Test setting regulation with custom TTL."""
        custom_ttl = timedelta(hours=12)
        result = cache_service.set_regulation("123", sample_regulation, ttl=custom_ttl)

        assert result is True
        call_args = mock_redis.setex.call_args
        assert call_args[0][1] == 43200  # 12 hours in seconds

    def test_set_regulation_redis_error(self, cache_service, mock_redis, sample_regulation):
        """Test handling of Redis errors."""
        import redis

        mock_redis.setex.side_effect = redis.RedisError("Connection failed")

        result = cache_service.set_regulation("123", sample_regulation)

        assert result is False


class TestCacheServiceGetRegulation:
    """Tests for getting regulation from cache."""

    def test_get_regulation_hit(self, cache_service, mock_redis, sample_regulation):
        """Test cache hit for regulation."""
        mock_redis.get.return_value = json.dumps(sample_regulation).encode()

        result = cache_service.get_regulation("123")

        assert result == sample_regulation
        mock_redis.get.assert_called_once_with("regulation:123")

    def test_get_regulation_miss(self, cache_service, mock_redis):
        """Test cache miss for regulation."""
        mock_redis.get.return_value = None

        result = cache_service.get_regulation("123")

        assert result is None

    def test_get_regulation_redis_error(self, cache_service, mock_redis):
        """Test handling of Redis errors."""
        import redis

        mock_redis.get.side_effect = redis.RedisError("Connection failed")

        result = cache_service.get_regulation("123")

        assert result is None


class TestCacheServiceDeleteRegulation:
    """Tests for deleting regulation from cache."""

    def test_delete_regulation_success(self, cache_service, mock_redis):
        """Test successful regulation deletion."""
        result = cache_service.delete_regulation("123")

        assert result is True
        mock_redis.delete.assert_called_once_with("regulation:123")

    def test_delete_regulation_redis_error(self, cache_service, mock_redis):
        """Test handling of Redis errors."""
        import redis

        mock_redis.delete.side_effect = redis.RedisError("Connection failed")

        result = cache_service.delete_regulation("123")

        assert result is False


class TestCacheServiceFrameworkRegulations:
    """Tests for framework regulations caching."""

    def test_set_framework_regulations_success(self, cache_service, mock_redis):
        """Test successful framework regulations caching."""
        regulations = [
            {"id": "1", "title": "Reg 1"},
            {"id": "2", "title": "Reg 2"},
        ]

        result = cache_service.set_framework_regulations("DORA_A", regulations)

        assert result is True
        mock_redis.setex.assert_called_once()

        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "framework:DORA_A"
        assert json.loads(call_args[0][2]) == regulations

    def test_get_framework_regulations_hit(self, cache_service, mock_redis):
        """Test cache hit for framework regulations."""
        regulations = [
            {"id": "1", "title": "Reg 1"},
            {"id": "2", "title": "Reg 2"},
        ]
        mock_redis.get.return_value = json.dumps(regulations).encode()

        result = cache_service.get_framework_regulations("DORA_A")

        assert result == regulations

    def test_get_framework_regulations_miss(self, cache_service, mock_redis):
        """Test cache miss for framework regulations."""
        mock_redis.get.return_value = None

        result = cache_service.get_framework_regulations("DORA_A")

        assert result is None

    def test_invalidate_framework_cache_success(self, cache_service, mock_redis):
        """Test successful framework cache invalidation."""
        result = cache_service.invalidate_framework_cache("DORA_A")

        assert result is True
        mock_redis.delete.assert_called_once_with("framework:DORA_A")


class TestCacheServiceClearAll:
    """Tests for clearing all cache."""

    def test_clear_all_regulation_cache_success(self, cache_service, mock_redis):
        """Test successful clearing of all regulation cache."""
        mock_redis.keys.side_effect = [
            [b"regulation:1", b"regulation:2"],
            [b"framework:DORA_A"],
        ]

        result = cache_service.clear_all_regulation_cache()

        assert result is True
        assert mock_redis.delete.call_count == 2

    def test_clear_all_regulation_cache_empty(self, cache_service, mock_redis):
        """Test clearing empty cache."""
        mock_redis.keys.side_effect = [[], []]

        result = cache_service.clear_all_regulation_cache()

        assert result is True
        mock_redis.delete.assert_not_called()

    def test_clear_all_regulation_cache_redis_error(self, cache_service, mock_redis):
        """Test handling of Redis errors."""
        import redis

        mock_redis.keys.side_effect = redis.RedisError("Connection failed")

        result = cache_service.clear_all_regulation_cache()

        assert result is False


class TestCacheServiceStats:
    """Tests for cache statistics."""

    def test_get_cache_stats_success(self, cache_service, mock_redis):
        """Test getting cache statistics."""
        mock_redis.keys.side_effect = [
            [b"regulation:1", b"regulation:2", b"regulation:3"],
            [b"framework:DORA_A", b"framework:SOX"],
        ]

        stats = cache_service.get_cache_stats()

        assert stats["regulation_entries"] == 3
        assert stats["framework_entries"] == 2
        assert stats["total_entries"] == 5

    def test_get_cache_stats_empty(self, cache_service, mock_redis):
        """Test getting cache statistics for empty cache."""
        mock_redis.keys.side_effect = [[], []]

        stats = cache_service.get_cache_stats()

        assert stats["regulation_entries"] == 0
        assert stats["framework_entries"] == 0
        assert stats["total_entries"] == 0

    def test_get_cache_stats_redis_error(self, cache_service, mock_redis):
        """Test handling of Redis errors."""
        import redis

        mock_redis.keys.side_effect = redis.RedisError("Connection failed")

        stats = cache_service.get_cache_stats()

        assert stats == {}
