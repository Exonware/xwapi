#exonware/xwjson/src/exonware/xwjson/formats/binary/xwjson/schema.py
"""
XWJSON Schema Validator - Uses xwschema for schema validation
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 2025-01-XX
Schema validation using xwschema for fast compiled schemas (10x faster).
Priority 1 (Security): Safe schema validation, input validation
Priority 2 (Usability): Clear validation errors, helpful error messages
Priority 3 (Maintainability): Clean code, design patterns
Priority 4 (Performance): Fast compiled schemas, efficient validation
Priority 5 (Extensibility): Plugin system for custom validators
"""

from typing import Any
from pathlib import Path
# Use xwsystem schema validator discovery (avoids direct xwschema import, breaks circular dependency)
# This matches the pattern used in xwdata
_XWSCHEMA_VALIDATOR = None


def _get_xwschema_validator():
    """Get schema validator via xwsystem discovery (optional dependency via entry points)."""
    global _XWSCHEMA_VALIDATOR
    if _XWSCHEMA_VALIDATOR is False:  # Already checked and not available
        return None
    if _XWSCHEMA_VALIDATOR is None:  # Not checked yet
        try:
            from exonware.xwsystem.validation import get_schema_validator
            validator = get_schema_validator()
            _XWSCHEMA_VALIDATOR = validator if validator is not None else False
        except Exception:
            _XWSCHEMA_VALIDATOR = False
    return _XWSCHEMA_VALIDATOR if _XWSCHEMA_VALIDATOR is not False else None
# Fallback to jsonschema if xwschema not available
try:
    from jsonschema import Draft7Validator, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    Draft7Validator = None
    ValidationError = None
from exonware.xwsystem.io.errors import SerializationError
from exonware.xwsystem.io.serialization.formats.text import json as xw_json


class XWJSONSchemaValidator:
    """
    Schema validator using xwschema for fast compiled schemas.
    Uses xwsystem schema validator discovery to find xwschema (via entry points).
    Falls back to jsonschema if xwschema not available.
    This avoids direct xwschema imports and breaks circular dependencies.
    """

    def __init__(self, schema: dict | str | Path | None = None):
        """
        Initialize schema validator.
        Args:
            schema: Schema definition (dict, file path, or schema string)
        """
        self._schema = schema
        self._compiled_validator = None
        self._xwschema_validator = _get_xwschema_validator()
        if schema:
            self._compile_schema(schema)

    def _compile_schema(self, schema: dict | str | Path) -> None:
        """
        Compile schema for fast validation.
        Args:
            schema: Schema definition
        """
        # Load schema if it's a file path
        if isinstance(schema, (str, Path)):
            schema_path = Path(schema)
            if schema_path.exists():
                with open(schema_path, encoding='utf-8') as f:
                    schema = xw_json.load(f)
            else:
                # Try parsing as JSON string
                schema = xw_json.loads(str(schema))
        self._schema = schema
        # xwschema validator is obtained via xwsystem discovery (stored in __init__)
        # We don't need to compile/initialize it here - it validates on each call
        # Fallback to jsonschema
        if JSONSCHEMA_AVAILABLE and Draft7Validator:
            try:
                self._compiled_validator = Draft7Validator(schema)
            except Exception as e:
                raise SerializationError(f"Failed to compile schema: {e}") from e
        elif not self._xwschema_validator:
            raise ImportError(
                "Schema validation requires xwschema or jsonschema. "
                "Install with: pip install exonware-xwjson[full]"
            )

    def validate(self, data: Any) -> bool:
        """
        Validate data against schema.
        Args:
            data: Data to validate
        Returns:
            True if valid, False otherwise
        """
        if not self._schema:
            return True  # No schema = everything is valid
        # Prefer compiled jsonschema validator when available.
        # It avoids provider dispatch overhead in hot validation paths.
        if self._compiled_validator:
            return self._validate_with_jsonschema(data)
        # Use xwschema validator if available (via xwsystem discovery)
        if self._xwschema_validator:
            try:
                # Use xwsystem ISchemaProvider interface (validate_schema returns tuple[bool, list[str]])
                is_valid, _errors = self._xwschema_validator.validate_schema(data, self._schema)
                return is_valid
            except Exception:
                # Fallback to jsonschema if xwschema fails
                return self._validate_with_jsonschema(data)
        # Use jsonschema
        return self._validate_with_jsonschema(data)

    def _validate_with_jsonschema(self, data: Any) -> bool:
        """Validate using jsonschema (fallback)."""
        if not self._compiled_validator:
            return True
        try:
            self._compiled_validator.validate(data)
            return True
        except ValidationError:
            return False
        except Exception:
            return False

    async def validate_async(self, data: Any) -> bool:
        """
        Validate data asynchronously (if xwschema supports it).
        Args:
            data: Data to validate
        Returns:
            True if valid, False otherwise
        """
        # Try to use xwschema validator if available
        if self._xwschema_validator:
            try:
                # Use xwsystem ISchemaProvider interface
                # For async, run the sync validate_schema in executor
                import asyncio
                loop = asyncio.get_event_loop()
                is_valid, _errors = await loop.run_in_executor(
                    None,
                    lambda: self._xwschema_validator.validate_schema(data, self._schema)
                )
                return is_valid
            except Exception:
                # Fallback to synchronous validation
                pass
        # Fallback to synchronous validation
        # Run in executor to avoid blocking
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.validate, data)

    def get_validation_errors(self, data: Any) -> list[str]:
        """
        Get validation errors for data.
        Args:
            data: Data to validate
        Returns:
            list of validation error messages
        """
        errors = []
        if not self._schema:
            return errors
        # Use xwschema validator if available (via xwsystem discovery)
        if self._xwschema_validator:
            try:
                # Use xwsystem ISchemaProvider interface (validate_schema returns tuple[bool, list[str]])
                _is_valid, errors = self._xwschema_validator.validate_schema(data, self._schema)
                return errors if errors else []
            except Exception:
                pass
        # Use jsonschema for error messages
        if self._compiled_validator:
            try:
                errors_list = list(self._compiled_validator.iter_errors(data))
                return [str(error) for error in errors_list]
            except Exception:
                pass
        return errors

    def load_schema(self, schema_path: str | Path) -> None:
        """
        Load schema from file.
        Args:
            schema_path: Path to schema file
        """
        self._compile_schema(schema_path)

    def save_schema(self, schema_path: str | Path) -> None:
        """
        Save schema to file.
        Args:
            schema_path: Path to save schema file
        """
        if not self._schema:
            raise SerializationError("No schema to save")
        schema_path = Path(schema_path)
        with open(schema_path, 'w', encoding='utf-8') as f:
            xw_json.dump(self._schema, f, indent=2)
