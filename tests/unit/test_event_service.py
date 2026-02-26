"""Unit tests for EventService.check_availability."""

from unittest.mock import Mock

import pytest

from ticketer.services.event_service import EventService


def test_check_availability_event_not_found():
    """Should raise ValueError when event does not exist."""
    mock_repo = Mock()
    mock_repo.get_by_id.return_value = None

    service = EventService(mock_repo)

    with pytest.raises(ValueError, match="Event not found"):
        service.check_availability(event_id=1, requested_quantity=1)


def test_check_availability_sales_closed():
    """Should return False when sales are closed."""
    mock_event = Mock()
    mock_event.sales_open = False

    mock_repo = Mock()
    mock_repo.get_by_id.return_value = mock_event

    service = EventService(mock_repo)

    result = service.check_availability(event_id=1, requested_quantity=1)

    assert result is False


def test_check_availability_insufficient_capacity():
    """Should return False when available capacity is insufficient."""
    mock_event = Mock()
    mock_event.sales_open = True
    mock_event.capacity = 10

    mock_repo = Mock()
    mock_repo.get_by_id.return_value = mock_event
    mock_repo.get_reserved_count.return_value = 9  # only 1 seat left

    service = EventService(mock_repo)

    result = service.check_availability(event_id=1, requested_quantity=2)

    assert result is False


def test_check_availability_success():
    """Should return True when enough capacity is available."""
    mock_event = Mock()
    mock_event.sales_open = True
    mock_event.capacity = 10

    mock_repo = Mock()
    mock_repo.get_by_id.return_value = mock_event
    mock_repo.get_reserved_count.return_value = 3  # 7 seats available

    service = EventService(mock_repo)

    result = service.check_availability(event_id=1, requested_quantity=5)

    assert result is True
