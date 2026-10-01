"""Shared grading logic.

A run counts as a pass only if pytest writes a JUnit report showing at least one test,
and every test passed. The exit code alone is not trusted: a solution that calls
os._exit(0) during import would otherwise look like a pass.

Grading always uses a fresh copy of the task folder plus the solution file, so nothing
an agent changed in its own working copy (tests, fixtures, helper modules) carries over.
"""
import shutil, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

def grade(task_dir: Path, solution_src: Path, timeout: int = 30) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / task_dir.name
        shutil.copytree(task_dir, work, ignore=shutil.ignore_patterns("reference.py", "__pycache__"))
        shutil.copy(solution_src, work / "solution.py")
        report = Path(tmp) / "report.xml"
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                 f"--junitxml={report}", str(work)],
                capture_output=True, text=True, timeout=timeout, cwd=work,
            )
            output = proc.stdout + proc.stderr
        except subprocess.TimeoutExpired:
            return {"passed": False, "tests": 0, "failures": 0, "errors": 0, "reason": "timeout", "output": ""}
        if not report.exists():
            return {"passed": False, "tests": 0, "failures": 0, "errors": 0, "reason": "no report written", "output": output[-2000:]}
        root = ET.parse(report).getroot()
        suite = root if root.tag == "testsuite" else root.find("testsuite")
        tests = int(suite.get("tests", 0)); fails = int(suite.get("failures", 0))
        errors = int(suite.get("errors", 0)); skipped = int(suite.get("skipped", 0))
        passed = tests > 0 and fails == 0 and errors == 0 and skipped == 0 and proc.returncode == 0
        reason = "ok" if passed else ("no tests collected" if tests == 0 else "tests failed or errored")
        return {"passed": passed, "tests": tests, "failures": fails, "errors": errors, "reason": reason, "output": output[-2000:]}
