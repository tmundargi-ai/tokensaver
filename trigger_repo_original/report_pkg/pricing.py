def discounted_total(subtotal: float, discount_pct: float) -> float:
    """Apply a percentage discount, e.g. 10 for 10 percent off."""
    return round(subtotal * (1 - discount_pct / 100), 2)
