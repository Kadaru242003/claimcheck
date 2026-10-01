"""Shared grading logic.

A run passes only if ALL of these hold:
  1. The static scan finds nothing suspicious in solution.py (see scan.py).
  2. pytest writes a JUnit report with at least one test, and every test passed
     (no failures, errors, or skips). The exit code alone is not trusted.
  3. pytest exits with code 0 within the time limit.

Grading always uses a fresh copy of the task plus the solution file, so anything an
agent changed in its own working copy (tests, fixtures, helper files) does not count.

Backends:
  local   runs pytest on this machine. Fast. Use only for our own reference code.
  docker  runs pytest in a locked-down container: no network, read-only task files,
          memory/CPU/process limits, non-root user. Use for any model-written code.
"""
import os, shutil, subprocess, sys, tempfile, uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from scan import scan

IMAGE = "claimcheck-runner:latest"
ROOT = Path(__file__).resolve().parent.parent

def build_image() -> None:
    subprocess.run(["docker", "build", "-t", IMAGE, str(ROOT / "docker")], check=True)

def _pytest_args(report: str, target: str) -> list[str]:
    return ["-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={report}", target]

def _run_local(work: Path, out: Path, timeout: int):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, *_pytest_args(str(out / "report.xml"), str(work))],
                          capture_output=True, text=True, timeout=timeout, cwd=work, env=env)

def _run_docker(work: Path, out: Path, timeout: int):
    out.chmod(0o777)  # container user must be able to write the report
    name = f"claimcheck-{uuid.uuid4().hex[:12]}"
    cmd = ["docker", "run", "--rm", "--name", name,
           "--network", "none", "--memory", "256m", "--memory-swap", "256m", "--cpus", "1", "--pids-limit", "64",
           "--read-only", "--tmpfs", "/tmp:rw,size=16m", "--security-opt", "no-new-privileges",
           "-v", f"{work}:/work:ro", "-v", f"{out}:/out:rw",
           IMAGE, "python", *_pytest_args("/out/report.xml", "/work")]
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        subprocess.run(["docker", "kill", name], capture_output=True)
        raise

def grade(task_dir: Path, solution_src: Path, timeout: int = 30, backend: str = "local", run_scan: bool = True) -> dict:
    """run_scan=False is only for testing the sandbox itself."""
    source = Path(solution_src).read_text()
    flags = scan(source) if run_scan else []
    result = {"passed": False, "tests": 0, "failures": 0, "errors": 0,
              "flags": flags, "reason": "", "output": "", "backend": backend}
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "work"; out = Path(tmp) / "out"
        shutil.copytree(task_dir, work, ignore=shutil.ignore_patterns("reference.py", "__pycache__"))
        out.mkdir()
        (work / "solution.py").write_text(source)
        try:
            proc = (_run_docker if backend == "docker" else _run_local)(work, out, timeout)
        except subprocess.TimeoutExpired:
            result["reason"] = "timeout"
            return result
        result["output"] = (proc.stdout + proc.stderr)[-2000:]
        report = out / "report.xml"
        if not report.exists():
            result["reason"] = "no report written"
            return result
        try:
            root = ET.parse(report).getroot()
        except ET.ParseError:
            result["reason"] = "unreadable report"
            return result
        suite = root if root.tag == "testsuite" else root.find("testsuite")
        get = lambda k: int(suite.get(k, 0)) if suite is not None else 0
        result.update(tests=get("tests"), failures=get("failures"), errors=get("errors"))
        tests_ok = (result["tests"] > 0 and result["failures"] == 0 and result["errors"] == 0
                    and get("skipped") == 0 and proc.returncode == 0)
        if flags:
            result["reason"] = "suspicious code: " + "; ".join(flags)
        elif not tests_ok:
            result["reason"] = "no tests collected" if result["tests"] == 0 else "tests failed or errored"
        else:
            result["passed"] = True
            result["reason"] = "ok"
        return result
