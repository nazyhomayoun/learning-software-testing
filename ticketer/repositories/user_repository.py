"""User repository."""

from typing import Protocol

from sqlalchemy.orm import Session

from ticketer.models.user import User


class UserRepository(Protocol):
    """Interface for user repository."""

    def create(self, email: str, hashed_password: str) -> User:
        """Create a new user."""
        ...

    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        ...

    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        ...


class SQLAlchemyUserRepository:
    """SQLAlchemy implementation of user repository."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, hashed_password: str) -> User:
        """Create a new user."""
        user = User(email=email, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

