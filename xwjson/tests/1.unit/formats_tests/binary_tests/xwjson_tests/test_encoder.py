#exonware/xwjson/tests/1.unit/formats_tests/binary_tests/xwjson_tests/test_encoder.py
"""
Unit tests for XWJSONEncoder and XWJSONDecoder.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

import pytest
from exonware.xwjson.formats.binary.xwjson.encoder import (
    XWJSONEncoder, XWJSONDecoder, XWJSONHybridParser,
    XWJSON_MAGIC, HEADER_SIZE, FORMAT_JSON, FLAG_HAS_METADATA
)
from exonware.xwsystem.io.errors import SerializationError
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_encoder


def test_hybrid_parser_init():
    """Test XWJSONHybridParser initialization."""
    try:
        parser = XWJSONHybridParser()
        assert parser is not None
    except ImportError:
        pytest.skip("msgspec or orjson not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_encoder


def test_hybrid_parser_dumps_loads():
    """Test hybrid parser dumps/loads round-trip."""
    try:
        parser = XWJSONHybridParser()
        data = {"test": "data", "number": 42}
        encoded = parser.dumps(data)
        assert isinstance(encoded, bytes)
        decoded = parser.loads(encoded)
        assert decoded == data
    except ImportError:
        pytest.skip("msgspec or orjson not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_encoder


def test_encoder_init():
    """Test XWJSONEncoder initialization."""
    try:
        encoder = XWJSONEncoder()
        assert encoder is not None
    except ImportError:
        pytest.skip("msgpack not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_encoder


def test_encoder_encode_basic():
    """Test basic encoding."""
    try:
        encoder = XWJSONEncoder()
        data = {"test": "data"}
        encoded = encoder.encode(data)
        assert isinstance(encoded, bytes)
        assert len(encoded) > HEADER_SIZE
        assert encoded[:4] == XWJSON_MAGIC
    except ImportError:
        pytest.skip("msgpack not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_encoder


def test_encoder_encode_with_metadata():
    """Test encoding with metadata."""
    try:
        encoder = XWJSONEncoder()
        data = {"test": "data"}
        metadata = {"source": "json"}
        encoded = encoder.encode(
            data,
            metadata=metadata,
            format_code=FORMAT_JSON,
            flags=FLAG_HAS_METADATA
        )
        assert isinstance(encoded, bytes)
        assert len(encoded) > HEADER_SIZE
    except ImportError:
        pytest.skip("msgpack not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_encoder


def test_decoder_init():
    """Test XWJSONDecoder initialization."""
    try:
        decoder = XWJSONDecoder()
        assert decoder is not None
    except ImportError:
        pytest.skip("msgpack not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_encoder


def test_decoder_decode_round_trip():
    """Test decode round-trip."""
    try:
        encoder = XWJSONEncoder()
        decoder = XWJSONDecoder()
        data = {"test": "data", "number": 42}
        encoded = encoder.encode(data)
        decoded_data, metadata, index, header = decoder.decode(encoded)
        assert decoded_data == data
        assert header['magic'] == XWJSON_MAGIC
        assert header['version'] == 1
    except ImportError:
        pytest.skip("msgpack not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_encoder


def test_decoder_invalid_magic():
    """Test decoder with invalid magic bytes."""
    try:
        decoder = XWJSONDecoder()
        invalid_data = b'INVALID' + b'\x00' * 100
        with pytest.raises(SerializationError, match="Invalid.*magic"):
            decoder.decode(invalid_data)
    except ImportError:
        pytest.skip("msgpack not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_encoder


def test_decoder_too_short():
    """Test decoder with data too short."""
    try:
        decoder = XWJSONDecoder()
        short_data = b'XWJ1' + b'\x00' * 5  # Less than HEADER_SIZE
        with pytest.raises(SerializationError, match="too short"):
            decoder.decode(short_data)
    except ImportError:
        pytest.skip("msgpack not available")
