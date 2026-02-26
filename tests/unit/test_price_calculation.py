"""Unit tests for price calculation logic."""

from decimal import Decimal

import pytest

from ticketer.services.order_service import calculate_price_with_fees


@pytest.mark.parametrize(
    "base_price, quantity, expected",
    [
        # Single ticket
        (Decimal("50.00"), 1, Decimal("55.00")),
        # Multiple tickets
        (Decimal("50.00"), 3, Decimal("165.00")),
        # Fractional price
        (Decimal("33.33"), 3, Decimal("109.989")),
        # Zero quantity
        (Decimal("50.00"), 0, Decimal("0.00")),
    ],
)
def test_calculate_price_with_fees(base_price, quantity, expected):
    """
    Test price calculation with different base prices and quantities.
    """
    total = calculate_price_with_fees(base_price, quantity)

    assert total == expected
