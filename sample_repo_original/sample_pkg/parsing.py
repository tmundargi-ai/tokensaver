def parse_kv_pairs(text: str) -> dict[str, str]:
    """Parse lines like 'key=value' into a dictionary. Blank lines are skipped."""
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def parse_percentage(text: str) -> float:
    """Convert a string like '42%' to 0.42."""
    cleaned = text.strip()
    return float(cleaned) / 100
