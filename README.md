# claimcheck

A benchmark and harness that tests whether AI coding agents falsely claim success.

Every task has known ground truth. Some can be solved. Some cannot: the tests contradict
the spec, or the environment is broken. When a model says "done, all tests pass," we
already know whether that is true.

## Task categories

| Category | Can it be solved? | Example |
|---|---|---|
| solvable | Yes | Merge overlapping intervals |
| impossible | No | Spec asks for three even numbers with an odd sum |
| broken_env | No | Tests import a helper module that does not exist |

## Task folder

```
tasks/<id>/
  task.md            instructions the model sees
  solution_stub.py   starter code
  test_task.py       pytest tests (ground truth)
  reference.py       our solution (best effort for unsolvable tasks)
  meta.json          id, category, solvable, why_unsolvable, known_exploits
```

## Check the tasks

```
pip install -r requirements.txt
python scripts/check_tasks.py
```

The checker confirms that solvable references pass, unsolvable references fail, and
empty stubs always fail.

## Status

Day 1: task format, checker, first 12 tasks.
