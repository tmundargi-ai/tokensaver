import argparse
import json
import os

from openai import OpenAI
from tools import TOOL_SPECS, read_file, edit_file, search_code, run_tests
from optimize import truncate_output, ReadCache

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
    max_retries=5,
    timeout=120,
)

MODEL = "muse-spark-1.3"
MAX_STEPS = 15
LOG_FILE = "runs.jsonl"
DEFAULT_TASK = "The tests in sample_repo are failing. Find the bug and fix it."
MODES = ["baseline", "truncate-only", "optimized"]

SYSTEM = (
    "You are a coding agent working in a small Python repo. "
    "Make only the change the task asks for. "
    "After every edit, run the tests. "
    "Stop as soon as the target tests pass: reply with a one-paragraph summary "
    "and make no further tool calls. "
    "Do not read files unrelated to the task, and do not edit files outside "
    "the code the task names."
)


def make_dispatch(mode: str):
    reads_cached = mode == "optimized"
    truncating = mode in ("optimized", "truncate-only")
    cache = ReadCache()

    def clip(out: str) -> str:
        if not truncating:
            return out
        clipped = truncate_output(out)
        if clipped != out:
            print("  [truncated tool output]")
        return clipped

    def dispatch(name: str, args: dict) -> str:
        try:
            if name == "read_file":
                if reads_cached:
                    return cache.read(args["path"], read_file)
                return read_file(args["path"])
            if name == "edit_file":
                return edit_file(args["path"], args["old"], args["new"])
            if name == "search_code":
                return clip(search_code(args["pattern"]))
            if name == "run_tests":
                return clip(run_tests())
            return f"unknown tool: {name}"
        except Exception as e:
            return f"tool error: {e}"

    return dispatch, cache


def run(task: str, mode: str) -> None:
    dispatch, cache = make_dispatch(mode)
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": task},
    ]
    totals = {"prompt_tokens": 0, "completion_tokens": 0, "cached_tokens": 0}
    steps = 0
    completed = False
    edited: list[str] = []

    for step in range(1, MAX_STEPS + 1):
        steps = step
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_SPECS,
        )
        msg = response.choices[0].message
        usage = response.usage

        totals["prompt_tokens"] += usage.prompt_tokens
        totals["completion_tokens"] += usage.completion_tokens
        details = usage.prompt_tokens_details
        totals["cached_tokens"] += (details.cached_tokens or 0) if details else 0
        print(f"step {step}: in={usage.prompt_tokens} out={usage.completion_tokens}")

        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            completed = True
            print("\nFINAL:", msg.content)
            break

        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            if call.function.name == "edit_file":
                edited.append(args.get("path", ""))
            result = dispatch(call.function.name, args)
            print(f"  -> {call.function.name}({args})")
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result[:20000],
            })
    else:
        print("stopped: reached MAX_STEPS")

    record = {
        "task": task,
        "mode": mode,
        "steps": steps,
        "completed": completed,
        "edited_files": sorted(set(edited)),
        "reads_suppressed": cache.suppressed,
        **totals,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")
    print("\nTOTALS:", record)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=MODES, default="baseline")
    parser.add_argument("task", nargs="?", default=DEFAULT_TASK)
    args = parser.parse_args()
    run(args.task, args.mode)
