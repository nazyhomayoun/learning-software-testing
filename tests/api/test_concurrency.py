"""Concurrency tests to demonstrate race conditions."""

import concurrent.futures

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ticketer.api.v1 import deps
from ticketer.main import app


@pytest.fixture
def concurrent_client(engine, fake_payment_gateway, fake_email_service):
    """
    Client for concurrency tests that uses fresh sessions per request.

    This is necessary because the standard client fixture uses a single
    transactional session that is not thread-safe and rolls back changes,
    making them invisible to other threads.
    """

    def override_get_db():
        # Create a new session for each request
        with Session(engine) as session:
            yield session

    # Override dependencies
    app.dependency_overrides[deps.get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides
    app.dependency_overrides.clear()

    # Cleanup: delete all data created during concurrent tests
    from sqlalchemy import text

    with Session(engine) as session:
        session.execute(
            text(
                "TRUNCATE TABLE order_items, orders, seats, events, venues, users RESTART IDENTITY CASCADE"
            )
        )
        session.commit()


def test_concurrent_booking_no_overbooking(concurrent_client, engine):
    """
    Test that concurrent booking requests don't result in overbooking.
    """
    # Setup data using a dedicated session that commits
    from datetime import datetime, timedelta, timezone

    from ticketer.models.event import Event
    from ticketer.models.venue import Venue
    from ticketer.repositories.user_repository import SQLAlchemyUserRepository
    from ticketer.services.auth_service import AuthService

    with Session(engine) as session:
        # Create venue
        venue = Venue(name="Concurrent Venue", address="123 Test St")
        session.add(venue)
        session.commit()

        # Create event
        event = Event(
            venue_id=venue.id,
            name="Concurrent Event",
            start_at=datetime.now(timezone.utc) + timedelta(days=30),
            capacity=5,
            sales_open=True,
        )
        session.add(event)
        session.commit()

        # Create user
        user_repo = SQLAlchemyUserRepository(session)
        auth_service = AuthService(user_repo)
        user = auth_service.register_user("concurrent@example.com", "12345678")

        event_id = event.id
        user_id = user.id

    def try_book():
        """Attempt to book a ticket."""
        response = concurrent_client.post(
            "/api/v1/orders/",
            json={
                "user_id": user_id,
                "items": [{"event_id": event_id, "quantity": 1}],
            },
        )
        return response

    # Launch 10 concurrent booking attempts for 5 available tickets
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(try_book) for _ in range(10)]
        responses = [f.result() for f in futures]

    # Count successful bookings
    successful = sum(1 for r in responses if r.status_code == status.HTTP_201_CREATED)
    failed = sum(1 for r in responses if r.status_code == status.HTTP_400_BAD_REQUEST)

    # Should have exactly 5 successful bookings (the capacity)
    assert successful == 5, f"Expected 5 successful bookings, got {successful}"
    assert failed == 5, f"Expected 5 failed bookings, got {failed}"

    # Verify capacity is not exceeded
    from ticketer.repositories.event_repository import SQLAlchemyEventRepository

    with Session(engine) as session:
        event_repo = SQLAlchemyEventRepository(session)
        reserved_count = event_repo.get_reserved_count(event_id)
        assert reserved_count == 5


def test_concurrent_seat_reservation(concurrent_client, engine):
    """
    Test that the same seat cannot be reserved by multiple concurrent requests.
    """
    from datetime import datetime, timedelta, timezone

    from ticketer.models.event import Event
    from ticketer.models.seat import Seat
    from ticketer.models.venue import Venue
    from ticketer.repositories.user_repository import SQLAlchemyUserRepository
    from ticketer.services.auth_service import AuthService

    with Session(engine) as session:
        venue = Venue(name="Seat Venue", address="123 Test St")
        session.add(venue)
        session.commit()

        event = Event(
            venue_id=venue.id,
            name="Seat Event",
            start_at=datetime.now(timezone.utc) + timedelta(days=30),
            capacity=10,
            sales_open=True,
        )
        session.add(event)
        session.commit()

        seat = Seat(event_id=event.id, seat_label="A1", row="A", col=1)
        session.add(seat)
        session.commit()

        user_repo = SQLAlchemyUserRepository(session)
        auth_service = AuthService(user_repo)
        user1 = auth_service.register_user("seat1@example.com", "12345678")
        user2 = auth_service.register_user("seat2@example.com", "12345678")

        event_id = event.id
        seat_id = seat.id
        user1_id = user1.id
        user2_id = user2.id

    def try_reserve_seat(user_id):
        """Attempt to reserve the specific seat."""
        response = concurrent_client.post(
            "/api/v1/orders/",
            json={
                "user_id": user_id,
                "items": [
                    {
                        "event_id": event_id,
                        "quantity": 1,
                        "seat_id": seat_id,
                    }
                ],
            },
        )
        return response

    # Two users try to book the same seat concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(try_reserve_seat, user1_id)
        future2 = executor.submit(try_reserve_seat, user2_id)

        response1 = future1.result()
        response2 = future2.result()

    responses = [response1, response2]
    successful = sum(1 for r in responses if r.status_code == status.HTTP_201_CREATED)
    failed = sum(1 for r in responses if r.status_code == status.HTTP_400_BAD_REQUEST)

    # Exactly one should succeed
    assert successful == 1, "Only one user should successfully reserve the seat"
    assert failed == 1, "One user should fail to reserve the seat"


