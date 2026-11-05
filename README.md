# TokenSaver

I wanted to know whether a coding agent could finish the same tasks while sending less text to the model. Every step of an agent loop sends the whole conversation back, so a long test log or a file read twice gets billed again on each later step. TokenSaver is a small harness that runs a coding agent on Muse Spark 1.3 in three modes and measures what changes.

The short version: across 60 runs, the optimized mode used about 11% fewer prompt tokens and cost about 18% less per run. Every run still passed its tests. I could not show that the read cache saves anything measurable on this suite, and the details are below.

## How it works

The agent gets a coding task, such as "fix this bug" or "add a sort order," and a set of tools:

- `read_file` reads a file in the sample repo
- `search_code` greps the Python files
- `edit_file` replaces one exact piece of text in a file
- `run_tests` runs pytest

The model picks a tool, the harness runs it, the result goes back into the conversation, and the loop repeats until the model stops calling tools or hits 15 steps.

There are two optimizations, both in `optimize.py`:

1. **Truncation.** If a tool result is longer than 60 lines, the harness keeps the first 20 and last 20 lines, plus up to 20 lines from the middle that mention an error or failure. The rest is replaced with a count of omitted lines.
2. **Read cache.** If the agent reads a file and then reads it again without the content changing, the second read returns a short note instead of the whole file.

The three modes are:

- **Baseline:** no changes.
- **Truncate-only:** truncation on, read cache off. This is the control. It shows how much of the effect comes from truncation alone.
- **Optimized:** truncation and the read cache.

## How a run is scored

A run only passes if all of these hold:

1. The agent finished before the step limit.
2. The target tests for the task pass. For t3, a hidden test is also run.
3. The protected tests pass. These are the tests no task is supposed to touch.
4. The agent only edited files its task allows.

The evaluator resets the repo and runs the tests itself. The model saying "done" doesn't count. This check is in `evaluate.py`, and it runs after the agent process exits.

## Repository layout

| File | What it does |
|---|---|
| `agent.py` | The agent loop. Sends requests to the model, runs tool calls, and writes one record per run to `runs.jsonl`. |
| `tools.py` | The four tools. Paths are resolved and rejected if they fall outside the repo. |
| `optimize.py` | Truncation and the read cache. |
| `evaluate.py` | Runs every task in every mode, scores each run, and writes `eval_runs.jsonl`, `eval_logs/`, and `results.md`. |
| `export_dataset.py` | Builds `site/dataset.json` from the eval output for the results page. |
| `tasks_trigger.json` | The four tasks used for the final experiment. |
| `tasks.json` | The first, smaller task set I used during development. |
| `pricing.json` | Muse Spark 1.3 rates in USD per 1M tokens. |
| `trigger_repo_original/` | The test repo for the final experiment. It's copied fresh before every run. |
| `sample_repo_original/` | The smaller repo used for development. |
| `hidden_tests/` | The hidden test for t3. The agent never sees it during a run. |
| `eval_runs.jsonl` | One record per evaluated run from the final experiment. |
| `eval_logs/` | The printed output of each final run, which is where the traces come from. |
| `results.md` | The final results tables. |
| `site/` | A static results page. |
| `first_call.py` | The first API call I made, as a minimal example. |

## Setup

You need Python 3.9 or newer, git, and a Meta Model API key with credits. I developed this on Windows using WSL (Ubuntu) with Python 3.14.

```bash
git clone https://github.com/YOUR-USERNAME/tokensaver.git
cd tokensaver
python3 -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
export MODEL_API_KEY="your-key-here"
```

Keep the key in your environment. Don't put it in a file that gets committed.

## Running one task

The agent works on a folder called `sample_repo`, which is generated and not committed. Copy the trigger repo into place first:

```bash
cp -r trigger_repo_original sample_repo
python agent.py --mode optimized "format_summary should list orders from highest total to lowest, one per line."
```

The output shows each step with its token counts, the tool calls, and a totals line. The same record is appended to `runs.jsonl`.

