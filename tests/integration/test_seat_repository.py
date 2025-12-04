"""Integration tests for seat repository."""

from ticketer.repositories.seat_repository import SQLAlchemySeatRepository


def test_create_seat(db_session, create_event):
    """Test creating a seat in the database."""
    event = create_event()
    repo = SQLAlchemySeatRepository(db_session)
    
    seat = repo.create(
        event_id=event.id,
        seat_label="A1",
        row="A",
        col=1,
    )
    
    assert seat.id is not None
    assert seat.event_id == event.id
    assert seat.seat_label == "A1"
    assert seat.is_reserved is False


def test_get_available_seats(db_session, create_event):
    """Test getting available seats for an event."""
    event = create_event()
    repo = SQLAlchemySeatRepository(db_session)
    
    # Create seats
    seat1 = repo.create(event.id, "A1", "A", 1)
    seat2 = repo.create(event.id, "A2", "A", 2)
    seat3 = repo.create(event.id, "B1", "B", 1)
    
    # Reserve one seat
    repo.reserve_seat(seat2.id)
    
    available = repo.get_available_seats(event.id)
    
    assert len(available) == 2
    assert seat1.id in [s.id for s in available]
    assert seat3.id in [s.id for s in available]
    assert seat2.id not in [s.id for s in available]


def test_reserve_seat_success(db_session, create_event):
    """Test successfully reserving a seat."""
    event = create_event()
    repo = SQLAlchemySeatRepository(db_session)
    
    seat = repo.create(event.id, "A1", "A", 1)
    
    success = repo.reserve_seat(seat.id)
    
    assert success is True
    
    # Verify seat is reserved
    db_session.refresh(seat)
    assert seat.is_reserved is True


def test_reserve_seat_already_reserved(db_session, create_event):
    """Test reserving an already reserved seat fails."""
    event = create_event()
    repo = SQLAlchemySeatRepository(db_session)
    
    seat = repo.create(event.id, "A1", "A", 1)
    
    # Reserve once
    success1 = repo.reserve_seat(seat.id)
    assert success1 is True
    
    # Try to reserve again
    success2 = repo.reserve_seat(seat.id)
    assert success2 is False


def test_release_seat(db_session, create_event):
    """Test releasing a reserved seat."""
    event = create_event()
    repo = SQLAlchemySeatRepository(db_session)
    
    seat = repo.create(event.id, "A1", "A", 1)
    repo.reserve_seat(seat.id)
    
    repo.release_seat(seat.id)
    
    db_session.refresh(seat)
    assert seat.is_reserved is False


def test_seats_ordered_by_row_and_col(db_session, create_event):
    """Test that available seats are ordered by row and column."""
    event = create_event()
    repo = SQLAlchemySeatRepository(db_session)
    
    # Create seats in random order
    repo.create(event.id, "C3", "C", 3)
    repo.create(event.id, "A1", "A", 1)
    repo.create(event.id, "B2", "B", 2)
    
    available = repo.get_available_seats(event.id)
    
    assert len(available) == 3
    assert available[0].seat_label == "A1"
    assert available[1].seat_label == "B2"
    assert available[2].seat_label == "C3"

