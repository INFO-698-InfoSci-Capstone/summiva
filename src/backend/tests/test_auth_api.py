import pytest
from fastapi.testclient import TestClient
from src.backend.auth.main import app
from sqlalchemy.orm import Session
from src.backend.auth.models.user import User

client = TestClient(app)

def test_register_user(db_session: Session):
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert db_session.query(User).filter(User.email == "test@example.com").first() is not None

def test_register_user_email_already_exists(db_session: Session):
    user_data = {
        "email": "test2@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    client.post("/register", json=user_data)
    response = client.post("/register", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_user(db_session: Session):
    user_data = {
        "email": "test3@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    client.post("/register", json=user_data)
    response = client.post("/login", json={"email": "test3@example.com", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_user_wrong_credentials(db_session: Session):
    user_data = {
        "email": "test4@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    client.post("/register", json=user_data)
    response = client.post("/login", json={"email": "test4@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication failed"

def test_get_current_user(db_session: Session):
    user_data = {
        "email": "test5@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    client.post("/register", json=user_data)
    login_response = client.post("/login", json={"email": "test5@example.com", "password": "testpassword"})
    access_token = login_response.json()["access_token"]
    response = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "test5@example.com"

def test_get_current_user_wrong_token(db_session: Session):
    response = client.get("/users/me", headers={"Authorization": "Bearer wrongtoken"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication failed"