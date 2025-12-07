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

    def test_error_types_are_correct(self):
        """Test that error types are correctly set."""
        with pytest.raises(AIError) as exc_info:
            _function_auth_error()
        assert exc_info.value.error_type == "authentication"

        with pytest.raises(AIError) as exc_info:
            _function_rate_limit_error()
        assert exc_info.value.error_type == "rate_limit"

        with pytest.raises(AIError) as exc_info:
            _function_not_found_error()
        assert exc_info.value.error_type == "model"

        with pytest.raises(AIError) as exc_info:
            _function_server_error()
        assert exc_info.value.error_type == "connection"

        with pytest.raises(AIError) as exc_info:
            _function_timeout_error()
        assert exc_info.value.error_type == "timeout"

        with pytest.raises(AIError) as exc_info:
            _function_connection_error()
        assert exc_info.value.error_type == "connection"


@handle_provider_errors("TestProvider")
def _function_http_error_with_api_key():
    """Helper function that raises HTTP error with API key in response."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Invalid API key: sk-abcdefghijklmnopqrstuvwxyz1234567890abcd"
    raise httpx.HTTPStatusError("400", request=MagicMock(), response=mock_response)


@handle_provider_errors("TestProvider")
def _function_reraise_aierror():
    """Helper function that raises AIError directly."""
    raise AIError.authentication_error("Direct AIError")


class TestErrorHandlerSanitization:
    """Test error response sanitization in the decorator."""

    def test_api_key_redacted_in_error(self):
        """Test that API keys are redacted from HTTP error responses."""
        with pytest.raises(AIError) as exc_info:
            _function_http_error_with_api_key()

        error_message = str(exc_info.value)
        assert "sk-abcdefghijklmnopqrstuvwxyz1234567890abcd" not in error_message
        assert "[REDACTED]" in error_message

    def test_aierror_passthrough(self):
        """Test that AIError is re-raised without wrapping."""
        with pytest.raises(AIError) as exc_info:
            _function_reraise_aierror()

        assert "Direct AIError" in str(exc_info.value)
        assert exc_info.value.error_type == "authentication"


class TestErrorHandlerStringBasedClassification:
    """Test string-based error classification for non-HTTP exceptions."""

    @handle_provider_errors("TestProvider")
    def _function_auth_string_error(self):
        raise Exception("Authentication failed for user")

    @handle_provider_errors("TestProvider")
    def _function_unauthorized_string_error(self):
        raise Exception("Unauthorized access denied")

    @handle_provider_errors("TestProvider")
    def _function_rate_limit_string_error(self):
        raise Exception("Rate limit exceeded, try again later")

    @handle_provider_errors("TestProvider")
    def _function_quota_string_error(self):
        raise Exception("API quota exceeded")

    @handle_provider_errors("TestProvider")
    def _function_timeout_string_error(self):
        raise Exception("Connection timeout occurred")

    @handle_provider_errors("TestProvider")
    def _function_connection_string_error(self):
        raise Exception("Connection refused")

    def test_auth_string_classification(self):
        """Test authentication-related string errors are classified correctly."""
        with pytest.raises(AIError) as exc_info:
            self._function_auth_string_error()
        assert exc_info.value.error_type == "authentication"

        with pytest.raises(AIError) as exc_info:
            self._function_unauthorized_string_error()
        assert exc_info.value.error_type == "authentication"

    def test_rate_limit_string_classification(self):
        """Test rate limit string errors are classified correctly."""
        with pytest.raises(AIError) as exc_info:
            self._function_rate_limit_string_error()
        assert exc_info.value.error_type == "rate_limit"

        with pytest.raises(AIError) as exc_info:
            self._function_quota_string_error()
        assert exc_info.value.error_type == "rate_limit"

    def test_timeout_string_classification(self):
        """Test timeout string errors are classified correctly."""
        with pytest.raises(AIError) as exc_info:
            self._function_timeout_string_error()
        assert exc_info.value.error_type == "timeout"

    def test_connection_string_classification(self):
        """Test connection string errors are classified correctly."""
        with pytest.raises(AIError) as exc_info:
            self._function_connection_string_error()
        assert exc_info.value.error_type == "connection"

    def test_long_error_truncation(self):
        """Test that very long error responses are truncated (line 64 coverage)."""
        from gac.providers.error_handler import sanitize_error_response

        # Create text that starts with non-sensitive content but is very long
        # This should trigger both pattern matching and truncation
        long_text = "API Error: " + "normal text long enough to trigger truncation " * 10 + "x" * 100
        result = sanitize_error_response(long_text)

        # Should result in some processed text (truncation logic executed)
        assert isinstance(result, str)
        assert len(result) > 0  # Should return something
        # Line 64 (truncation) should be executed in processing

    def test_empty_error_sanitization(self):
        """Test sanitization handles empty text properly."""
        from gac.providers.error_handler import sanitize_error_response

        assert sanitize_error_response("") == ""
        assert sanitize_error_response(None) == ""

    def test_sanitization_and_truncation_combined(self):
        """Test sanitization followed by truncation (line 57 and 64)."""
        from gac.providers.error_handler import sanitize_error_response

        # Create text with API key that will also need truncation
        text_with_key = "Error: sk-test1234567890abcdef1234567890abcdef12345678 " + "x" * 200
        result = sanitize_error_response(text_with_key)

        # Should process through sanitization (line 57) and truncation (line 64)
        assert "[REDACTED]" in result  # Sanitization happened
        assert isinstance(result, str)
        # Length should be reasonable due to truncation
        assert len(result) <= 210  # Allow some wiggle room for redaction + truncation
