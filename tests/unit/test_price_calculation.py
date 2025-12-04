"""Unit tests for price calculation logic."""

from decimal import Decimal

from ticketer.services.order_service import calculate_price_with_fees


def test_calculate_price_with_fees_single_ticket():
    """Test price calculation for a single ticket."""
    base_price = Decimal("50.00")
    quantity = 1

    total = calculate_price_with_fees(base_price, quantity)

    # 50 + 10% fee = 55
    assert total == Decimal("55.00")


def test_calculate_price_with_fees_multiple_tickets():
    """Test price calculation for multiple tickets."""
    base_price = Decimal("50.00")
    quantity = 3

    total = calculate_price_with_fees(base_price, quantity)

    # (50 * 3) + 10% fee = 150 + 15 = 165
    assert total == Decimal("165.00")


def test_calculate_price_with_fees_fractional():
    """Test that price calculation handles fractional amounts correctly."""
    base_price = Decimal("33.33")
    quantity = 3

    total = calculate_price_with_fees(base_price, quantity)

    # 33.33 + 10% fee = 36.663 (should be exact decimal)
    expected = Decimal("33.33") * Decimal("1.10") * Decimal("3")
    assert total == expected
