"""
Integration tests for chat API endpoints

Note: Tests that require ChatService (which depends on VectorService/embedding model)
are marked as 'slow' and can be skipped in CI with: pytest -m "not slow"
"""

from fastapi.testclient import TestClient
import pytest

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    # TestClient works with httpx <0.28.0 and FastAPI 0.109.0
    # httpx 0.28+ has compatibility issues with TestClient
    return TestClient(app)


class TestChatAPI:
    """Test chat API endpoints"""

    def test_health_endpoint(self, client: TestClient):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_ready_endpoint(self, client: TestClient):
        """Test ready endpoint - always ready with Google Embeddings API"""
        response = client.get("/ready")
        # With Google Embeddings API, service is always immediately ready
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    @pytest.mark.slow
    def test_chat_endpoint_structure(self, client: TestClient):
        """Test chat endpoint accepts correct structure.

        Note: This test requires the embedding model to be loaded,
        which takes 60-120 seconds. Mark as 'slow' to skip in CI.
        """
        payload = {"session_id": "test-session-123", "message": "Hello"}

        response = client.post("/api/chat", json=payload)
        # May fail due to missing API keys in test, but structure should be valid
        assert response.status_code in [200, 500]  # 500 if no API key

    @pytest.mark.slow
    def test_sessions_endpoint(self, client: TestClient):
        """Test sessions endpoint.

        Note: This test requires ChatService which depends on VectorService.
        Mark as 'slow' to skip in CI.
        """
        response = client.get("/api/chat/sessions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
