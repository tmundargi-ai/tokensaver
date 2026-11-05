from dataclasses import dataclass


@dataclass
class Order:
    order_id: str
    weight_kg: float
    subtotal: float
    discount_pct: float = 0.0
