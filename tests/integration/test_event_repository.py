"""Integration tests for event repository."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from ticketer.models.order import OrderStatus
from ticketer.repositories.event_repository import SQLAlchemyEventRepository
from ticketer.repositories.order_repository import SQLAlchemyOrderRepository


def test_create_event(db_session, create_venue):
    """Test creating an event in the database."""
    venue = create_venue()
    repo = SQLAlchemyEventRepository(db_session)
    
    start_at = datetime.now(timezone.utc) + timedelta(days=30)
    event = repo.create(
        venue_id=venue.id,
        name="Test Concert",
        start_at=start_at,
        capacity=100,
    )
    
    assert event.id is not None
    assert event.name == "Test Concert"
    assert event.capacity == 100
    assert event.sales_open is True


def test_get_event_by_id(db_session, create_event):
    """Test retrieving an event by ID."""
    event = create_event(name="Test Event")
    repo = SQLAlchemyEventRepository(db_session)
    
    retrieved = repo.get_by_id(event.id)
    
    assert retrieved is not None
    assert retrieved.id == event.id
    assert retrieved.name == "Test Event"


def test_list_all_events(db_session, create_event):
    """Test listing all events."""
    create_event(name="Event 1")
    create_event(name="Event 2")
    create_event(name="Event 3", sales_open=False)
    
    repo = SQLAlchemyEventRepository(db_session)
    
    all_events = repo.list_all(sales_open_only=False)
    assert len(all_events) == 3
    
    open_events = repo.list_all(sales_open_only=True)
    assert len(open_events) == 2


def test_update_sales_status(db_session, create_event):
    """Test updating event sales status."""
    event = create_event(sales_open=True)
    repo = SQLAlchemyEventRepository(db_session)
    
    updated = repo.update_sales_status(event.id, False)
    
    assert updated is not None
    assert updated.sales_open is False


def test_get_reserved_count(db_session, create_user, create_event):
    """Test getting reserved ticket count for an event."""
    user = create_user()
    event = create_event()
    
    event_repo = SQLAlchemyEventRepository(db_session)
    order_repo = SQLAlchemyOrderRepository(db_session)
    
    # Create order with items
    order = order_repo.create(user_id=user.id)
    order_repo.add_item(order.id, event.id, Decimal("50.00"))
    order_repo.add_item(order.id, event.id, Decimal("50.00"))
    order_repo.update_status(order.id, OrderStatus.HELD)
    
    count = event_repo.get_reserved_count(event.id)
    
    assert count == 2


def test_get_reserved_count_excludes_cancelled(db_session, create_user, create_event):
    """Test that cancelled orders don't count toward reserved tickets."""
    user = create_user()
    event = create_event()
    
    event_repo = SQLAlchemyEventRepository(db_session)
    order_repo = SQLAlchemyOrderRepository(db_session)
    
    # Create cancelled order
    order1 = order_repo.create(user_id=user.id)
    order_repo.add_item(order1.id, event.id, Decimal("50.00"))
    order_repo.update_status(order1.id, OrderStatus.CANCELLED)
    
    # Create held order
    order2 = order_repo.create(user_id=user.id)
    order_repo.add_item(order2.id, event.id, Decimal("50.00"))
    order_repo.update_status(order2.id, OrderStatus.HELD)
    
    count = event_repo.get_reserved_count(event.id)
    
    # Should only count the held order
    assert count == 1

