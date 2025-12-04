"""Order repository."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Protocol

from sqlalchemy.orm import Session

from ticketer.models.order import Order, OrderItem, OrderStatus


class OrderRepository(Protocol):
    """Interface for order repository."""

    def create(self, user_id: int) -> Order:
        """Create a new order."""
        ...

    def get_by_id(self, order_id: int) -> Order | None:
        """Get order by ID."""
        ...

    def add_item(
        self,
        order_id: int,
        event_id: int,
        price: Decimal,
        ticket_type: str = "GENERAL",
        seat_id: int | None = None,
    ) -> OrderItem:
        """Add an item to an order."""
        ...

    def update_status(self, order_id: int, status: OrderStatus) -> Order | None:
        """Update order status."""
        ...

    def set_expiration(self, order_id: int, expires_at: datetime) -> None:
        """Set order expiration time."""
        ...

    def get_expired_orders(self) -> list[Order]:
        """Get all expired orders that are still held."""
        ...

    def calculate_total(self, order_id: int) -> Decimal:
        """Calculate total price for an order."""
        ...


class SQLAlchemyOrderRepository:
    """SQLAlchemy implementation of order repository."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int) -> Order:
        """Create a new order."""
        order = Order(user_id=user_id, status=OrderStatus.DRAFT, total_price=Decimal("0"))
        self.db.add(order)
        self.db.flush()  # Flush to get ID without committing
        return order

    def get_by_id(self, order_id: int) -> Order | None:
        """Get order by ID."""
        return self.db.query(Order).filter(Order.id == order_id).first()

    def add_item(
        self,
        order_id: int,
        event_id: int,
        price: Decimal,
        ticket_type: str = "GENERAL",
        seat_id: int | None = None,
    ) -> OrderItem:
        """Add an item to an order."""
        item = OrderItem(
            order_id=order_id,
            event_id=event_id,
            price=price,
            ticket_type=ticket_type,
            seat_id=seat_id,
        )
        self.db.add(item)
        self.db.flush()  # Flush to get ID without committing
        return item

    def update_status(self, order_id: int, status: OrderStatus) -> Order | None:
        """Update order status."""
        order = self.get_by_id(order_id)
        if order:
            order.status = status
            self.db.flush()  # Flush without committing
        return order

    def set_expiration(self, order_id: int, expires_at: datetime) -> None:
        """Set order expiration time."""
        order = self.get_by_id(order_id)
        if order:
            order.expires_at = expires_at
            self.db.flush()  # Flush without committing

    def get_expired_orders(self) -> list[Order]:
        """Get all expired orders that are still held."""
        now = datetime.now(timezone.utc)
        return list(
            self.db.query(Order)
            .filter(
                Order.status == OrderStatus.HELD,
                Order.expires_at <= now,
            )
            .all()
        )

    def calculate_total(self, order_id: int) -> Decimal:
        """Calculate total price for an order."""
        order = self.get_by_id(order_id)
        if not order:
            return Decimal("0")

        total = sum(item.price for item in order.items)
        order.total_price = total
        self.db.flush()  # Flush without committing
        return total
