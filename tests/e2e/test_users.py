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