"""Order schemas."""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel

from ticketer.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    """Schema for creating an order item."""

    event_id: int
    quantity: int = 1
    ticket_type: str = "GENERAL"
    seat_id: int | None = None


class OrderItemResponse(BaseModel):
    """Schema for order item response."""

    id: int
    order_id: int
    event_id: int
    seat_id: int | None
    ticket_type: str
    price: Decimal

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    """Schema for creating an order."""

    user_id: int
    items: list[OrderItemCreate]


class OrderResponse(BaseModel):
    """Schema for order response."""

    id: int
    user_id: int
    status: OrderStatus
    total_price: Decimal
    created_at: datetime
    expires_at: datetime | None
    items: list[OrderItemResponse]

    model_config = {"from_attributes": True}


class OrderConfirm(BaseModel):
    """Schema for confirming an order."""

    payment_token: str

