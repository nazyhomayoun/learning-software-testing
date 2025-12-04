"""Unit tests for seat allocation logic."""

from unittest.mock import MagicMock
from ticketer.services.event_service import choose_best_seat


def test_choose_best_seat_prefers_front_rows():
    """Test that seat allocator prefers front rows (A over C)."""
    # Arrange
    mock_repo = MagicMock()
    mock_seats = [
        MagicMock(id=1, row="A", col=1, seat_label="A1"),
        MagicMock(id=2, row="C", col=1, seat_label="C1"),
    ]
    mock_repo.get_available_seats.return_value = mock_seats

    # Act
    chosen = choose_best_seat(mock_repo, event_id=123)

    # Assert
    assert chosen is not None
    assert chosen["id"] == 1
    assert chosen["row"] == "A"
    mock_repo.get_available_seats.assert_called_once_with(123)


def test_choose_best_seat_returns_none_when_no_seats():
    """Test that choose_best_seat returns None when no seats available."""
    # Arrange
    mock_repo = MagicMock()
    mock_repo.get_available_seats.return_value = []

    # Act
    chosen = choose_best_seat(mock_repo, event_id=123)

    # Assert
    assert chosen is None


def test_choose_best_seat_scoring():
    """Test seat scoring logic."""
    # Arrange
    mock_repo = MagicMock()
    mock_seats = [
        MagicMock(id=1, row="A", col=5, seat_label="A5"),
        MagicMock(id=2, row="B", col=5, seat_label="B5"),
        MagicMock(id=3, row="Z", col=1, seat_label="Z1"),
    ]
    mock_repo.get_available_seats.return_value = mock_seats

    # Act
    chosen = choose_best_seat(mock_repo, event_id=123)

    # Assert - should prefer row A (highest score)
    assert chosen["id"] == 1
    assert chosen["row"] == "A"

