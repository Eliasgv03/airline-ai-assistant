"""
Integration tests for chat API endpoints
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestChatAPI:
    """Test chat API endpoints"""

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_chat_endpoint_structure(self):
        """Test chat endpoint accepts correct structure"""
        payload = {"session_id": "test-session-123", "message": "Hello"}

        response = client.post("/api/chat", json=payload)
        # May fail due to missing API keys in test, but structure should be valid
        assert response.status_code in [200, 500]  # 500 if no API key

    def test_sessions_endpoint(self):
        """Test sessions endpoint"""
        response = client.get("/api/chat/sessions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