def test_last_ticket_race_condition(concurrent_client, engine):
    """
    Test the classic 'last ticket' race condition.
    """
    from datetime import datetime, timedelta, timezone

    from ticketer.models.event import Event
    from ticketer.models.venue import Venue
    from ticketer.repositories.user_repository import SQLAlchemyUserRepository
    from ticketer.services.auth_service import AuthService

    with Session(engine) as session:
        venue = Venue(name="Race Venue", address="123 Test St")
        session.add(venue)
        session.commit()

        event = Event(
            venue_id=venue.id,
            name="Race Event",
            start_at=datetime.now(timezone.utc) + timedelta(days=30),
            capacity=1,  # Only 1 ticket
            sales_open=True,
        )
        session.add(event)
        session.commit()

        user_repo = SQLAlchemyUserRepository(session)
        auth_service = AuthService(user_repo)
        user1 = auth_service.register_user("race1@example.com", "12345678")
        user2 = auth_service.register_user("race2@example.com", "12345678")
        user3 = auth_service.register_user("race3@example.com", "12345678")

        event_id = event.id
        user1_id = user1.id
        user2_id = user2.id
        user3_id = user3.id

    def try_book(user_id):
        """Attempt to book the last ticket."""
        response = concurrent_client.post(
            "/api/v1/orders/",
            json={
                "user_id": user_id,
                "items": [{"event_id": event_id, "quantity": 1}],
            },
        )
        return response

    # Three users compete for 1 ticket
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(try_book, user1_id),
            executor.submit(try_book, user2_id),
            executor.submit(try_book, user3_id),
        ]
        responses = [f.result() for f in futures]

    successful = sum(1 for r in responses if r.status_code == status.HTTP_201_CREATED)
    failed = sum(1 for r in responses if r.status_code == status.HTTP_400_BAD_REQUEST)

    assert successful == 1, "Exactly one booking should succeed"
    assert failed == 2, "Two bookings should fail"


def test_rapid_fire_bookings(concurrent_client, engine):
    """
    Stress test: Many rapid booking attempts.
    """
    from datetime import datetime, timedelta, timezone

    from ticketer.models.event import Event
    from ticketer.models.venue import Venue
    from ticketer.repositories.user_repository import SQLAlchemyUserRepository
    from ticketer.services.auth_service import AuthService

    with Session(engine) as session:
        venue = Venue(name="Rapid Venue", address="123 Test St")
        session.add(venue)
        session.commit()

        event = Event(
            venue_id=venue.id,
            name="Rapid Event",
            start_at=datetime.now(timezone.utc) + timedelta(days=30),
            capacity=10,
            sales_open=True,
        )
        session.add(event)
        session.commit()

        user_repo = SQLAlchemyUserRepository(session)
        auth_service = AuthService(user_repo)

        users = []
        for i in range(20):
            user = auth_service.register_user(f"rapid{i}@example.com", "12345678")
            users.append(user.id)

        event_id = event.id

    def try_book(user_id):
        """Attempt to book a ticket."""
        return concurrent_client.post(
            "/api/v1/orders/",
            json={
                "user_id": user_id,
                "items": [{"event_id": event_id, "quantity": 1}],
            },
        )

    # 20 users try to book 10 tickets as fast as possible
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(try_book, user_id) for user_id in users]
        responses = [f.result() for f in futures]

    successful = sum(1 for r in responses if r.status_code == status.HTTP_201_CREATED)

    # Should not exceed capacity
    assert successful <= 10, f"Should not exceed capacity of 10, got {successful}"
    assert successful == 10, f"All 10 tickets should be sold, got {successful}"
