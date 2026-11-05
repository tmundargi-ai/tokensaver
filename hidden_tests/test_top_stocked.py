from sample_pkg.inventory import Inventory


def test_top_stocked():
    inv = Inventory()
    inv.add("a", 5, 1.0)
    inv.add("b", 20, 1.0)
    inv.add("c", 10, 1.0)
    assert inv.top_stocked(2) == ["b", "c"]
