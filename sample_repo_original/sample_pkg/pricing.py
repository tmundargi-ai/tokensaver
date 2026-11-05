from .textutils import round_money


def apply_discount(price: float, fraction: float) -> float:
    """Reduce price by fraction, e.g. 0.1 for 10 percent off."""
    return price * (1 - fraction)


def format_price(amount: float) -> str:
    """Format an amount as dollars with two decimals."""
    return f"${round_money(amount):.2f}"
