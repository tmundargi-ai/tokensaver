from report_pkg.models import Order
from report_pkg.shipping import shipping_cost


def test_light_order():
    assert shipping_cost(Order("a", 2.0, 0.0)) == 8.0


def test_heavy_order_surcharge():
    assert shipping_cost(Order("b", 12.0, 0.0)) == 31.0
