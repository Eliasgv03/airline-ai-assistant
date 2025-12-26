"""
Pytest configuration for airline-ai-assistant backend tests
"""

import os

import pytest

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["LOG_LEVEL"] = "debug"


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Get test database URL"""
    return os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/airline_ai_test"
    )


@pytest.fixture(scope="session")
def mock_llm_api_key() -> str:
    """Mock API key for testing"""
    return "test-api-key-12345"


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
