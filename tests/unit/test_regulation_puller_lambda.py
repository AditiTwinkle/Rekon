"""Unit tests for Regulation Puller Lambda function."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Mock the Lambda function module
import sys
from pathlib import Path

# Add lambda_functions to path for testing
lambda_path = Path(__file__).parent.parent.parent / "lambda_functions" / "regulation_puller"
sys.path.insert(0, str(lambda_path))


@pytest.fixture
def mock_aws_clients():
    """Mock AWS clients."""
    with patch("app.eventbridge") as mock_eb, \
         patch("app.rds_client") as mock_rds, \
         patch("app.ssm_client") as mock_ssm:
        yield {
            "eventbridge": mock_eb,
            "rds_client": mock_rds,
            "ssm_client": mock_ssm,
        }


@pytest.fixture
def mock_requests():
    """Mock requests library."""
    with patch("app.requests") as mock_req:
        yield mock_req


class TestCalculateContentHash:
    """Tests for content hash calculation."""

    def test_calculate_content_hash(self):
        """Test SHA-256 hash calculation."""
        from app import calculate_content_hash

        content = "Test content"
        hash_result = calculate_content_hash(content)

        # Verify it's a valid hex string
        assert isinstance(hash_result, str)
        assert len(hash_result) == 64  # SHA-256 produces 64 hex characters
        assert all(c in "0123456789abcdef" for c in hash_result)

    def test_calculate_content_hash_consistency(self):
        """Test that same content produces same hash."""
        from app import calculate_content_hash

        content = "Test content"
        hash1 = calculate_content_hash(content)
        hash2 = calculate_content_hash(content)

        assert hash1 == hash2

    def test_calculate_content_hash_different_content(self):
        """Test that different content produces different hash."""
        from app import calculate_content_hash

        hash1 = calculate_content_hash("Content 1")
        hash2 = calculate_content_hash("Content 2")

        assert hash1 != hash2


class TestFetchRegulationWithRetry:
    """Tests for regulation fetching with retry."""

    def test_fetch_regulation_success(self, mock_requests):
        """Test successful regulation fetch."""
        from app import fetch_regulation_with_retry

        mock_response = Mock()
        mock_response.text = "Regulation content"
        mock_response.raise_for_status = Mock()
        mock_requests.get.return_value = mock_response

        result = fetch_regulation_with_retry("DORA_A")

        assert result is not None
        assert result["framework"] == "DORA_A"
        assert result["content"] == "Regulation content"
        assert "content_hash" in result
        assert "fetch_timestamp" in result

    def test_fetch_regulation_timeout_retry(self, mock_requests):
        """Test retry on timeout."""
        from app import fetch_regulation_with_retry
        import requests

        # First two attempts timeout, third succeeds
        mock_response = Mock()
        mock_response.text = "Regulation content"
        mock_response.raise_for_status = Mock()

        mock_requests.get.side_effect = [
            requests.exceptions.Timeout(),
            requests.exceptions.Timeout(),
            mock_response,
        ]

        result = fetch_regulation_with_retry("DORA_A", max_retries=3)

        assert result is not None
        assert result["framework"] == "DORA_A"
        assert mock_requests.get.call_count == 3

    def test_fetch_regulation_all_retries_fail(self, mock_requests):
        """Test failure after all retries exhausted."""
        from app import fetch_regulation_with_retry, RegulationFetchError
        import requests

        mock_requests.get.side_effect = requests.exceptions.Timeout()

        with pytest.raises(RegulationFetchError):
            fetch_regulation_with_retry("DORA_A", max_retries=3)

    def test_fetch_regulation_invalid_framework(self):
        """Test fetch with invalid framework."""
        from app import fetch_regulation_with_retry

        with pytest.raises(ValueError, match="Unknown framework"):
            fetch_regulation_with_retry("INVALID_FRAMEWORK")

    def test_fetch_regulation_request_error(self, mock_requests):
        """Test handling of request errors."""
        from app import fetch_regulation_with_retry, RegulationFetchError
        import requests

        mock_requests.get.side_effect = requests.exceptions.RequestException("Connection error")

        with pytest.raises(RegulationFetchError):
            fetch_regulation_with_retry("DORA_A", max_retries=1)


class TestStoreRegulationInDatabase:
    """Tests for storing regulation in database."""

    def test_store_regulation_success(self, mock_aws_clients):
        """Test successful regulation storage."""
        from app import store_regulation_in_database

        mock_aws_clients["ssm_client"].get_parameter.return_value = {
            "Parameter": {"Value": "postgresql://localhost/rekon"}
        }

        regulation_data = {
            "framework": "DORA_A",
            "content_hash": "abc123",
            "fetch_timestamp": datetime.utcnow().isoformat(),
        }

        result = store_regulation_in_database(regulation_data)

        assert result is True

    def test_store_regulation_database_error(self, mock_aws_clients):
        """Test handling of database errors."""
        from app import store_regulation_in_database
        from botocore.exceptions import ClientError

        error_response = {"Error": {"Code": "ParameterNotFound", "Message": "Not found"}}
        mock_aws_clients["ssm_client"].get_parameter.side_effect = ClientError(
            error_response, "GetParameter"
        )

        regulation_data = {
            "framework": "DORA_A",
            "content_hash": "abc123",
            "fetch_timestamp": datetime.utcnow().isoformat(),
        }

        result = store_regulation_in_database(regulation_data)

        assert result is False


class TestEmitRegulationEvent:
    """Tests for emitting regulation events."""

    def test_emit_regulation_event_success(self, mock_aws_clients):
        """Test successful event emission."""
        from app import emit_regulation_event

        mock_aws_clients["eventbridge"].put_events.return_value = {"FailedEntryCount": 0}

        regulation_data = {
            "framework": "DORA_A",
            "content_hash": "abc123",
            "fetch_timestamp": datetime.utcnow().isoformat(),
            "url": "https://example.com",
        }

        result = emit_regulation_event(regulation_data)

        assert result is True
        mock_aws_clients["eventbridge"].put_events.assert_called_once()

    def test_emit_regulation_event_failure(self, mock_aws_clients):
        """Test event emission failure."""
        from app import emit_regulation_event

        mock_aws_clients["eventbridge"].put_events.return_value = {"FailedEntryCount": 1}

        regulation_data = {
            "framework": "DORA_A",
            "content_hash": "abc123",
            "fetch_timestamp": datetime.utcnow().isoformat(),
            "url": "https://example.com",
        }

        result = emit_regulation_event(regulation_data)

        assert result is False

    def test_emit_regulation_event_aws_error(self, mock_aws_clients):
        """Test handling of AWS errors."""
        from app import emit_regulation_event
        from botocore.exceptions import ClientError

        error_response = {"Error": {"Code": "AccessDenied", "Message": "Access denied"}}
        mock_aws_clients["eventbridge"].put_events.side_effect = ClientError(
            error_response, "PutEvents"
        )

        regulation_data = {
            "framework": "DORA_A",
            "content_hash": "abc123",
            "fetch_timestamp": datetime.utcnow().isoformat(),
            "url": "https://example.com",
        }

        result = emit_regulation_event(regulation_data)

        assert result is False


class TestLambdaHandler:
    """Tests for Lambda handler."""

    def test_lambda_handler_success(self, mock_aws_clients, mock_requests):
        """Test successful Lambda execution."""
        from app import lambda_handler

        mock_response = Mock()
        mock_response.text = "Regulation content"
        mock_response.raise_for_status = Mock()
        mock_requests.get.return_value = mock_response

        mock_aws_clients["ssm_client"].get_parameter.return_value = {
            "Parameter": {"Value": "postgresql://localhost/rekon"}
        }
        mock_aws_clients["eventbridge"].put_events.return_value = {"FailedEntryCount": 0}

        event = {"frameworks": ["DORA_A"]}
        context = Mock()

        result = lambda_handler(event, context)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert len(body["successful"]) == 1
        assert body["successful"][0] == "DORA_A"

    def test_lambda_handler_partial_failure(self, mock_aws_clients, mock_requests):
        """Test Lambda with partial failures."""
        from app import lambda_handler
        import requests

        # First framework succeeds, second fails
        mock_response = Mock()
        mock_response.text = "Regulation content"
        mock_response.raise_for_status = Mock()

        mock_requests.get.side_effect = [
            mock_response,
            requests.exceptions.Timeout(),
        ]

        mock_aws_clients["ssm_client"].get_parameter.return_value = {
            "Parameter": {"Value": "postgresql://localhost/rekon"}
        }
        mock_aws_clients["eventbridge"].put_events.return_value = {"FailedEntryCount": 0}

        event = {"frameworks": ["DORA_A", "SOX"]}
        context = Mock()

        result = lambda_handler(event, context)

        assert result["statusCode"] == 206  # Partial content
        body = json.loads(result["body"])
        assert len(body["successful"]) == 1
        assert len(body["failed"]) >= 1

    def test_lambda_handler_all_frameworks(self, mock_aws_clients, mock_requests):
        """Test Lambda with all frameworks."""
        from app import lambda_handler

        mock_response = Mock()
        mock_response.text = "Regulation content"
        mock_response.raise_for_status = Mock()
        mock_requests.get.return_value = mock_response

        mock_aws_clients["ssm_client"].get_parameter.return_value = {
            "Parameter": {"Value": "postgresql://localhost/rekon"}
        }
        mock_aws_clients["eventbridge"].put_events.return_value = {"FailedEntryCount": 0}

        event = {}  # No frameworks specified, should use all
        context = Mock()

        result = lambda_handler(event, context)

        assert result["statusCode"] in [200, 206]
        body = json.loads(result["body"])
        assert "successful" in body
        assert "failed" in body
