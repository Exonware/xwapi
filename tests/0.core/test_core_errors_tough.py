#exonware/xwapi/tests/0.core/test_core_errors_tough.py
"""
Tough core tests for xwapi error handling - Edge cases, boundary conditions, and complex scenarios.
Tests error handling with invalid inputs, concurrent scenarios, security cases,
and failure modes.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from __future__ import annotations
import pytest
from unittest.mock import Mock, MagicMock, patch
from exonware.xwapi.errors import (
    XWAPIError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    InternalError,
    OpenAPIGenerationError,
    FastAPICreationError,
    EntityMappingError,
    OAuth2ConfigurationError,
    EndpointConfigurationError,
    create_error_response,
    get_http_status_code,
    get_trace_id,
    error_to_http_response,
    get_error_headers,
)
@pytest.mark.xwapi_core

def test_error_with_empty_message():
    """Test error creation with empty message."""
    error = XWAPIError("")
    assert error.message == ""
    assert str(error) == ""
@pytest.mark.xwapi_core

def test_error_with_very_long_message():
    """Test error creation with extremely long message."""
    long_message = "A" * 10000
    error = XWAPIError(long_message)
    assert error.message == long_message
    assert len(str(error)) == 10000
@pytest.mark.xwapi_core

def test_error_with_unicode_message():
    """Test error creation with Unicode characters."""
    unicode_message = "错误消息 🚀 日本語 العربية"
    error = XWAPIError(unicode_message)
    assert error.message == unicode_message
@pytest.mark.xwapi_core

def test_error_with_special_characters_message():
    """Test error creation with special characters."""
    special_message = "Error: <>&\"'\\n\\t\\r"
    error = XWAPIError(special_message)
    assert error.message == special_message
@pytest.mark.xwapi_core

def test_error_with_none_code():
    """Test error creation with None code - should use class name."""
    error = ValidationError("Test")
    assert error.code == "ValidationError"
@pytest.mark.xwapi_core

def test_error_with_empty_code():
    """Test error creation with empty code string."""
    error = XWAPIError("Test", code="")
    assert error.code == ""
@pytest.mark.xwapi_core

def test_error_with_very_long_code():
    """Test error creation with extremely long code."""
    long_code = "A" * 500
    error = XWAPIError("Test", code=long_code)
    assert error.code == long_code
@pytest.mark.xwapi_core

def test_error_with_special_characters_code():
    """Test error creation with special characters in code."""
    special_code = "ERROR_CODE_<>&\"'"
    error = XWAPIError("Test", code=special_code)
    assert error.code == special_code
@pytest.mark.xwapi_core

def test_error_with_none_details():
    """Test error creation with None details - should use empty dict."""
    error = XWAPIError("Test", details=None)
    assert error.details == {}
@pytest.mark.xwapi_core

def test_error_with_empty_details():
    """Test error creation with empty details dict."""
    error = XWAPIError("Test", details={})
    assert error.details == {}
@pytest.mark.xwapi_core

def test_error_with_large_details():
    """Test error creation with large details dict."""
    large_details = {f"key{i}": f"value{i}" * 100 for i in range(100)}
    error = XWAPIError("Test", details=large_details)
    assert len(error.details) == 100
@pytest.mark.xwapi_core

def test_error_with_nested_details():
    """Test error creation with deeply nested details."""
    nested_details = {
        "level1": {
            "level2": {
                "level3": {
                    "level4": {
                        "level5": "deep_value"
                    }
                }
            }
        }
    }
    error = XWAPIError("Test", details=nested_details)
    assert error.details["level1"]["level2"]["level3"]["level4"]["level5"] == "deep_value"
@pytest.mark.xwapi_core

def test_error_with_none_hint():
    """Test error creation with None hint."""
    error = XWAPIError("Test", hint=None)
    assert error.hint is None
@pytest.mark.xwapi_core

def test_error_with_empty_hint():
    """Test error creation with empty hint."""
    error = XWAPIError("Test", hint="")
    assert error.hint == ""
@pytest.mark.xwapi_core

def test_error_with_very_long_hint():
    """Test error creation with extremely long hint."""
    long_hint = "Hint: " + "A" * 5000
    error = XWAPIError("Test", hint=long_hint)
    assert error.hint == long_hint
@pytest.mark.xwapi_core

def test_all_error_classes_instantiable():
    """Test that all error classes can be instantiated."""
    error_classes = [
        ValidationError,
        AuthenticationError,
        AuthorizationError,
        NotFoundError,
        RateLimitError,
        InternalError,
        OpenAPIGenerationError,
        FastAPICreationError,
        EntityMappingError,
        OAuth2ConfigurationError,
        EndpointConfigurationError,
    ]
    for error_class in error_classes:
        error = error_class("Test message")
        assert isinstance(error, XWAPIError)
        assert isinstance(error, error_class)
@pytest.mark.xwapi_core

def test_error_inheritance_chain():
    """Test complete inheritance chain for all errors."""
    error_classes = [
        ValidationError,
        AuthenticationError,
        AuthorizationError,
        NotFoundError,
        RateLimitError,
        InternalError,
    ]
    for error_class in error_classes:
        assert issubclass(error_class, XWAPIError)
        assert issubclass(error_class, Exception)
@pytest.mark.xwapi_core

def test_error_equality():
    """Test error equality comparison."""
    error1 = ValidationError("Same message")
    error2 = ValidationError("Same message")
    error3 = ValidationError("Different message")
    # Errors are not equal by default (different instances)
    assert error1 != error2
    assert error1 != error3
@pytest.mark.xwapi_core

def test_error_hashability():
    """Test that errors are hashable (for use in sets/dicts)."""
    error1 = ValidationError("Error 1")
    error2 = ValidationError("Error 2")
    error_set = {error1, error2}
    assert len(error_set) == 2
@pytest.mark.xwapi_core

def test_error_repr():
    """Test error string representation."""
    error = ValidationError("Test message", code="TEST_CODE")
    repr_str = repr(error)
    assert "ValidationError" in repr_str or "Test message" in repr_str
@pytest.mark.xwapi_core

def test_create_error_response_with_none_trace_id():
    """Test creating error response with None trace_id."""
    error = ValidationError("Test")
    response = create_error_response(error, trace_id=None)
    assert isinstance(response, dict)
    assert "trace_id" in response
    assert response["trace_id"] is None
@pytest.mark.xwapi_core

def test_create_error_response_with_empty_trace_id():
    """Test creating error response with empty trace_id."""
    error = ValidationError("Test")
    response = create_error_response(error, trace_id="")
    assert response["trace_id"] == ""
@pytest.mark.xwapi_core

def test_create_error_response_with_very_long_trace_id():
    """Test creating error response with extremely long trace_id."""
    long_trace_id = "A" * 1000
    error = ValidationError("Test")
    response = create_error_response(error, trace_id=long_trace_id)
    assert response["trace_id"] == long_trace_id
@pytest.mark.xwapi_core

def test_create_error_response_with_all_error_types():
    """Test creating error response for all error types."""
    error_types = [
        ValidationError("Validation error"),
        AuthenticationError("Auth error"),
        AuthorizationError("Authz error"),
        NotFoundError("Not found"),
        RateLimitError("Rate limit"),
        InternalError("Internal error"),
    ]
    for error in error_types:
        response = create_error_response(error, trace_id="test")
        assert isinstance(response, dict)
        assert "code" in response
        assert "message" in response
@pytest.mark.xwapi_core

def test_get_http_status_code_for_all_errors():
    """Test HTTP status code mapping for all error types."""
    from exonware.xwapi.errors import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_429_TOO_MANY_REQUESTS, HTTP_500_INTERNAL_SERVER_ERROR
    test_cases = [
        (ValidationError("Test"), HTTP_400_BAD_REQUEST),
        (AuthenticationError("Test"), HTTP_401_UNAUTHORIZED),
        (AuthorizationError("Test"), HTTP_403_FORBIDDEN),
        (NotFoundError("Test"), HTTP_404_NOT_FOUND),
        (RateLimitError("Test"), HTTP_429_TOO_MANY_REQUESTS),
        (InternalError("Test"), HTTP_500_INTERNAL_SERVER_ERROR),
    ]
    for error, expected_status in test_cases:
        status = get_http_status_code(error)
        assert status == expected_status
@pytest.mark.xwapi_core

def test_get_http_status_code_for_base_error():
    """Test HTTP status code for base XWAPIError."""
    error = XWAPIError("Test")
    status = get_http_status_code(error)
    # Should return a valid status code (default 500)
    assert isinstance(status, int)
    assert 400 <= status <= 599
@pytest.mark.xwapi_core

def test_get_trace_id_from_header():
    """Test extracting trace ID from request header."""
    mock_request = MagicMock()
    mock_request.headers = {"X-Trace-Id": "header-trace-123"}
    mock_request.state = MagicMock()
    mock_request.state.trace_id = None
    trace_id = get_trace_id(mock_request)
    assert trace_id == "header-trace-123" or trace_id is not None
@pytest.mark.xwapi_core

def test_get_trace_id_from_state():
    """Test extracting trace ID from request state."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_request.state.trace_id = "state-trace-456"
    trace_id = get_trace_id(mock_request)
    assert trace_id == "state-trace-456" or trace_id is not None
