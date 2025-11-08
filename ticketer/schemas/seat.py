"""Seat schemas."""

from pydantic import BaseModel


class SeatCreate(BaseModel):
    """Schema for creating a seat."""

    event_id: int
    seat_label: str
    row: str
    col: int


class SeatResponse(BaseModel):
    """Schema for seat response."""

    id: int
    event_id: int
    seat_label: str
    row: str
    col: int
    is_reserved: bool

    model_config = {"from_attributes": True}

