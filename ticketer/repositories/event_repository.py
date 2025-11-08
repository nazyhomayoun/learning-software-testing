"""Event repository."""

from datetime import datetime
from typing import Protocol

from sqlalchemy.orm import Session

from ticketer.models.event import Event


class EventRepository(Protocol):
    """Interface for event repository."""

    def create(
        self, venue_id: int, name: str, start_at: datetime, capacity: int, sales_open: bool = True
    ) -> Event:
        """Create a new event."""
        ...

    def get_by_id(self, event_id: int) -> Event | None:
        """Get event by ID."""
        ...

    def list_all(self, sales_open_only: bool = False) -> list[Event]:
        """List all events."""
        ...

    def update_sales_status(self, event_id: int, sales_open: bool) -> Event | None:
        """Update event sales status."""
        ...

    def get_reserved_count(self, event_id: int) -> int:
        """Get count of reserved tickets for an event."""
        ...


class SQLAlchemyEventRepository:
    """SQLAlchemy implementation of event repository."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self, venue_id: int, name: str, start_at: datetime, capacity: int, sales_open: bool = True
    ) -> Event:
        """Create a new event."""
        event = Event(
            venue_id=venue_id, name=name, start_at=start_at, capacity=capacity, sales_open=sales_open
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_by_id(self, event_id: int) -> Event | None:
        """Get event by ID."""
        return self.db.query(Event).filter(Event.id == event_id).first()

    def list_all(self, sales_open_only: bool = False) -> list[Event]:
        """List all events."""
        query = self.db.query(Event)
        if sales_open_only:
            query = query.filter(Event.sales_open == True)  # noqa: E712
        return list(query.all())

    def update_sales_status(self, event_id: int, sales_open: bool) -> Event | None:
        """Update event sales status."""
        event = self.get_by_id(event_id)
        if event:
            event.sales_open = sales_open
            self.db.commit()
            self.db.refresh(event)
        return event

    def get_reserved_count(self, event_id: int) -> int:
        """Get count of reserved tickets for an event."""
        from ticketer.models.order import Order, OrderItem, OrderStatus

        # Count confirmed order items for this event
        count = (
            self.db.query(OrderItem)
            .join(Order)
            .filter(
                OrderItem.event_id == event_id,
                Order.status.in_([OrderStatus.HELD, OrderStatus.CONFIRMED]),
            )
            .count()
        )
        return count

