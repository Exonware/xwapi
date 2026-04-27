#exonware/xwapi/tests/conftest.py
"""
Pytest configuration and fixtures for xwapi tests.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from exonware.xwapi.config import XWAPIConfig


@pytest.fixture
def sample_api_config():
    """Sample API configuration for testing."""
    return XWAPIConfig(
        title="Test API",
        version="1.0.0",
        description="Test API for xwapi testing",
    )


@pytest.fixture
def sample_app(sample_api_config):
    """Create a sample FastAPI app for testing."""
    from exonware.xwapi.common.app import create_app

    return create_app(config=sample_api_config)


@pytest.fixture
def test_client(sample_app):
    """Create a test client for FastAPI app."""
    from fastapi.testclient import TestClient

    return TestClient(sample_app)


@pytest.fixture
def sample_openapi_schema():
    """Sample OpenAPI schema for testing."""
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0",
            "description": "Test API for xwapi testing",
        },
        "paths": {},
    }
