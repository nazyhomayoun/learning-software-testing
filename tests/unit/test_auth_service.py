"""Unit tests for authentication service."""

from unittest.mock import MagicMock

import pytest

from ticketer.models.user import User
from ticketer.services.auth_service import AuthService


def test_hash_password():
    """Test password hashing."""
    mock_repo = MagicMock()
    auth_service = AuthService(mock_repo)

    password = "mysecretpassword"
    hashed = auth_service.hash_password(password)

    assert hashed != password
    assert len(hashed) > 20


def test_verify_password_correct():
    """Test password verification with correct password."""
    mock_repo = MagicMock()
    auth_service = AuthService(mock_repo)

    password = "mysecretpassword"
    hashed = auth_service.hash_password(password)

    assert auth_service.verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test password verification with incorrect password."""
    mock_repo = MagicMock()
    auth_service = AuthService(mock_repo)

    password = "mysecretpassword"
    hashed = auth_service.hash_password(password)

    assert auth_service.verify_password("wrongpassword", hashed) is False


def test_register_user_success():
    """Test successful user registration."""
    mock_repo = MagicMock()
    mock_user = User(id=1, email="test@example.com", hashed_password="hashed")
    mock_repo.get_by_email.return_value = None
    mock_repo.create.return_value = mock_user

    auth_service = AuthService(mock_repo)
    user = auth_service.register_user("test@example.com", "password123")

    assert user == mock_user
    mock_repo.get_by_email.assert_called_once_with("test@example.com")
    mock_repo.create.assert_called_once()


def test_register_user_already_exists():
    """Test registration fails when user already exists."""
    mock_repo = MagicMock()
    existing_user = User(id=1, email="test@example.com", hashed_password="hashed")
    mock_repo.get_by_email.return_value = existing_user

    auth_service = AuthService(mock_repo)

    with pytest.raises(ValueError, match="already exists"):
        auth_service.register_user("test@example.com", "password123")


def test_authenticate_user_success():
    """Test successful authentication."""
    mock_repo = MagicMock()
    hashed_pwd = "$2b$12$MN93TgNXE3T2EZv8ExXz3OOx/5CHGuuo1TUZecXILK0uM8kbm6JUu"  # Mock bcrypt hash
    mock_user = User(id=1, email="test@example.com", hashed_password=hashed_pwd)
    mock_repo.get_by_email.return_value = mock_user

    auth_service = AuthService(mock_repo)

    # Hash the actual password we'll test with
    correct_password = "password123"
    mock_user.hashed_password = auth_service.hash_password(correct_password)

    user = auth_service.authenticate_user("test@example.com", correct_password)

    assert user == mock_user


def test_authenticate_user_wrong_email():
    """Test authentication fails with wrong email."""
    mock_repo = MagicMock()
    mock_repo.get_by_email.return_value = None

    auth_service = AuthService(mock_repo)
    user = auth_service.authenticate_user("wrong@example.com", "password123")

    assert user is None


def test_create_access_token():
    """Test JWT token creation."""
    mock_repo = MagicMock()
    auth_service = AuthService(mock_repo)

    token = auth_service.create_access_token(user_id=1)

    assert isinstance(token, str)
    assert len(token) > 20
