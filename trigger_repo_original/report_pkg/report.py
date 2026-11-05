from .models import Order
from .pricing import discounted_total
from .shipping import shipping_cost


def order_total(order: Order) -> float:
    """Discounted subtotal plus shipping."""
    return discounted_total(order.subtotal, order.discount_pct) + shipping_cost(order)


def summarize(orders: list[Order]) -> dict[str, float]:
    """Map each order_id to its total."""
    return {o.order_id: order_total(o) for o in orders}


def grand_total(orders: list[Order]) -> float:
    return round(sum(o.subtotal for o in orders), 2)


def format_summary(orders: list[Order]) -> str:
    totals = summarize(orders)
    return "\n".join(f"{oid}: ${total:.2f}" for oid, total in sorted(totals.items()))
