import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ticketer.db.session import SessionLocal
from ticketer.repositories.user_repository import SQLAlchemyUserRepository



@pytest.fixture
def user_repository(db_session: Session):
    return SQLAlchemyUserRepository(db_session)


def test_create_user(user_repository):
    user = user_repository.create(
        email="testuser@example.com",
        hashed_password="hashed-password",
    )

    assert user.id is not None
    assert user.email == "testuser@example.com"


def test_retrieve_user_by_email(user_repository):
    user_repository.create(
        email="findme@example.com",
        hashed_password="hashed-password",
    )

    user = user_repository.get_by_email("findme@example.com")

    assert user is not None
    assert user.email == "findme@example.com"


def test_duplicate_user_email_not_allowed(user_repository):
    user_repository.create(
        email="duplicate@example.com",
        hashed_password="hashed-password",
    )

    with pytest.raises(IntegrityError):
        user_repository.create(
            email="duplicate@example.com",
            hashed_password="hashed-password",
        )
