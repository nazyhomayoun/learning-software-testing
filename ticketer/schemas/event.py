"""Event schemas."""

from datetime import datetime
from pydantic import BaseModel


class EventCreate(BaseModel):
    """Schema for creating an event."""

    venue_id: int
    name: str
    start_at: datetime
    capacity: int
    sales_open: bool = True


class EventUpdate(BaseModel):
    """Schema for updating an event."""

    name: str | None = None
    start_at: datetime | None = None
    capacity: int | None = None
    sales_open: bool | None = None


class EventResponse(BaseModel):
    """Schema for event response."""

    id: int
    venue_id: int
    name: str
    start_at: datetime
    capacity: int
    sales_open: bool
    created_at: datetime

    model_config = {"from_attributes": True}

