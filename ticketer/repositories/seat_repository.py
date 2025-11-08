"""Seat repository."""

from typing import Protocol

from sqlalchemy.orm import Session

from ticketer.models.seat import Seat


class SeatRepository(Protocol):
    """Interface for seat repository."""

    def create(self, event_id: int, seat_label: str, row: str, col: int) -> Seat:
        """Create a new seat."""
        ...

    def get_by_id(self, seat_id: int) -> Seat | None:
        """Get seat by ID."""
        ...

    def get_available_seats(self, event_id: int) -> list[Seat]:
        """Get all available (unreserved) seats for an event."""
        ...

    def reserve_seat(self, seat_id: int) -> bool:
        """Reserve a seat. Returns True if successful, False if already reserved."""
        ...

    def release_seat(self, seat_id: int) -> None:
        """Release a reserved seat."""
        ...


class SQLAlchemySeatRepository:
    """SQLAlchemy implementation of seat repository."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, event_id: int, seat_label: str, row: str, col: int) -> Seat:
        """Create a new seat."""
        seat = Seat(event_id=event_id, seat_label=seat_label, row=row, col=col)
        self.db.add(seat)
        self.db.commit()
        self.db.refresh(seat)
        return seat

    def get_by_id(self, seat_id: int) -> Seat | None:
        """Get seat by ID."""
        return self.db.query(Seat).filter(Seat.id == seat_id).first()

    def get_available_seats(self, event_id: int) -> list[Seat]:
        """Get all available (unreserved) seats for an event."""
        return list(
            self.db.query(Seat)
            .filter(Seat.event_id == event_id, Seat.is_reserved == False)  # noqa: E712
            .order_by(Seat.row, Seat.col)
            .all()
        )

    def reserve_seat(self, seat_id: int) -> bool:
        """Reserve a seat. Returns True if successful, False if already reserved."""
        seat = self.get_by_id(seat_id)
        if not seat or seat.is_reserved:
            return False
        seat.is_reserved = True
        self.db.commit()
        return True

    def release_seat(self, seat_id: int) -> None:
        """Release a reserved seat."""
        seat = self.get_by_id(seat_id)
        if seat:
            seat.is_reserved = False
            self.db.commit()

