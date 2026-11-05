import hashlib


def truncate_output(text: str, max_lines: int = 60, keep: int = 20,
                    max_error_lines: int = 20) -> str:
    """Keep the first and last lines, plus error lines from the middle."""
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    head = lines[:keep]
    tail = lines[-keep:]
    middle = lines[keep:-keep]
    errors = [l for l in middle
              if "error" in l.lower() or "fail" in l.lower()][:max_error_lines]
    omitted = len(middle) - len(errors)
    return "\n".join(
        head
        + [f"... {omitted} lines omitted ..."]
        + (["[error lines from the omitted section:]"] + errors if errors else [])
        + tail
    )


class ReadCache:
    """Suppress re-reads of files whose content hasn't changed in this run."""

    def __init__(self):
        self._seen: dict[str, str] = {}
        self.suppressed = 0

    def read(self, path: str, reader) -> str:
        content = reader(path)
        digest = hashlib.sha256(content.encode()).hexdigest()
        if self._seen.get(path) == digest:
            self.suppressed += 1
            return (f"{path} is unchanged since it was last read; "
                    "its content is already earlier in this conversation.")
        self._seen[path] = digest
        return content
