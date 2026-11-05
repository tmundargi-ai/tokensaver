from .inventory import Inventory


def restock(inv: Inventory, name: str, target: int) -> None:
    """Bring an item up to target units."""
    inv.set_quantity(name, target)
