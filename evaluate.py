import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT / "sample_repo"
ORIGINAL = ROOT / os.environ.get("SUITE_REPO", "sample_repo_original")
HIDDEN_FILE = ROOT / "hidden_tests" / "test_top_stocked.py"
RUNS_LOG = ROOT / "runs.jsonl"
EVAL_LOG = ROOT / "eval_runs.jsonl"
RESULTS_MD = ROOT / "results.md"
LOG_DIR = ROOT / "eval_logs"
MAX_ATTEMPTS = 3
MODE_ORDER = ("baseline", "truncate-only", "optimized")

PRICING = json.loads((ROOT / "pricing.json").read_text())
TASKS = json.loads((ROOT / os.environ.get("SUITE_TASKS", "tasks.json")).read_text())
HIDDEN_TEST_ID = "tests/test_top_stocked.py::test_top_stocked"
RESULT_RE = re.compile(r"^(PASSED|FAILED|ERROR) (\S+)")


def target_ids(task):
    return [HIDDEN_TEST_ID if t.startswith("hidden") else t for t in task["target_tests"]]


ALL_TARGET_IDS = {tid for t in TASKS for tid in target_ids(t)}


def collect_protected():
    """Tests in the original repo that are not targets of any task."""
    out = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=ORIGINAL, capture_output=True, text=True,
    ).stdout
    collected = [line.strip() for line in out.splitlines() if "::" in line]
    return [c for c in collected if c not in ALL_TARGET_IDS]


def reset_repo():
    if REPO.exists():
        shutil.rmtree(REPO)
    shutil.copytree(ORIGINAL, REPO,
                    ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))


def run_tests_in_repo(add_hidden):
    if add_hidden:
        shutil.copy(HIDDEN_FILE, REPO / "tests" / HIDDEN_FILE.name)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-rA", "--tb=no"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    outcomes = {}
    for line in proc.stdout.splitlines():
        m = RESULT_RE.match(line)
        if m:
            outcomes[m.group(2)] = m.group(1)
    return outcomes


def cost(prompt, cached, completion):
    uncached = prompt - cached
    return (uncached * PRICING["input_per_m"]
            + cached * PRICING["cached_input_per_m"]
            + completion * PRICING["output_per_m"]) / 1_000_000


def evaluate_one(task, mode, rep, protected):
    reset_repo()
    before = len(RUNS_LOG.read_text().splitlines()) if RUNS_LOG.exists() else 0
    proc = subprocess.run(
        [sys.executable, "agent.py", "--mode", mode, task["description"]],
        cwd=ROOT, capture_output=True, text=True, timeout=900,
    )
    LOG_DIR.mkdir(exist_ok=True)
    (LOG_DIR / f"{task['id']}_{mode}_rep{rep}.txt").write_text(proc.stdout + proc.stderr)

    lines = RUNS_LOG.read_text().splitlines() if RUNS_LOG.exists() else []
    new = lines[before:]
    rec = json.loads(new[-1]) if new else {}

    targets = target_ids(task)
    outcomes = run_tests_in_repo(add_hidden=HIDDEN_TEST_ID in targets)
    target_failures = [t for t in targets if outcomes.get(t) != "PASSED"]
    protected_failures = [p for p in protected if outcomes.get(p) != "PASSED"]

    completed = bool(rec.get("completed", False))
    allowed = set(task["allowed_files"])
    out_of_scope = [f for f in rec.get("edited_files", []) if f not in allowed]
    passed = (bool(rec) and completed and not target_failures
              and not protected_failures and not out_of_scope)

    prompt = rec.get("prompt_tokens", 0)
    cached = rec.get("cached_tokens", 0)
    completion = rec.get("completion_tokens", 0)
    return {
        "task": task["id"], "mode": mode, "rep": rep, "passed": passed,
        "agent_ran": bool(rec), "completed": completed,
        "out_of_scope": out_of_scope,
        "target_failures": target_failures,
        "protected_failures": protected_failures,
        "steps": rec.get("steps", 0), "prompt_tokens": prompt,
        "cached_tokens": cached, "completion_tokens": completion,
        "reads_suppressed": rec.get("reads_suppressed", 0),
        "cost": cost(prompt, cached, completion),
    }


