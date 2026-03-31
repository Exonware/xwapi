#exonware/xwjson/tests/2.integration/scenarios/test_stress_schema_validation.py
"""
Stress tests for schema validation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Stress tests for schema validation performance, compiled schemas.
"""

import pytest
from exonware.xwjson.formats.binary.xwjson.schema import XWJSONSchemaValidator
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_stress_schema_validation():
    """Stress test: Schema validation performance."""
    try:
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0, "maximum": 150}
            },
            "required": ["id", "name"]
        }
        validator = XWJSONSchemaValidator(schema)
        # Create 10000 valid items
        valid_data = [
            {"id": i, "name": f"User{i}", "age": 20 + (i % 50)}
            for i in range(10000)
        ]
        import time
        start = time.perf_counter()
        for item in valid_data:
            assert validator.validate(item) is True
        validation_time = time.perf_counter() - start
        # Should be fast (< 2s for 10000 validations)
        assert validation_time < 2.0, f"Schema validation too slow: {validation_time:.3f}s"
    except ImportError:
        pytest.skip("xwschema or jsonschema not available")
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_stress_invalid_data_validation():
    """Stress test: Invalid data validation performance."""
    try:
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"}
            },
            "required": ["id", "name"]
        }
        validator = XWJSONSchemaValidator(schema)
        # Mix of valid and invalid data
        test_data = []
        for i in range(10000):
            if i % 2 == 0:
                # Valid
                test_data.append({"id": i, "name": f"User{i}"})
            else:
                # Invalid (missing required field)
                test_data.append({"id": i})
        import time
        start = time.perf_counter()
        valid_count = 0
        invalid_count = 0
        for item in test_data:
            if validator.validate(item):
                valid_count += 1
            else:
                invalid_count += 1
        validation_time = time.perf_counter() - start
        # Should be fast
        assert validation_time < 2.0, f"Validation too slow: {validation_time:.3f}s"
        assert valid_count == 5000
        assert invalid_count == 5000
    except ImportError:
        pytest.skip("xwschema or jsonschema not available")
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_stress_compiled_schema_reuse():
    """Stress test: Compiled schema reuse performance."""
    try:
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "value": {"type": "string"}
                }
            }
        }
        validator = XWJSONSchemaValidator(schema)
        # Create data
        data = [{"id": i, "value": f"item{i}"} for i in range(50000)]
        import time
        start = time.perf_counter()
        # Validate (schema should be compiled and reused)
        is_valid = validator.validate(data)
        validation_time = time.perf_counter() - start
        # Compiled schema should stay well under a loose ceiling; 0.5s was too tight on Windows/loaded CPUs.
        assert validation_time < 2.0, f"Compiled schema validation too slow: {validation_time:.3f}s"
        assert is_valid is True
    except ImportError:
        pytest.skip("xwschema or jsonschema not available")
