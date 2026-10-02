"""Checks before any model call. Uses only Groq's free model-list endpoint (no tokens).

Stops if:
  - GROQ_API_KEY is missing
  - any of the 3 required models is not available on this account
    (the judge, qwen/qwen3.8-27b, is NEVER replaced by another model)
  - Docker is not running
"""
import json, os, subprocess, sys, urllib.error, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from claimcheck.config import GROQ_BASE_URL, API_KEY_ENV, USER_AGENT, AGENT_MODELS, JUDGE_MODEL

def available_models(key: str) -> set[str]:
    req = urllib.request.Request(f"{GROQ_BASE_URL}/models", headers={"Authorization": f"Bearer {key}", "User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        return {m["id"] for m in json.loads(r.read())["data"] if m.get("active", True)}

def main() -> int:
    ok = True
    key = os.environ.get(API_KEY_ENV, "")
    if not key:
        print(f"STOP: {API_KEY_ENV} is not set. Run: source ~/.zshrc"); return 1
    try:
        models = available_models(key)
    except urllib.error.HTTPError as e:
        print(f"STOP: Groq refused the model list (HTTP {e.code}): {e.read().decode(errors='replace')[:200]}")
        print("Nothing was spent."); return 1
    for m in AGENT_MODELS:
        print(f"{'OK  ' if m in models else 'MISSING'} agent model {m}")
        ok &= m in models
    if JUDGE_MODEL in models:
        print(f"OK   judge model {JUDGE_MODEL}")
    else:
        print(f"STOP: judge model {JUDGE_MODEL} is not available on this account.")
        print("      The harness will not substitute another judge. Tell Claude before doing anything else.")
        ok = False
    docker = subprocess.run(["docker", "info"], capture_output=True)
    print(f"{'OK  ' if docker.returncode == 0 else 'STOP:'} Docker {'is running' if docker.returncode == 0 else 'is not running; open Docker Desktop'}")
    ok &= docker.returncode == 0
    print("\nManual check (the API cannot show billing): your Groq billing page must say Free plan,")
    print("with no payment method. If it shows anything else, stop and tell Claude.")
    print("\nPreflight passed." if ok else "\nPreflight FAILED. Do not run anything.")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
