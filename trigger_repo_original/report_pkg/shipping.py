from .models import Order

BASE_RATE = 5.0
PER_KG = 1.5
HEAVY_THRESHOLD_KG = 10.0
HEAVY_SURCHARGE = 8.0


def shipping_cost(order: Order) -> float:
    """Base rate plus a per-kg charge. Orders over 10 kg add a flat heavy surcharge."""
    cost = BASE_RATE + PER_KG * order.weight_kg
    if order.weight_kg > HEAVY_THRESHOLD_KG:
        pass  # heavy surcharge not applied yet
    return round(cost, 2)