def row(label, group):
    n = len(group)
    passes = sum(1 for r in group if r["passed"])
    completed = sum(1 for r in group if r["completed"])
    out_of_scope = sum(1 for r in group if r["out_of_scope"])
    total_cost = sum(r["cost"] for r in group)

    def avg(key):
        return sum(r[key] for r in group) / n

    cost_per_pass = f"${total_cost / passes:.4f}" if passes else "n/a"
    return (f"| {label} | {n} | {passes / n:.0%} | {completed / n:.0%} | "
            f"{out_of_scope} | {avg('prompt_tokens'):.0f} | "
            f"{avg('cached_tokens'):.0f} | {avg('completion_tokens'):.0f} | "
            f"{avg('steps'):.1f} | {avg('reads_suppressed'):.1f} | "
            f"${total_cost / n:.4f} | {cost_per_pass} |")


HEADER = ("| Group | Runs | Pass rate | Finished | Out-of-scope runs | Avg prompt | "
          "Avg cached | Avg output | Avg steps | Avg reads suppressed | "
          "Avg cost/run | Cost per passing task |\n"
          "|---|---|---|---|---|---|---|---|---|---|---|---|")


def write_results(runs):
    modes = [m for m in MODE_ORDER if any(r["mode"] == m for r in runs)]
    task_ids = [t["id"] for t in TASKS if any(r["task"] == t["id"] for r in runs)]
    out = [
        "# Evaluation results",
        "",
        f"Model: {PRICING['model']}. Prices in USD per 1M tokens: input "
        f"{PRICING['input_per_m']}, cached {PRICING['cached_input_per_m']}, "
        f"output {PRICING['output_per_m']}.",
        "",
        "A run passes only if it finished before the step cap, its target and "
        "protected tests pass, and it edited only files its task allows. "
        "Cost per passing task divides total spend, including failed runs, "
        "by the number of passing runs.",
        "",
        "## By mode",
        "",
        HEADER,
    ]
    for mode in modes:
        out.append(row(mode, [r for r in runs if r["mode"] == mode]))
    out += ["", "## By task", "", HEADER]
    for task_id in task_ids:
        for mode in modes:
            group = [r for r in runs if r["task"] == task_id and r["mode"] == mode]
            if group:
                out.append(row(f"{task_id} / {mode}", group))
    RESULTS_MD.write_text("\n".join(out) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", default="all", help="comma-separated task ids, or all")
    parser.add_argument("--modes", default="baseline,optimized")
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()

    tasks = TASKS if args.tasks == "all" else [
        t for t in TASKS if t["id"] in args.tasks.split(",")]
    modes = args.modes.split(",")

    protected = collect_protected()
    if not protected:
        sys.exit("No protected tests found. Check the suite repo.")
    total = len(tasks) * len(modes) * args.repeats
    print(f"protected tests: {len(protected)}; agent runs planned: {total}")

    EVAL_LOG.write_text("")
    runs = []
    for task in tasks:
        for mode in modes:
            for rep in range(1, args.repeats + 1):
                for attempt in range(MAX_ATTEMPTS):
                    r = evaluate_one(task, mode, rep, protected)
                    if r["agent_ran"]:
                        break
                    if attempt < MAX_ATTEMPTS - 1:
                        print(f"  no agent record for {task['id']} {mode} rep{rep}; "
                              f"retrying ({attempt + 2}/{MAX_ATTEMPTS})")
                runs.append(r)
                with EVAL_LOG.open("a") as f:
                    f.write(json.dumps(r) + "\n")
                status = "PASS" if r["passed"] else "FAIL"
                print(f"{task['id']} {mode} rep{rep}: {status} "
                      f"finished={r['completed']} cost=${r['cost']:.4f}")

    reset_repo()
    write_results(runs)
    print(f"wrote {RESULTS_MD}")


if __name__ == "__main__":
    main()
