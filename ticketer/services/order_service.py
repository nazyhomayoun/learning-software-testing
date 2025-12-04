"""Order service with business logic."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from ticketer.core.config import settings
from ticketer.models.order import Order, OrderStatus
from ticketer.models.payment import Payment, PaymentStatus
from ticketer.repositories.event_repository import EventRepository
from ticketer.repositories.order_repository import OrderRepository
from ticketer.repositories.seat_repository import SeatRepository
from ticketer.services.email_service import EmailService
from ticketer.services.payment_gateway import PaymentGateway


def calculate_price_with_fees(base_price: Decimal, quantity: int) -> Decimal:
    """
    Calculate total price including fees.

    Pure business logic function - easy to unit test.
    Adds 10% service fee.
    """
    subtotal = base_price * quantity
    fee = subtotal * Decimal("0.1")
    return subtotal + fee


class OrderService:
    """Service for order-related business logic."""

    def __init__(
        self,
        order_repo: OrderRepository,
        event_repo: EventRepository,
        seat_repo: SeatRepository | None = None,
        payment_gateway: PaymentGateway | None = None,
        email_service: EmailService | None = None,
    ):
        self.order_repo = order_repo
        self.event_repo = event_repo
        self.seat_repo = seat_repo
        self.payment_gateway = payment_gateway
        self.email_service = email_service

    def create_order_with_hold(self, user_id: int, items: list[dict]) -> Order:
        """
        Create an order and place a temporary hold.

        Args:
            user_id: ID of the user placing the order
            items: List of dicts with 'event_id', 'quantity', 'ticket_type', optional 'seat_id'

        Returns:
            Created order with HELD status

        Raises:
            ValueError: If insufficient capacity or sales closed
        """
        # Create order
        order = self.order_repo.create(user_id)

        # Process each item
        for item_data in items:
            event_id = item_data["event_id"]
            quantity = item_data.get("quantity", 1)
            ticket_type = item_data.get("ticket_type", "GENERAL")
            seat_id = item_data.get("seat_id")

            # Check event exists and sales are open
            # Lock the event to prevent overbooking race conditions
            event = self.event_repo.get_by_id_with_lock(event_id)
            if not event:
                raise ValueError(f"Event {event_id} not found")
            if not event.sales_open:
                raise ValueError(f"Sales are closed for event {event_id}")

            # Check capacity
            reserved_count = self.event_repo.get_reserved_count(event_id)
            available = event.capacity - reserved_count
            if available < quantity:
                raise ValueError(f"Insufficient capacity for event {event_id}")

            # Calculate price (simplified - $50 base price)
            base_price = Decimal("50.00")
            if ticket_type == "VIP":
                base_price = Decimal("100.00")
            total_price = calculate_price_with_fees(base_price, quantity)

            # Add items to order
            for _ in range(quantity):
                self.order_repo.add_item(
                    order_id=order.id,
                    event_id=event_id,
                    price=total_price / quantity,
                    ticket_type=ticket_type,
                    seat_id=seat_id,
                )

                # Reserve seat if specified
                if seat_id and self.seat_repo:
                    if not self.seat_repo.reserve_seat(seat_id):
                        raise ValueError(f"Seat {seat_id} is not available")

        # Calculate total and set hold
        total = self.order_repo.calculate_total(order.id)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.HOLD_EXPIRATION_MINUTES
        )

        self.order_repo.update_status(order.id, OrderStatus.HELD)
        self.order_repo.set_expiration(order.id, expires_at)

        # Commit the entire order creation as one atomic transaction
        self.order_repo.db.commit()

        # Refresh order to get updated data
        order = self.order_repo.get_by_id(order.id)
        if not order:
            raise ValueError("Order not found after creation")

        return order

    def confirm_order(self, order_id: int, payment_token: str, db_session) -> Order:
        """
        Confirm an order by processing payment.

        Args:
            order_id: ID of the order to confirm
            payment_token: Payment token from client
            db_session: Database session for payment record

        Returns:
            Confirmed order

        Raises:
            ValueError: If order not found, expired, or payment fails
        """
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        if order.status != OrderStatus.HELD:
            raise ValueError(f"Order is not in HELD status (current: {order.status})")

        # Check if expired
        if order.expires_at and order.expires_at < datetime.now(timezone.utc):
            self.order_repo.update_status(order_id, OrderStatus.CANCELLED)
            raise ValueError("Order has expired")

        # Process payment
        if self.payment_gateway:
            result = self.payment_gateway.process_payment(order.total_price, payment_token)

            # Record payment
            payment = Payment(
                order_id=order_id,
                status=PaymentStatus.SUCCESS if result.success else PaymentStatus.FAILED,
                gateway_ref=result.transaction_id,
            )
            db_session.add(payment)
            db_session.commit()

            if not result.success:
                raise ValueError(f"Payment failed: {result.error_message}")

        # Confirm order
        order = self.order_repo.update_status(order_id, OrderStatus.CONFIRMED)
        if not order:
            raise ValueError("Failed to update order status")

        # Send confirmation email
        if self.email_service:
            # Would need to get user email, simplified here
            self.email_service.send_confirmation_email(
                f"user_{order.user_id}@example.com", order_id
            )

        return order

    def cancel_order(self, order_id: int) -> Order:
        """Cancel an order and release any reserved seats."""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        if order.status == OrderStatus.CONFIRMED:
            raise ValueError("Cannot cancel confirmed order (use refund instead)")

        # Release seats
        if self.seat_repo:
            for item in order.items:
                if item.seat_id:
                    self.seat_repo.release_seat(item.seat_id)

        # Cancel order
        result = self.order_repo.update_status(order_id, OrderStatus.CANCELLED)
        if not result:
            raise ValueError("Failed to cancel order")

        return result

    def release_expired_holds(self) -> int:
        """
        Release all expired order holds.

        This would typically run as a background job.

        Returns:
            Number of orders released
        """
        expired_orders = self.order_repo.get_expired_orders()
        count = 0

        for order in expired_orders:
            try:
                self.cancel_order(order.id)
                count += 1
            except ValueError:
                # Log error in production
                pass

        return count
