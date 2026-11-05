from report_pkg.models import Order
from report_pkg.report import summarize, grand_total, format_summary


def test_summarize():
    orders = [Order("a", 2.0, 100.0, 10.0)]
    assert summarize(orders) == {"a": 98.0}


def test_grand_total_includes_shipping_and_discount():
    orders = [Order("a", 2.0, 100.0, 10.0), Order("b", 2.0, 50.0, 0.0)]
    assert grand_total(orders) == 156.0


def test_format_summary_sorted_by_total():
    orders = [Order("cheap", 1.0, 10.0, 0.0), Order("dear", 1.0, 200.0, 0.0)]
    lines = format_summary(orders).splitlines()
    assert lines[0].startswith("dear")


def test_reconciliation_log():
    orders = [Order(f"o{i:02d}", 2.0, 100.0 + i, 0.0) for i in range(60)]
    totals = summarize(orders)
    for oid, total in totals.items():
        print(f"reconcile {oid}: total={total:.2f}")
    print("END OF RECONCILIATION")
    assert grand_total(orders) == round(sum(totals.values()), 2)
