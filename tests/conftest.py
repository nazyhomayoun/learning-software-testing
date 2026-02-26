"""Pytest configuration and fixtures."""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from alembic.config import Config
from alembic import command

from ticketer.api.v1 import deps
from ticketer.db.base import Base
from ticketer.main import app
from ticketer.services.email_service import FakeEmailService
from ticketer.services.payment_gateway import FakePaymentGateway

# -----------------------------
# Test database URL
# -----------------------------
DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/ticketing_test",
)

# -----------------------------
# Fixtures
# -----------------------------

@pytest.fixture(scope="session")
def engine():
    """Create a test database engine for the entire test session and run Alembic migrations."""
    engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=10)

    # Run Alembic migrations on test database
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.upgrade(alembic_cfg, "head")

    yield engine

    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """
    Create a new database session for a test with rollback.

    This provides transactional test isolation:
    - Each test gets a fresh transaction
    - Changes are rolled back after the test
    - Tests don't interfere with each other
    """
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def fake_payment_gateway():
    """Provide a fake payment gateway for testing."""
    return FakePaymentGateway()


@pytest.fixture
def fake_email_service():
    """Provide a fake email service for testing."""
    service = FakeEmailService()
    yield service
    service.clear()


@pytest.fixture
def client(db_session: Session, fake_payment_gateway, fake_email_service):
    """
    Provide a test client with overridden dependencies.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_order_service():
        from ticketer.repositories.event_repository import SQLAlchemyEventRepository
        from ticketer.repositories.order_repository import SQLAlchemyOrderRepository
        from ticketer.repositories.seat_repository import SQLAlchemySeatRepository
        from ticketer.services.order_service import OrderService

        return OrderService(
            order_repo=SQLAlchemyOrderRepository(db_session),
            event_repo=SQLAlchemyEventRepository(db_session),
            seat_repo=SQLAlchemySeatRepository(db_session),
            payment_gateway=fake_payment_gateway,
            email_service=fake_email_service,
        )

    # Override dependencies
    app.dependency_overrides[deps.get_db] = override_get_db
    app.dependency_overrides[deps.get_order_service] = override_get_order_service

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides after test
    app.dependency_overrides.clear()


# ======================================================================
# Factory Fixtures
# ======================================================================

@pytest.fixture
def create_user(db_session: Session):
    """Factory fixture for creating test users."""
    from ticketer.repositories.user_repository import SQLAlchemyUserRepository
    from ticketer.services.auth_service import AuthService

    def _create_user(email: str = "test@example.com", password: str = "12345678"):
        repo = SQLAlchemyUserRepository(db_session)
        auth_service = AuthService(repo)
        return auth_service.register_user(email, password)

    return _create_user


@pytest.fixture
def create_venue(db_session: Session):
    """Factory fixture for creating test venues."""
    from ticketer.models.venue import Venue

    def _create_venue(name: str = "Test Venue", address: str = "123 Test St"):
        venue = Venue(name=name, address=address)
        db_session.add(venue)
        db_session.commit()
        db_session.refresh(venue)
        return venue

    return _create_venue


@pytest.fixture
def create_event(db_session: Session, create_venue):
    """Factory fixture for creating test events."""
    from datetime import datetime, timedelta, timezone
    from ticketer.models.event import Event

    def _create_event(
        name: str = "Test Event",
        capacity: int = 100,
        sales_open: bool = True,
        venue=None,
    ):
        if venue is None:
            venue = create_venue()

        event = Event(
            venue_id=venue.id,
            name=name,
            start_at=datetime.now(timezone.utc) + timedelta(days=30),
            capacity=capacity,
            sales_open=sales_open,
        )
        db_session.add(event)
        db_session.commit()
        db_session.refresh(event)
        return event

    return _create_event


@pytest.fixture
def create_seat(db_session: Session):
    """Factory fixture for creating test seats."""
    from ticketer.models.seat import Seat

    def _create_seat(event_id: int, seat_label: str, row: str, col: int):
        seat = Seat(event_id=event_id, seat_label=seat_label, row=row, col=col)
        db_session.add(seat)
        db_session.commit()
        db_session.refresh(seat)
        return seat

    return _create_seat