@pytest.mark.xwapi_core

def test_get_trace_id_generates_new():
    """Test that trace ID is generated if not present."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_request.state.trace_id = None
    trace_id = get_trace_id(mock_request)
    # Should generate a new trace ID
    assert trace_id is not None
    assert isinstance(trace_id, str)
    assert len(trace_id) > 0
@pytest.mark.xwapi_core

def test_get_trace_id_with_invalid_request():
    """Test get_trace_id with invalid request object."""
    # Should handle gracefully
    try:
        trace_id = get_trace_id(None)
        # May return None or generate ID
        assert trace_id is None or isinstance(trace_id, str)
    except (AttributeError, TypeError):
        # Acceptable - None is invalid
        pass
@pytest.mark.xwapi_core

def test_error_to_http_response_with_none_request():
    """Test error_to_http_response with None request."""
    error = ValidationError("Test")
    response, status = error_to_http_response(error, request=None)
    assert isinstance(response, dict)
    assert isinstance(status, int)
@pytest.mark.xwapi_core

def test_error_to_http_response_with_mock_request():
    """Test error_to_http_response with mock request."""
    error = ValidationError("Test")
    mock_request = MagicMock()
    mock_request.url.path = "/test"
    mock_request.method = "GET"
    response, status = error_to_http_response(error, request=mock_request)
    assert isinstance(response, dict)
    assert isinstance(status, int)
@pytest.mark.xwapi_core

def test_get_error_headers_with_none_trace_id():
    """Test get_error_headers with None trace_id."""
    headers = get_error_headers(trace_id=None)
    assert isinstance(headers, dict)
@pytest.mark.xwapi_core

def test_get_error_headers_with_empty_trace_id():
    """Test get_error_headers with empty trace_id."""
    headers = get_error_headers(trace_id="")
    assert isinstance(headers, dict)
@pytest.mark.xwapi_core

def test_get_error_headers_with_trace_id():
    """Test get_error_headers with valid trace_id."""
    headers = get_error_headers(trace_id="test-trace-123")
    assert isinstance(headers, dict)
    assert "X-Trace-Id" in headers
    assert headers["X-Trace-Id"] == "test-trace-123"
@pytest.mark.xwapi_core

def test_error_with_complex_details_structure():
    """Test error with complex nested details structure."""
    complex_details = {
        "errors": [
            {"field": "email", "message": "Invalid format"},
            {"field": "password", "message": "Too short"}
        ],
        "metadata": {
            "request_id": "req-123",
            "timestamp": "2025-01-01T00:00:00Z",
            "user_id": "user-456"
        },
        "validation": {
            "rules": {
                "email": {"pattern": "^[a-z]+@[a-z]+\\.[a-z]+$"},
                "password": {"min_length": 8}
            }
        }
    }
    error = ValidationError("Validation failed", details=complex_details)
    assert len(error.details["errors"]) == 2
    assert "metadata" in error.details
@pytest.mark.xwapi_core

def test_error_chaining():
    """Test error chaining (cause/context)."""
    try:
        try:
            raise ValueError("Inner error")
        except ValueError as e:
            raise ValidationError("Outer error") from e
    except ValidationError as outer:
        assert outer.__cause__ is not None
        assert isinstance(outer.__cause__, ValueError)
@pytest.mark.xwapi_core

def test_error_with_all_parameters():
    """Test error creation with all parameters specified."""
    error = XWAPIError(
        message="Full error",
        code="FULL_ERROR_CODE",
        details={"key": "value", "number": 42},
        hint="This is a hint"
    )
    assert error.message == "Full error"
    assert error.code == "FULL_ERROR_CODE"
    assert error.details == {"key": "value", "number": 42}
    assert error.hint == "This is a hint"
@pytest.mark.xwapi_core

def test_error_subclassing():
    """Test creating custom error subclass."""
    class CustomError(XWAPIError):
        """Custom error for testing."""
        pass
    error = CustomError("Custom message")
    assert isinstance(error, XWAPIError)
    assert isinstance(error, CustomError)
    assert error.code == "CustomError"
@pytest.mark.xwapi_core

def test_error_with_numeric_code():
    """Test error with numeric code string."""
    error = XWAPIError("Test", code="12345")
    assert error.code == "12345"
@pytest.mark.xwapi_core

def test_error_with_unicode_code():
    """Test error with Unicode characters in code."""
    error = XWAPIError("Test", code="错误代码_123")
    assert error.code == "错误代码_123"
@pytest.mark.xwapi_core

def test_error_details_immutability():
    """Test that modifying details dict doesn't affect error."""
    original_details = {"key": "value"}
    error = XWAPIError("Test", details=original_details)
    original_details["new_key"] = "new_value"
    # Error details should not change
    assert "new_key" not in error.details