You can also run the tests yourself:

```bash
cd sample_repo && python -m pytest -q
```

## Running the full evaluation

```bash
SUITE_REPO=trigger_repo_original SUITE_TASKS=tasks_trigger.json python evaluate.py --repeats 5
```

This runs 4 tasks in 3 modes, 5 times each, for 60 runs. It takes roughly an hour and costs under a dollar at the listed rates. Results go to `results.md`, and per-run records go to `eval_runs.jsonl`.

Be careful with the environment variables. Without them, `evaluate.py` uses the first, smaller suite (`sample_repo_original` and `tasks.json`), which is not the suite behind the results below.

## Results

These numbers come from `results.md`. Each mode has 20 runs (4 tasks × 5 repeats).

| Mode | Pass rate | Avg prompt tokens | Avg cached tokens | Avg output tokens | Avg steps | Avg cost per run |
|---|---|---|---|---|---|---|
| Baseline | 100% | 10,485 | 5,683 | 1,202 | 5.8 | $0.0120 |
| Truncate-only | 100% | 9,429 | 6,216 | 1,308 | 5.9 | $0.0105 |
| Optimized | 100% | 9,284 | 6,523 | 1,271 | 5.8 | $0.0098 |

By task:

| Task | Baseline prompt | Truncate-only prompt | Optimized prompt | Baseline cost | Truncate-only cost | Optimized cost |
|---|---|---|---|---|---|---|
| tr1 heavy surcharge | 8,549 | 7,320 | 6,962 | $0.0090 | $0.0077 | $0.0069 |
| tr2 grand total | 7,820 | 8,081 | 8,223 | $0.0091 | $0.0094 | $0.0083 |
| tr3 summary order | 9,088 | 7,704 | 7,764 | $0.0109 | $0.0078 | $0.0080 |
| tr4 reject discount | 16,484 | 14,613 | 14,189 | $0.0188 | $0.0171 | $0.0161 |

All 60 runs passed, finished, and stayed inside their allowed files.

## What the results show

**Truncation.** It fired on tr1, tr3, and tr4, in every run of the two modes that have it. On those three tasks, prompt tokens dropped by roughly 11 to 19% compared with baseline. On tr2, truncation never fired, and prompt tokens stayed flat. That's the check that tells me the drop comes from truncation and not from the task.

**The read cache.** It fired only on tr4, the task that asks the agent to read `report.py`, edit another file, and read `report.py` again. Each optimized run suppressed exactly one re-read. Compared with truncate-only, the effect on prompt tokens was about 3%, which is inside the run-to-run spread. I don't have evidence that the cache saves money on this suite. It works as designed, and this sample can't show a saving.

**tr2 is the exception.** The optimized average prompt (8,223) is higher than baseline (7,820). One optimized run used 9,860 prompt tokens, and the other four averaged about 7,815. Cost on tr2 is still lower in optimized mode, but that comes from cache hits, and those vary between runs more than prompt size does.

**Cost is noisy.** Cached-token counts move a lot between runs. I treat prompt tokens as the main measure and cost as secondary.

## Limits

- One model, one synthetic repo, four tasks, five repeats per cell. The result describes this suite. It doesn't say much about coding agents in general.
- Task 4 tells the agent to re-read `report.py`. The test shows the mechanism works. It does not show that the agent re-reads files on its own.
- The hidden test for t3 is in `hidden_tests/`, so anyone reading the repo can see it. "Hidden" only means the agent never sees it during a run.
- The repo is generated code built for testing. It isn't a production codebase.

## The results page

`site/index.html` is a static page with the workflow, the results, and a run explorer. To load the full traces and per-run costs, generate the data file and serve the folder:

```bash
SUITE_TASKS=tasks_trigger.json python export_dataset.py
cd site
python3 -m http.server 8000
```

Then open http://localhost:8000. Without `dataset.json`, the page still shows the aggregate and per-task numbers.

## License

MIT
