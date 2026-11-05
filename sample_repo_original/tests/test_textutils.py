from sample_pkg.textutils import word_count, title_case_names, average, clamp


def test_word_count():
    assert word_count("hello big world") == 3
    assert word_count("") == 0


def test_title_case_names():
    assert title_case_names(["  alice ", "BOB", ""]) == ["Alice", "Bob"]


def test_average():
    assert average([1, 2, 3]) == 2
    assert average([]) == 0.0


def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0
    assert clamp(99, 0, 10) == 10
