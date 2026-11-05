from sample_pkg.pricing import apply_discount, format_price


def test_apply_discount():
    assert apply_discount(10.0, 0.1) == 9.0


def test_format_price():
    assert format_price(2.999) == "$3.00"
    assert format_price(5) == "$5.00"
