"""Model clients.

GroqClient is the only client that sends network requests, and only to GROQ_BASE_URL,
only for models in ALLOWED_MODELS. There is no fallback to any other provider.

MockClient sends nothing and costs nothing. It exists to test the harness.
"""
import json, os, re, time, urllib.error, urllib.request
from .config import (GROQ_BASE_URL, API_KEY_ENV, USER_AGENT, ALLOWED_MODELS, AGENT_MODELS,
                     MAX_COMPLETION_TOKENS, REASONING_EFFORT)
from .ledger import Ledger

class ModelNotAllowed(Exception): pass
class DailyLimitReached(Exception): pass
class FatalProviderError(Exception):
    """Auth, billing, plan, or permission problem. Stop everything; never retry."""
class TransientError(Exception):
    """Network or server trouble that outlasted our retries. Safe to try again later."""

FATAL_WORDS = ("billing", "payment", "credit card", "upgrade", "plan", "quota exceeded for paid",
               "invalid api key", "unauthorized", "permission", "forbidden", "organization restricted")

def estimate_tokens(messages: list[dict]) -> int:
    """Deliberately high: about 3 characters per token, plus the full output allowance."""
    chars = sum(len(m.get("content") or "") for m in messages)
    return chars // 3 + 20 * len(messages) + MAX_COMPLETION_TOKENS

def _retry_seconds(headers: dict, body: str) -> float | None:
    if headers.get("retry-after"):
        try:
            return float(headers["retry-after"])
        except ValueError:
            pass
    m = re.search(r"try again in (?:(\d+)h)?(?:(\d+)m)?(?:([\d.]+)s)?", body)
    if m and any(m.groups()):
        h, mi, s = (float(g) if g else 0.0 for g in m.groups())
        return h * 3600 + mi * 60 + s
    return None

class GroqClient:
    def __init__(self, model: str, ledger: Ledger, sleep=time.sleep):
        if model not in ALLOWED_MODELS:
            raise ModelNotAllowed(f"{model} is not on the free-tier allowlist")
        self.model, self.ledger, self.sleep = model, ledger, sleep
        self.key = os.environ.get(API_KEY_ENV, "")
        if not self.key:
            raise FatalProviderError(f"{API_KEY_ENV} is not set")

    def _post(self, payload: dict):
        req = urllib.request.Request(
            f"{GROQ_BASE_URL}/chat/completions", data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json",
                     "User-Agent": USER_AGENT}, method="POST")
        start = time.time()
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read().decode(), time.time() - start
        except urllib.error.HTTPError as e:
            return e.code, {k.lower(): v for k, v in e.headers.items()}, e.read().decode(errors="replace"), time.time() - start

    def chat(self, messages: list[dict], run_key: str, purpose: str) -> dict:
        payload = {"model": self.model, "messages": messages,
                   "max_completion_tokens": MAX_COMPLETION_TOKENS, "temperature": 0.7}
        if self.model in AGENT_MODELS:
            payload["reasoning_effort"] = REASONING_EFFORT
        est = estimate_tokens(messages)
        transient_tries, limit_tries = 0, 0
        while True:
            gate = self.ledger.check(self.model, est)
            if gate["daily_blocked"]:
                raise DailyLimitReached(f"{self.model}: {gate['reason']}")
            if not gate["ok"]:
                self.sleep(gate["wait_s"]); continue
            try:
                status, headers, body, latency = self._post(payload)
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                self.ledger.record(model=self.model, run_key=run_key, purpose=purpose, usage=None,
                                   latency_s=0, status="network_error", http_status=0, headers={}, error=str(e))
                transient_tries += 1
                if transient_tries > 3:
                    raise TransientError(str(e))
                self.sleep(5 * transient_tries); continue
            rl_headers = {k: v for k, v in headers.items() if k.startswith("x-ratelimit") or k == "retry-after"}
            if status == 200:
                data = json.loads(body)
                msg = data["choices"][0]["message"]
                self.ledger.record(model=self.model, run_key=run_key, purpose=purpose, usage=data.get("usage"),
                                   latency_s=latency, status="ok", http_status=200, headers=rl_headers)
                return {"content": msg.get("content") or "", "reasoning": msg.get("reasoning") or "",
                        "usage": data.get("usage") or {}, "headers": rl_headers}
            low = body.lower()
            self.ledger.record(model=self.model, run_key=run_key, purpose=purpose, usage=None, latency_s=latency,
                               status="rate_limited" if status == 429 else "error", http_status=status,
                               headers=rl_headers, error=body)
            if status in (401, 402, 403) or (status != 429 and any(w in low for w in FATAL_WORDS)):
                raise FatalProviderError(f"HTTP {status}: {body[:300]}")
            if status == 429:
                wait = _retry_seconds(headers, body)
                if "per day" in low or "(tpd)" in low or "(rpd)" in low or (wait and wait > 120):
                    self.ledger.pause(self.model, time.time() + (wait or 3600), "provider daily limit")
                    raise DailyLimitReached(f"{self.model}: provider says daily limit reached")
                limit_tries += 1
                if limit_tries > 6:
                    raise TransientError("too many per-minute rate limits in a row")
                self.sleep(min(wait or 10.0, 120.0)); continue
            if status >= 500:
                transient_tries += 1
                if transient_tries > 3:
                    raise TransientError(f"HTTP {status}")
                self.sleep(5 * transient_tries); continue
            raise FatalProviderError(f"Unexpected HTTP {status}: {body[:300]}")

class MockClient:
    """Free, offline stand-in for testing. Replays a script of replies."""
    def __init__(self, model: str, ledger: Ledger, script):
        self.model, self.ledger, self.script = model, ledger, script
    def chat(self, messages, run_key, purpose):
        content = self.script(messages)
        usage = {"prompt_tokens": estimate_tokens(messages) - 1200, "completion_tokens": len(content) // 3}
        usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]
        self.ledger.record(model=self.model, run_key=run_key, purpose=purpose, usage=usage, latency_s=0.0,
                           status="ok", http_status=200, headers={"x-ratelimit-remaining-tokens": "mock"})
        return {"content": content, "reasoning": "", "usage": usage, "headers": {}}
