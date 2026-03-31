"""
API request/response schema validation for xwapi.
Uses xwschema for validation logic.
"""

from typing import Any, Optional
from exonware.xwsystem import get_logger
from exonware.xwschema import XWSchema
from .contracts import IAPIRulesValidator, IRequestValidator
from ..errors import XWAPIError
logger = get_logger(__name__)


class RequestValidator(IRequestValidator):
    """API request/response validator using xwschema."""

    def __init__(self):
        self._validator = XWSchema({})
        logger.debug("RequestValidator initialized")

    async def validate_request(
        self,
        request_data: Any,
        schema: dict[str, Any],
        endpoint: str,
        **opts
    ) -> dict[str, Any]:
        try:
            is_valid, errors = self._validator.validate_schema(request_data, schema)
            return {
                'valid': is_valid,
                'errors': errors if isinstance(errors, list) else [str(errors)] if errors else [],
                'endpoint': endpoint,
                'type': 'request'
            }
        except Exception as e:
            logger.error(f"Request validation failed for endpoint {endpoint}: {e}")
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'endpoint': endpoint,
                'type': 'request'
            }

    async def validate_response(
        self,
        response_data: Any,
        schema: dict[str, Any],
        endpoint: str,
        **opts
    ) -> dict[str, Any]:
        try:
            is_valid, errors = self._validator.validate_schema(response_data, schema)
            return {
                'valid': is_valid,
                'errors': errors if isinstance(errors, list) else [str(errors)] if errors else [],
                'endpoint': endpoint,
                'type': 'response'
            }
        except Exception as e:
            logger.error(f"Response validation failed for endpoint {endpoint}: {e}")
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'endpoint': endpoint,
                'type': 'response'
            }
ResponseValidator = RequestValidator
APIRulesValidator = RequestValidator
