from sample_pkg.inventory import Inventory
from sample_pkg.reports import restock


def test_restock_sets_quantity():
    inv = Inventory()
    inv.add("pen", 1, 1.0)
    restock(inv, "pen", 20)
    assert inv.items["pen"]["qty"] == 20
