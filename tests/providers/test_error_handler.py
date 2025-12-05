"""Tests for centralized error handler."""

from unittest.mock import MagicMock

import httpx
import pytest

from gac.errors import AIError
from gac.providers.error_handler import handle_provider_errors


@handle_provider_errors("TestProvider")
def _function_success() -> str:
    """Helper function that succeeds."""
    return "success"


@handle_provider_errors("TestProvider")
def _function_auth_error():
    """Helper function that raises auth error."""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    raise httpx.HTTPStatusError("401", request=MagicMock(), response=mock_response)


@handle_provider_errors("TestProvider")
def _function_rate_limit_error():
    """Helper function that raises rate limit error."""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.text = "Too many requests"
    raise httpx.HTTPStatusError("429", request=MagicMock(), response=mock_response)


@handle_provider_errors("TestProvider")
def _function_not_found_error():
    """Helper function that raises not found error."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not found"
    raise httpx.HTTPStatusError("404", request=MagicMock(), response=mock_response)


@handle_provider_errors("TestProvider")
def _function_server_error():
    """Helper function that raises server error."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    raise httpx.HTTPStatusError("500", request=MagicMock(), response=mock_response)


@handle_provider_errors("TestProvider")
def _function_service_unavailable():
    """Helper function that raises service unavailable error."""
    mock_response = MagicMock()
    mock_response.status_code = 503
    mock_response.text = "Service unavailable"
    raise httpx.HTTPStatusError("503", request=MagicMock(), response=mock_response)


@handle_provider_errors("TestProvider")
def _function_timeout_error():
    """Helper function that raises timeout error."""
    raise httpx.TimeoutException("Request timeout")


@handle_provider_errors("TestProvider")
def _function_connection_error():
    """Helper function that raises connection error."""
    raise httpx.ConnectError("Connection failed")


@handle_provider_errors("TestProvider")
def _function_generic_error():
    """Helper function that raises generic error."""
    raise Exception("Generic error")


class TestErrorHandler:
    """Test error handler decorator."""

    def test_success_passthrough(self):
        """Test that successful results are passed through."""
        result = _function_success()
        assert result == "success"

    def test_auth_error_conversion(self):
        """Test that 401 errors are converted to authentication_error."""
        with pytest.raises(AIError) as exc_info:
            _function_auth_error()

        error = exc_info.value
        assert "authentication" in str(error).lower() or "invalid api key" in str(error).lower()

    def test_rate_limit_error_conversion(self):
        """Test that 429 errors are converted to rate_limit_error."""
        with pytest.raises(AIError) as exc_info:
            _function_rate_limit_error()

        error = exc_info.value
        assert "rate limit" in str(error).lower()

    def test_not_found_error_conversion(self):
        """Test that 404 errors are converted to model_error."""
        with pytest.raises(AIError) as exc_info:
            _function_not_found_error()

        error = exc_info.value
        assert "not found" in str(error).lower() or "model" in str(error).lower()

    def test_server_error_conversion(self):
        """Test that 500 errors are converted to connection_error."""
        with pytest.raises(AIError) as exc_info:
            _function_server_error()

        error = exc_info.value
        assert "server error" in str(error).lower() or "500" in str(error)

    def test_service_unavailable_conversion(self):
        """Test that 503 errors are converted to connection_error."""
        with pytest.raises(AIError) as exc_info:
            _function_service_unavailable()

        error = exc_info.value
        assert "unavailable" in str(error).lower() or "503" in str(error)

    def test_timeout_error_conversion(self):
        """Test that timeout errors are converted to timeout_error."""
        with pytest.raises(AIError) as exc_info:
            _function_timeout_error()

        error = exc_info.value
        assert "timeout" in str(error).lower()

    def test_connection_error_conversion(self):
        """Test that connection errors are converted to connection_error."""
        with pytest.raises(AIError) as exc_info:
            _function_connection_error()

        error = exc_info.value
        assert "connection" in str(error).lower()

    def test_generic_error_handling(self):
        """Test that generic errors are converted to model_error."""
        with pytest.raises(AIError):
            _function_generic_error()

    def test_error_has_cause(self):
        """Test that errors preserve the original exception as cause."""
        with pytest.raises(AIError) as exc_info:
            _function_timeout_error()

        error = exc_info.value
        assert error.__cause__ is not None
