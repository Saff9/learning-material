import pytest
from app import create_app
from models import db

@pytest.fixture
def app():
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        API_TITLE = "Test API"
        API_VERSION = "v1"
        OPENAPI_VERSION = "3.0.2"
        
    app = create_app(TestConfig)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_user(client):
    response = client.post("/users/", json={"username": "testuser", "email": "test@example.com"})
    assert response.status_code == 201
    assert response.json["username"] == "testuser"

def test_get_users(client):
    client.post("/users/", json={"username": "user1", "email": "1@example.com"})
    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json) >= 1
