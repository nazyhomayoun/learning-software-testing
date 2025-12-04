"""Authentication service."""

import hashlib
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from ticketer.core.config import settings
from ticketer.models.user import User
from ticketer.repositories.user_repository import UserRepository


class AuthService:
    """Service for user authentication."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def _prehash_password(self, password: str) -> bytes:
        """
        Pre-hash with SHA-256 to handle long passwords and ensure consistent length
        hexdigest() returns a string of 64 hex characters
        """
        return hashlib.sha256(password.encode()).hexdigest().encode()

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt with SHA-256 pre-hashing."""
        # Pre-hash password
        pwd_hash = self._prehash_password(password)

        # Hash with bcrypt
        # bcrypt.hashpw returns bytes, so we decode to str for storage
        return bcrypt.hashpw(pwd_hash, bcrypt.gensalt()).decode()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        # Pre-hash the input password
        pwd_hash = self._prehash_password(plain_password)

        # Verify with bcrypt
        # hashed_password needs to be encoded to bytes for bcrypt.checkpw
        try:
            return bcrypt.checkpw(pwd_hash, hashed_password.encode())
        except ValueError:
            # Handle cases where hashed_password might be invalid or from a different scheme
            return False

    def create_access_token(self, user_id: int) -> str:
        """Create a JWT access token."""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {"sub": str(user_id), "exp": expire}
        # Use get_secret_value() to handle SecretStr
        secret = settings.SECRET_KEY.get_secret_value()
        encoded_jwt = jwt.encode(to_encode, secret, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def register_user(self, email: str, password: str) -> User:
        """Register a new user."""
        # Check if user already exists
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")

        hashed_password = self.hash_password(password)
        return self.user_repo.create(email=email, hashed_password=hashed_password)

    def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate a user."""
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
