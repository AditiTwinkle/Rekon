"""Unit tests for retry utilities."""

import pytest
import time
from unittest.mock import Mock, patch

from rekon.utils.retry import retry_with_backoff, RetryConfig


class TestRetryWithBackoff:
    """Tests for retry_with_backoff decorator."""

    def test_successful_on_first_attempt(self):
        """Test function succeeds on first attempt."""
        mock_func = Mock(return_value="success")

        @retry_with_backoff(max_retries=3)
        def test_func():
            return mock_func()

        result = test_func()

        assert result == "success"
        assert mock_func.call_count == 1

    def test_successful_after_retries(self):
        """Test function succeeds after retries."""
        mock_func = Mock(side_effect=[ValueError("fail"), ValueError("fail"), "success"])

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def test_func():
            return mock_func()

        result = test_func()

        assert result == "success"
        assert mock_func.call_count == 3

    def test_max_retries_exceeded(self):
        """Test exception raised when max retries exceeded."""
        mock_func = Mock(side_effect=ValueError("fail"))

        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def test_func():
            return mock_func()

        with pytest.raises(ValueError):
            test_func()

        assert mock_func.call_count == 2

    def test_specific_exception_caught(self):
        """Test only specified exceptions are caught."""
        mock_func = Mock(side_effect=TypeError("fail"))

        @retry_with_backoff(
            max_retries=3,
            exceptions=(ValueError,),
            base_delay=0.01,
        )
        def test_func():
            return mock_func()

        with pytest.raises(TypeError):
            test_func()

        assert mock_func.call_count == 1

    def test_exponential_backoff_timing(self):
        """Test exponential backoff timing."""
        mock_func = Mock(side_effect=[ValueError("fail"), ValueError("fail"), "success"])

        @retry_with_backoff(max_retries=3, base_delay=0.01, max_delay=1.0)
        def test_func():
            return mock_func()

        start = time.time()
        result = test_func()
        elapsed = time.time() - start

        assert result == "success"
        # Should have delays: 0.01 + 0.02 = 0.03 seconds minimum
        assert elapsed >= 0.02

    def test_max_delay_respected(self):
        """Test max delay is respected."""
        mock_func = Mock(side_effect=ValueError("fail"))

        @retry_with_backoff(
            max_retries=5,
            base_delay=10.0,
            max_delay=0.05,
        )
        def test_func():
            return mock_func()

        start = time.time()
        with pytest.raises(ValueError):
            test_func()
        elapsed = time.time() - start

        # Should not exceed max_delay * (max_retries - 1)
        assert elapsed < 0.3


class TestRetryConfig:
    """Tests for RetryConfig class."""

    def test_retry_config_initialization(self):
        """Test RetryConfig initialization."""
        config = RetryConfig(max_retries=5, base_delay=2.0, max_delay=30.0)

        assert config.max_retries == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 30.0

    def test_retry_config_defaults(self):
        """Test RetryConfig default values."""
        config = RetryConfig()

        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0

    def test_calculate_delay_exponential(self):
        """Test delay calculation with exponential backoff."""
        config = RetryConfig(base_delay=1.0, max_delay=60.0)

        assert config.calculate_delay(0) == 1.0
        assert config.calculate_delay(1) == 2.0
        assert config.calculate_delay(2) == 4.0
        assert config.calculate_delay(3) == 8.0

    def test_calculate_delay_respects_max(self):
        """Test delay calculation respects max delay."""
        config = RetryConfig(base_delay=1.0, max_delay=5.0)

        assert config.calculate_delay(0) == 1.0
        assert config.calculate_delay(1) == 2.0
        assert config.calculate_delay(2) == 4.0
        assert config.calculate_delay(3) == 5.0  # Capped at max_delay
        assert config.calculate_delay(4) == 5.0  # Still capped
