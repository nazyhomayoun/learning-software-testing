"""Venue repository."""

from typing import Protocol

from sqlalchemy.orm import Session

from ticketer.models.venue import Venue


class VenueRepository(Protocol):
    """Interface for venue repository."""

    def create(self, name: str, address: str) -> Venue:
        """Create a new venue."""
        ...

    def get_by_id(self, venue_id: int) -> Venue | None:
        """Get venue by ID."""
        ...

    def list_all(self) -> list[Venue]:
        """List all venues."""
        ...


class SQLAlchemyVenueRepository:
    """SQLAlchemy implementation of venue repository."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, address: str) -> Venue:
        """Create a new venue."""
        venue = Venue(name=name, address=address)
        self.db.add(venue)
        self.db.commit()
        self.db.refresh(venue)
        return venue

    def get_by_id(self, venue_id: int) -> Venue | None:
        """Get venue by ID."""
        return self.db.query(Venue).filter(Venue.id == venue_id).first()

    def list_all(self) -> list[Venue]:
        """List all venues."""
        return list(self.db.query(Venue).all())

