from decimal import Decimal

import pytest

from shop.cart import CartError, total


def test_total():
    assert total([("apple", 2), ("pear", 1)]) == Decimal("1.75")


def test_unknown_sku():
    with pytest.raises(CartError):
        total([("kiwi", 1)])