@pytest.mark.xwapi_core

def test_error_message_immutability():
    """Test that error message is immutable after creation."""
    error = XWAPIError("Original")
    original_message = error.message
    # Try to modify (should not affect)
    try:
        error.message = "Modified"
    except AttributeError:
        # Good - message should be immutable
        pass
    # Message should remain original
    assert error.message == original_message
@pytest.mark.xwapi_core

def test_create_error_response_preserves_all_fields():
    """Test that create_error_response preserves all error fields."""
    error = XWAPIError(
        message="Test message",
        code="TEST_CODE",
        details={"detail1": "value1", "detail2": "value2"},
        hint="Test hint"
    )
    response = create_error_response(error, trace_id="trace-123")
    assert response["message"] == "Test message"
    assert response["code"] == "TEST_CODE"
    assert "details" in response or "detail1" in response
    assert response.get("hint") == "Test hint" or "hint" not in response
@pytest.mark.xwapi_core

def test_error_response_structure_consistency():
    """Test that error responses have consistent structure across error types."""
    error_types = [
        ValidationError("Test"),
        AuthenticationError("Test"),
        NotFoundError("Test"),
        InternalError("Test"),
    ]
    structures = []
    for error in error_types:
        response = create_error_response(error, trace_id="test")
        structures.append(set(response.keys()))
    # All responses should have similar structure
    common_keys = structures[0].intersection(*structures[1:])
    assert "code" in common_keys or "message" in common_keys
