from report_pkg.pricing import discounted_total


def test_discounted_total():
    assert discounted_total(100.0, 10) == 90.0


def test_discounted_total_no_discount():
    assert discounted_total(50.0, 0) == 50.0
def test_discount_rejects_over_100():
    import pytest
    with pytest.raises(ValueError):
        discounted_total(100.0, 120)
