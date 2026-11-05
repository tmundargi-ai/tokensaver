import pytest
from sample_pkg.inventory import Inventory


def test_add_and_quantity():
    inv = Inventory()
    inv.add("pen", 10, 2.0)
    inv.add("pen", 5, 2.0)
    assert inv.items["pen"]["qty"] == 15


def test_discounted_value():
    inv = Inventory()
    inv.add("pen", 10, 2.0)
    assert inv.discounted_value("pen", 10) == pytest.approx(18.0)


def test_update_quantity_clamps():
    inv = Inventory()
    inv.add("pen", 1, 1.0)
    inv.update_quantity("pen", 50_000)
    assert inv.items["pen"]["qty"] == 10_000
    inv.update_quantity("pen", -5)
    assert inv.items["pen"]["qty"] == 0


def test_add_rejects_negative():
    inv = Inventory()
    with pytest.raises(ValueError):
        inv.add("pen", -1, 1.0)


def test_remove_insufficient_raises():
    inv = Inventory()
    inv.add("pen", 2, 1.0)
    with pytest.raises(ValueError):
        inv.remove("pen", 5)
