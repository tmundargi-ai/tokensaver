import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TASKS_FILE = ROOT / os.environ.get("SUITE_TASKS", "tasks_trigger.json")
EVAL_FILE = ROOT / "eval_runs.jsonl"
LOG_DIR = ROOT / "eval_logs"
OUT = ROOT / "docs" / "dataset.json"

TOOL_RE = re.compile(r"^\s+-> (\w+)\((.*)\)$")
PATH_RE = re.compile(r"'path': '([^']+)'")
HOME_RE = re.compile(r"/(home|Users)/[^\s'\"]+")


def parse_trace(text):
    calls, pending = [], False
    for line in text.splitlines():
        if line.strip() == "[truncated tool output]":
            pending = True
            continue
        m = TOOL_RE.match(line)
        if m:
            args = HOME_RE.sub("<path>", m.group(2))
            calls.append({"tool": m.group(1), "args": args, "truncated": pending})
            pending = False
    return calls


def main():
    tasks = json.loads(TASKS_FILE.read_text())
    runs = []
    for line in EVAL_FILE.read_text().splitlines():
        r = json.loads(line)
        log = LOG_DIR / f"{r['task']}_{r['mode']}_rep{r['rep']}.txt"
        text = log.read_text() if log.exists() else ""
        trace = parse_trace(text)
        edited = sorted({
            m.group(1)
            for c in trace if c["tool"] == "edit_file"
            for m in [PATH_RE.search(c["args"])] if m
        })
        runs.append({
            "task": r["task"], "mode": r["mode"], "rep": r["rep"],
            "pass": r["passed"], "finished": r["completed"],
            "target_failures": r["target_failures"],
            "protected_failures": r["protected_failures"],
            "out_of_scope": r["out_of_scope"],
            "edited": edited, "steps": r["steps"],
            "prompt": r["prompt_tokens"], "cached": r["cached_tokens"],
            "output": r["completion_tokens"], "reads": r["reads_suppressed"],
            "cost": round(r["cost"], 6),
            "truncated": "truncated tool output" in text,
            "trace": trace,
        })

    data = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tasks": tasks,
        "runs": runs,
    }
    text = json.dumps(data, indent=2)
    key = os.environ.get("MODEL_API_KEY", "")
    if key and key in text:
        sys.exit("Refusing to write: the API key appears in the output.")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(text)
    print(f"wrote {OUT} with {len(runs)} runs")


if __name__ == "__main__":
    main()
