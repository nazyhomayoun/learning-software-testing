"""Integration tests for order repository."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from ticketer.models.order import OrderStatus
from ticketer.repositories.order_repository import SQLAlchemyOrderRepository


def test_create_order(db_session, create_user):
    """Test creating an order in the database."""
    user = create_user()
    repo = SQLAlchemyOrderRepository(db_session)
    
    order = repo.create(user_id=user.id)
    
    assert order.id is not None
    assert order.user_id == user.id
    assert order.status == OrderStatus.DRAFT
    assert order.total_price == Decimal("0")


def test_add_item_to_order(db_session, create_user, create_event):
    """Test adding items to an order."""
    user = create_user()
    event = create_event()
    repo = SQLAlchemyOrderRepository(db_session)
    
    order = repo.create(user_id=user.id)
    item = repo.add_item(
        order_id=order.id,
        event_id=event.id,
        price=Decimal("50.00"),
        ticket_type="GENERAL",
    )
    
    assert item.id is not None
    assert item.order_id == order.id
    assert item.event_id == event.id
    assert item.price == Decimal("50.00")


def test_update_order_status(db_session, create_user):
    """Test updating order status."""
    user = create_user()
    repo = SQLAlchemyOrderRepository(db_session)
    
    order = repo.create(user_id=user.id)
    updated = repo.update_status(order.id, OrderStatus.HELD)
    
    assert updated is not None
    assert updated.status == OrderStatus.HELD


def test_calculate_total(db_session, create_user, create_event):
    """Test calculating order total from items."""
    user = create_user()
    event = create_event()
    repo = SQLAlchemyOrderRepository(db_session)
    
    order = repo.create(user_id=user.id)
    repo.add_item(order.id, event.id, Decimal("50.00"))
    repo.add_item(order.id, event.id, Decimal("75.00"))
    
    total = repo.calculate_total(order.id)
    
    assert total == Decimal("125.00")
    
    # Verify it was persisted
    db_session.refresh(order)
    assert order.total_price == Decimal("125.00")


def test_get_expired_orders(db_session, create_user):
    """Test retrieving expired held orders."""
    user = create_user()
    repo = SQLAlchemyOrderRepository(db_session)
    
    # Create expired order
    expired_order = repo.create(user_id=user.id)
    repo.update_status(expired_order.id, OrderStatus.HELD)
    repo.set_expiration(expired_order.id, datetime.now(timezone.utc) - timedelta(minutes=5))
    
    # Create non-expired order
    valid_order = repo.create(user_id=user.id)
    repo.update_status(valid_order.id, OrderStatus.HELD)
    repo.set_expiration(valid_order.id, datetime.now(timezone.utc) + timedelta(minutes=5))
    
    expired = repo.get_expired_orders()
    
    assert len(expired) == 1
    assert expired[0].id == expired_order.id


def test_set_expiration(db_session, create_user):
    """Test setting order expiration time."""
    user = create_user()
    repo = SQLAlchemyOrderRepository(db_session)
    
    order = repo.create(user_id=user.id)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    repo.set_expiration(order.id, expires_at)
    
    db_session.refresh(order)
    assert order.expires_at is not None
    # Compare with some tolerance for microseconds
    assert abs((order.expires_at - expires_at).total_seconds()) < 1

