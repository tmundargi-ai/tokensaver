import subprocess
import sys
from pathlib import Path

REPO = (Path(__file__).parent / "sample_repo").resolve()


def _safe_path(rel: str) -> Path:
    """Resolve a path and refuse anything outside sample_repo."""
    p = (REPO / rel).resolve()
    if p != REPO and REPO not in p.parents:
        raise ValueError(f"path outside sample_repo: {rel}")
    return p


def read_file(path: str) -> str:
    return _safe_path(path).read_text()


def edit_file(path: str, old: str, new: str) -> str:
    p = _safe_path(path)
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        return f"edit failed: old text found {count} times, must be exactly 1"
    p.write_text(text.replace(old, new))
    return "edit applied"


def search_code(pattern: str) -> str:
    result = subprocess.run(
        ["grep", "-rn", "--include=*.py", pattern, str(REPO)],
        capture_output=True, text=True, timeout=10,
    )
    return result.stdout or "no matches"


def run_tests() -> str:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    return result.stdout + result.stderr


TOOL_SPECS = [
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a file in sample_repo. Path is relative to sample_repo.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "edit_file",
        "description": "Replace one exact occurrence of old text with new text in a file.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"},
            "old": {"type": "string"},
            "new": {"type": "string"}}, "required": ["path", "old", "new"]}}},
    {"type": "function", "function": {
        "name": "search_code",
        "description": "Search for a text pattern in the .py files of sample_repo.",
        "parameters": {"type": "object", "properties": {
            "pattern": {"type": "string"}}, "required": ["pattern"]}}},
    {"type": "function", "function": {
        "name": "run_tests",
        "description": "Run the pytest suite for sample_repo and return the output.",
        "parameters": {"type": "object", "properties": {}}}},
]
