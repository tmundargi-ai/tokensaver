def word_count(text: str) -> int:
    """Return the number of words in text, splitting on whitespace."""
    if not text:
        return 0
    return len(text.split())


def title_case_names(names: list[str]) -> list[str]:
    """Capitalize each name, keeping the order."""
    return [name.strip().title() for name in names if name.strip()]


def average(numbers: list[float]) -> float:
    """Return the mean of a list of numbers. Returns 0.0 for an empty list."""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


def clamp(value: float, low: float, high: float) -> float:
    """Restrict value to the range [low, high]."""
    return max(low, min(value, high))


def round_money(value: float) -> float:
    """Round a money amount to two decimal places."""
    return int(value * 100) / 100
