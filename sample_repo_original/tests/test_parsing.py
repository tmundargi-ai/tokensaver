from sample_pkg.parsing import parse_kv_pairs, parse_percentage


def test_parse_kv_pairs():
    text = "name=Ada\n\nrole = engineer\n"
    assert parse_kv_pairs(text) == {"name": "Ada", "role": "engineer"}


def test_parse_percentage():
    assert parse_percentage("42%") == 0.42
    assert parse_percentage(" 7 % ") == 0.07
