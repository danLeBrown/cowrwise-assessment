import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine

# Fixture for the FastAPI test client
@pytest.fixture
def client():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    # Drop the database tables after the test
    Base.metadata.drop_all(bind=engine)

def test_create_user(client):
    response = client.post(
        "/users",
        json={"email": "test@example.com", "first_name": "John", "last_name": "Doe"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_get_users(client):
    # Create a user first
    client.post(
        "/users",
        json={"email": "test@example.com", "first_name": "John", "last_name": "Doe"},
    )
    # Get all users
    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) == 1