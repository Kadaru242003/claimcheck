# Contributing

Thanks for helping. The most useful contributions are **new tasks** and **new ways to
fake a pass** (with the fix).

## Setup

```
git clone https://github.com/Kadaru242003/claimcheck
cd claimcheck
pip install -e .
python -m pytest -q
```

Docker is needed for `claimcheck sandbox-test` and for running models.

## Adding a task

1. Read `docs/TASK_FORMAT.md`, especially the rules for impossible and broken tasks.
2. Add a folder under `tasks/` with the next free id for its category.
3. Run `claimcheck check-tasks` and `claimcheck probe`. Both must report 0 problems.
4. Open a pull request. CI runs the same checks.

## Reporting a cheat

If you find a solution.py that makes an unsolvable task pass, that is a real bug.
Open an issue with the task id and the code. A fix comes with a new entry in
`scripts/probe_exploits.py` so the cheat stays blocked.

## Running models

Running agents uses an API key and the free-tier budget guard (`claimcheck preflight`,
`claimcheck run --plan pilot`). Nothing in tests or CI calls a model.
