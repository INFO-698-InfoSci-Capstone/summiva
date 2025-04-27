import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app

client = TestClient(app)

@pytest.fixture
def mock_auth(mocker):
    """Patch fetch_user_from_auth to simulate a valid user from Auth Service."""
    with patch("src.api.endpoints.summarize.fetch_user_from_auth", return_value={"id": "testuser"}):
        yield

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert "Summarization Service running with Celery + RabbitMQ" in response.text

def test_summarize_no_token():
    # No Authorization => 401
    response = client.post("/api/v1/summarize", json={"text":"Hello World"})
    assert response.status_code == 401

def test_summarize_queued(mock_auth):
    response = client.post(
        "/api/v1/summarize",
        headers={"Authorization": "Bearer faketoken"},
        json={"text": "Hello from async summarization"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert "doc_id" in data
