"""
Unit tests for the health check endpoint
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    from app.main import app
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for the /health endpoint"""

    def test_health_check_healthy(self, client):
        """Test health check when all environment variables are set"""
        with patch.dict(os.environ, {
            "CLIENT_ID": "test_client_id",
            "TENANT_ID": "test_tenant_id",
            "REDIRECT_URI": "http://localhost:8000/auth/callback"
        }):
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["message"] == "Service is running"
            assert data["environment"]["client_id_set"] is True
            assert data["environment"]["tenant_id_set"] is True
            assert data["environment"]["redirect_uri_set"] is True

    def test_health_check_unhealthy_missing_all_vars(self, client):
        """Test health check when all environment variables are missing"""
        with patch.dict(os.environ, {}, clear=True):
            response = client.get("/health")
            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "unhealthy"
            assert "Missing required environment variables" in data["message"]
            assert len(data["missing_vars"]) == 3
            assert "CLIENT_ID" in data["missing_vars"]
            assert "TENANT_ID" in data["missing_vars"]
            assert "REDIRECT_URI" in data["missing_vars"]

    def test_health_check_unhealthy_missing_some_vars(self, client):
        """Test health check when some environment variables are missing"""
        with patch.dict(os.environ, {"CLIENT_ID": "test_id"}, clear=True):
            response = client.get("/health")
            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "unhealthy"
            assert len(data["missing_vars"]) == 2
            assert "TENANT_ID" in data["missing_vars"]
            assert "REDIRECT_URI" in data["missing_vars"]
            assert "CLIENT_ID" not in data["missing_vars"]


class TestRootEndpoint:
    """Tests for the / root endpoint"""

    def test_root_endpoint(self, client):
        """Test the root endpoint returns welcome message"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to Pepper - Outlook AI Agent"
        assert data["version"] == "0.1.0"
        assert data["docs"] == "/docs"
