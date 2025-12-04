"""API tests for user endpoints."""

from fastapi import status


def test_register_user(client):
    """Test user registration via API."""
    response = client.post(
        "/api/v1/users/register",
        json={"email": "newuser@example.com", "password": "password123"},
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "hashed_password" not in data  # Should not expose password


def test_register_duplicate_user(client, create_user):
    """Test that registering with existing email fails."""
    create_user(email="existing@example.com")
    
    response = client.post(
        "/api/v1/users/register",
        json={"email": "existing@example.com", "password": "password123"},
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]


def test_login_user(client, create_user):
    """Test user login via API."""
    create_user(email="login@example.com", password="password123")
    
    response = client.post(
        "/api/v1/users/login",
        json={"email": "login@example.com", "password": "password123"},
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, create_user):
    """Test login fails with wrong password."""
    create_user(email="user@example.com", password="correctpassword")
    
    response = client.post(
        "/api/v1/users/login",
        json={"email": "user@example.com", "password": "wrongpassword"},
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    """Test login fails for non-existent user."""
    response = client.post(
        "/api/v1/users/login",
        json={"email": "nobody@example.com", "password": "password123"},
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

