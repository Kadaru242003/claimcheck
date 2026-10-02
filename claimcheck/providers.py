"""Model clients.

GroqClient is the only client that sends network requests, and only to GROQ_BASE_URL,
only for models in ALLOWED_MODELS. There is no fallback to any other provider.

MockClient sends nothing and costs nothing. It exists to test the harness.
"""
import json, os, re, time, urllib.error, urllib.request
from .config import (GROQ_BASE_URL, API_KEY_ENV, USER_AGENT, ALLOWED_MODELS, AGENT_MODELS,
                     MAX_COMPLETION_TOKENS, REASONING_EFFORT, PARSE_RETRIES, MAX_CALL_TOKENS)
from .ledger import Ledger

class ModelNotAllowed(Exception): pass
class DailyLimitReached(Exception): pass
class FatalProviderError(Exception):
    """Auth, billing, plan, or permission problem. Stop everything; never retry."""
class TransientError(Exception):
    """Network or server trouble that outlasted our retries. Safe to try again later."""
class ModelOutputError(Exception):
    """The provider could not parse what the model generated (e.g. a malformed tool call).
    This is model behavior, not an account problem: the caller records it and moves on."""
    def __init__(self, generation: str):
        super().__init__(generation); self.generation = generation

PARSE_FAILURE_CODES = ("output_parse_failed", "tool_use_failed", "json_validate_failed")

FATAL_WORDS = ("billing", "payment", "credit card", "upgrade", "plan", "quota exceeded for paid",
               "invalid api key", "unauthorized", "permission", "forbidden", "organization restricted")

def estimate_tokens(messages: list[dict], tools: list | None = None) -> int:
    """Deliberately high: about 3 characters per token, plus the full output allowance."""
    chars = sum(len(m.get("content") or "") + len(json.dumps(m.get("tool_calls") or "")) for m in messages)
    chars += len(json.dumps(tools)) if tools else 0
    return chars // 3 + 20 * len(messages) + MAX_COMPLETION_TOKENS

def _error_fields(body: str) -> tuple[str, str, str]:
    """(code, message, failed_generation) from a provider error body. Fatal-word checks look
    only at code and message, never at failed_generation, which is the model's own text."""
    try:
        err = json.loads(body).get("error") or {}
        return (str(err.get("code") or ""), str(err.get("message") or ""), str(err.get("failed_generation") or ""))
    except (ValueError, AttributeError):
        return ("", body[:500], "")

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

    def chat(self, messages: list[dict], run_key: str, purpose: str, tools: list | None = None) -> dict:
        payload = {"model": self.model, "messages": messages,
                   "max_completion_tokens": MAX_COMPLETION_TOKENS, "temperature": 0.7}
        if self.model in AGENT_MODELS:
            payload["reasoning_effort"] = REASONING_EFFORT
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        est = estimate_tokens(messages, tools)
        if est > MAX_CALL_TOKENS:
            # Could never fit under the per-minute cap: waiting would loop forever.
            raise TransientError(f"call too large ({est} est. tokens > {MAX_CALL_TOKENS}); trim the prompt")
        transient_tries, limit_tries, parse_tries = 0, 0, 0
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
                        "tool_calls": msg.get("tool_calls") or [],
                        "finish_reason": data["choices"][0].get("finish_reason") or "",
                        "usage": data.get("usage") or {}, "headers": rl_headers}
            code, message, generation = _error_fields(body)
            if status == 400 and code in PARSE_FAILURE_CODES:
                # Count the full estimate against the budget: the provider likely counted it too.
                self.ledger.record(model=self.model, run_key=run_key, purpose=purpose,
                                   usage={"total_tokens": est}, latency_s=latency, status="parse_failed",
                                   http_status=status, headers=rl_headers, error=f"{code}: {generation[:300]}")
                parse_tries += 1
                if parse_tries > PARSE_RETRIES:
                    raise ModelOutputError(generation)
                continue
            self.ledger.record(model=self.model, run_key=run_key, purpose=purpose, usage=None, latency_s=latency,
                               status="rate_limited" if status == 429 else "error", http_status=status,
                               headers=rl_headers, error=body)
            low = (code + " " + message).lower()
            if status in (401, 402, 403) or (status != 429 and any(w in low for w in FATAL_WORDS)):
                raise FatalProviderError(f"HTTP {status}: {code} {message[:300]}")
            if status == 429:
                body = message or body
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
    def chat(self, messages, run_key, purpose, tools=None):
        out = self.script(messages, tools)
        content, tool_calls = (out, []) if isinstance(out, str) else ("", out)
        usage = {"prompt_tokens": estimate_tokens(messages, tools) - 1200, "completion_tokens": len(str(out)) // 3}
        usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]
        self.ledger.record(model=self.model, run_key=run_key, purpose=purpose, usage=usage, latency_s=0.0,
                           status="ok", http_status=200, headers={"x-ratelimit-remaining-tokens": "mock"})
        return {"content": content, "reasoning": "", "tool_calls": tool_calls, "finish_reason": "stop",
                "usage": usage, "headers": {}}
