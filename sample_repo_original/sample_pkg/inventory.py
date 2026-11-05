from .pricing import apply_discount
from .textutils import clamp

MAX_QUANTITY = 10_000


class Inventory:
    def __init__(self):
        self.items: dict[str, dict] = {}

    def add(self, name: str, qty: int, price: float) -> None:
        """Add qty units of name at price. Negative quantities should be rejected."""
        item = self.items.setdefault(name, {"qty": 0, "price": price})
        item["qty"] += qty
        item["price"] = price

    def remove(self, name: str, qty: int) -> None:
        """Remove qty units of name. Removing more than is stocked should raise ValueError."""
        self.items[name]["qty"] -= qty

    def set_quantity(self, name: str, qty: int) -> None:
        """Set the stocked quantity, kept between 0 and MAX_QUANTITY."""
        self.items[name]["qty"] = clamp(qty, 0, MAX_QUANTITY)

    def discounted_value(self, name: str, percent: float) -> float:
        """Total value of name after a percent discount, e.g. 10 for 10 percent off."""
        item = self.items[name]
        return item["qty"] * apply_discount(item["price"], percent)

    def total_value(self) -> float:
        return sum(i["qty"] * i["price"] for i in self.items.values())
