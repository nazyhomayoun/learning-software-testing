#!/usr/bin/env python3
"""
Script to set up the test database with sample data.

This is useful for manual testing and exploration.
Run with: poetry run python scripts/setup_test_db.py
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ticketer.db.base import Base
from ticketer.models import Event, Seat, Venue
from ticketer.repositories.user_repository import SQLAlchemyUserRepository
from ticketer.services.auth_service import AuthService

DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/ticketing_test"


def setup_sample_data():
    """Create sample data for testing."""
    print("Setting up sample data...")

    # Create engine and session
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create users
        print("Creating users...")
        user_repo = SQLAlchemyUserRepository(session)
        auth_service = AuthService(user_repo)

        user1 = auth_service.register_user("alice@example.com", "password123")
        user2 = auth_service.register_user("bob@example.com", "password123")
        print(f"✓ Created users: {user1.email}, {user2.email}")

        # Create venues
        print("Creating venues...")
        venue1 = Venue(
            name="Madison Square Garden", address="4 Pennsylvania Plaza, New York, NY 10001"
        )
        venue2 = Venue(name="Hollywood Bowl", address="2301 Highland Ave, Los Angeles, CA 90068")
        session.add_all([venue1, venue2])
        session.commit()
        print(f"✓ Created venues: {venue1.name}, {venue2.name}")

        # Create events
        print("Creating events...")
        event1 = Event(
            venue_id=venue1.id,
            name="Rock Concert 2024",
            start_at=datetime.now(timezone.utc) + timedelta(days=30),
            capacity=100,
            sales_open=True,
        )
        event2 = Event(
            venue_id=venue2.id,
            name="Jazz Festival",
            start_at=datetime.now(timezone.utc) + timedelta(days=45),
            capacity=200,
            sales_open=True,
        )
        event3 = Event(
            venue_id=venue1.id,
            name="Comedy Night",
            start_at=datetime.now(timezone.utc) + timedelta(days=15),
            capacity=50,
            sales_open=False,  # Sales closed
        )
        session.add_all([event1, event2, event3])
        session.commit()
        print(f"✓ Created events: {event1.name}, {event2.name}, {event3.name}")

        # Create seats for Rock Concert
        print("Creating seats...")
        seats = []
        for row in ["A", "B", "C", "D"]:
            for col in range(1, 11):  # 10 seats per row
                seat_label = f"{row}{col}"
                seat = Seat(
                    event_id=event1.id,
                    seat_label=seat_label,
                    row=row,
                    col=col,
                )
                seats.append(seat)

        session.add_all(seats)
        session.commit()
        print(f"✓ Created {len(seats)} seats for {event1.name}")

        print("\n" + "=" * 50)
        print("Sample data setup complete! 🎉")
        print("=" * 50)
        print("\nYou can now:")
        print("1. Start the app: poetry run uvicorn ticketer.main:app --reload")
        print("2. Visit API docs: http://localhost:8000/docs")
        print("3. Login with: alice@example.com / password123")
        print("\nSample events:")
        print(f"  - {event1.name} (ID: {event1.id}) - {event1.capacity} capacity, sales OPEN")
        print(f"  - {event2.name} (ID: {event2.id}) - {event2.capacity} capacity, sales OPEN")
        print(f"  - {event3.name} (ID: {event3.id}) - {event3.capacity} capacity, sales CLOSED")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    setup_sample_data()
