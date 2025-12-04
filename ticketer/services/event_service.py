"""Event service with business logic."""

from datetime import datetime, timezone

from ticketer.models.event import Event
from ticketer.repositories.event_repository import EventRepository
from ticketer.repositories.seat_repository import SeatRepository


def choose_best_seat(seat_repo: SeatRepository, event_id: int) -> dict | None:
    """
    Choose the best available seat for an event.

    This is a pure business logic function that can be unit tested.
    Prefers seats in front rows (lower row letters).

    Args:
        seat_repo: Seat repository
        event_id: ID of the event

    Returns:
        Dictionary with seat info or None if no seats available
    """
    available_seats = seat_repo.get_available_seats(event_id)
    if not available_seats:
        return None

    # Convert seats to dict format and score them
    seats_with_scores = []
    for seat in available_seats:
        # Score based on row (A=10, B=9, etc.) and prefer center columns
        row_score = ord("Z") - ord(seat.row[0]) + 1
        seats_with_scores.append(
            {"id": seat.id, "row": seat.row, "col": seat.col, "score": row_score}
        )

    # Sort by score (descending) and return the best
    seats_with_scores.sort(key=lambda x: x["score"], reverse=True)
    return seats_with_scores[0]


class EventService:
    """Service for event-related business logic."""

    def __init__(self, event_repo: EventRepository):
        self.event_repo = event_repo

    def create_event(self, venue_id: int, name: str, start_at: datetime, capacity: int) -> Event:
        """Create a new event."""
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        if start_at <= datetime.now(timezone.utc):
            raise ValueError("Event must be in the future")

        return self.event_repo.create(
            venue_id=venue_id, name=name, start_at=start_at, capacity=capacity
        )

    def check_availability(self, event_id: int, requested_quantity: int) -> bool:
        """
        Check if event has enough available capacity.

        This is important business logic for preventing overbooking.
        """
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found")

        if not event.sales_open:
            return False

        reserved_count = self.event_repo.get_reserved_count(event_id)
        available = event.capacity - reserved_count

        return available >= requested_quantity

    def open_sales(self, event_id: int) -> Event:
        """Open sales for an event."""
        result = self.event_repo.update_sales_status(event_id, True)
        if not result:
            raise ValueError("Event not found")
        return result

    def close_sales(self, event_id: int) -> Event:
        """Close sales for an event."""
        result = self.event_repo.update_sales_status(event_id, False)
        if not result:
            raise ValueError("Event not found")
        return result