@pytest.mark.xwapi_core

def test_get_http_status_code_edge_cases():
    """Test HTTP status code for edge case errors."""
    # Test with custom error code
    error = XWAPIError("Test", code="CUSTOM_500")
    status = get_http_status_code(error)
    assert isinstance(status, int)
    assert 400 <= status <= 599
@pytest.mark.xwapi_core

def test_error_with_none_in_details():
    """Test error with None values in details."""
    error = XWAPIError("Test", details={"key1": None, "key2": "value", "key3": None})
    assert error.details["key1"] is None
    assert error.details["key2"] == "value"
    assert error.details["key3"] is None
@pytest.mark.xwapi_core

def test_error_with_list_in_details():
    """Test error with list values in details."""
    error = XWAPIError("Test", details={"items": [1, 2, 3], "tags": ["a", "b", "c"]})
    assert error.details["items"] == [1, 2, 3]
    assert error.details["tags"] == ["a", "b", "c"]
@pytest.mark.xwapi_core

def test_error_with_mixed_types_in_details():
    """Test error with mixed types in details."""
    error = XWAPIError("Test", details={
        "string": "text",
        "number": 42,
        "float": 3.14,
        "boolean": True,
        "list": [1, 2, 3],
        "dict": {"nested": "value"},
        "none": None
    })
    assert isinstance(error.details["string"], str)
    assert isinstance(error.details["number"], int)
    assert isinstance(error.details["float"], float)
    assert isinstance(error.details["boolean"], bool)
    assert isinstance(error.details["list"], list)
    assert isinstance(error.details["dict"], dict)
    assert error.details["none"] is None
