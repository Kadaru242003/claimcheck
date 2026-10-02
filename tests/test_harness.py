"""Tests for the $0 safeguards and the protocol. No network: the HTTP call is faked."""
import json, time
import pytest
from claimcheck import providers
from claimcheck.config import FREE_LIMITS, SAFETY_FRACTION
from claimcheck.ledger import Ledger
from claimcheck.providers import GroqClient, DailyLimitReached, FatalProviderError, ModelNotAllowed
from claimcheck.agent import parse_json_reply, classify
from claimcheck.store import Store

MODEL = "openai/gpt-oss-20b"
OK_BODY = json.dumps({"choices": [{"message": {"content": "{}"}}],
                      "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}})

@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    return Ledger(tmp_path / "l.sqlite")

def client(ledger, responses, sleeps):
    c = GroqClient(MODEL, ledger, sleep=lambda s: sleeps.append(s))
    posts = []
    def fake_post(payload):
        posts.append(payload)
        return responses.pop(0)
    c._post = fake_post
    return c, posts

MSG = [{"role": "user", "content": "hi"}]

def test_refuses_models_not_on_allowlist(env):
    with pytest.raises(ModelNotAllowed):
        GroqClient("gpt-4o", env)

def test_daily_token_cap_blocks_before_sending(env):
    cap = int(FREE_LIMITS["tpd"] * SAFETY_FRACTION)
    env.record(model=MODEL, run_key="x", purpose="t", usage={"total_tokens": cap - 100},
               latency_s=0, status="ok", http_status=200, headers={})
    c, posts = client(env, [], [])
    with pytest.raises(DailyLimitReached):
        c.chat(MSG, "k", "t")
    assert posts == []  # nothing was sent

def test_daily_request_cap_blocks_before_sending(env):
    for _ in range(int(FREE_LIMITS["rpd"] * SAFETY_FRACTION)):
        env.record(model=MODEL, run_key="x", purpose="t", usage={"total_tokens": 1},
                   latency_s=0, status="ok", http_status=200, headers={})
    c, posts = client(env, [], [])
    with pytest.raises(DailyLimitReached):
        c.chat(MSG, "k", "t")
    assert posts == []

def test_per_minute_cap_waits_instead_of_sending(env, monkeypatch):
    cap = int(FREE_LIMITS["tpm"] * SAFETY_FRACTION)
    env.record(model=MODEL, run_key="x", purpose="t", usage={"total_tokens": cap},
               latency_s=0, status="ok", http_status=200, headers={})
    sleeps = []
    c, posts = client(env, [(200, {}, OK_BODY, 0.1)], sleeps)
    real_check = env.check
    calls = {"n": 0}
    def check_then_clear(model, est, now=None):
        calls["n"] += 1
        return real_check(model, est, now=time.time() + (61 if calls["n"] > 1 else 0))
    monkeypatch.setattr(env, "check", check_then_clear)
    c.chat(MSG, "k", "t")
    assert sleeps and sleeps[0] > 0 and len(posts) == 1

def test_minute_429_waits_and_retries(env):
    sleeps = []
    c, posts = client(env, [(429, {"retry-after": "7"}, "Rate limit reached on requests per minute (RPM)", 0.1),
                            (200, {"x-ratelimit-remaining-requests": "990"}, OK_BODY, 0.1)], sleeps)
    out = c.chat(MSG, "k", "t")
    assert sleeps == [7.0] and len(posts) == 2 and out["usage"]["total_tokens"] == 150

def test_daily_429_pauses_model_and_stops(env):
    body = "Rate limit reached for model on tokens per day (TPD): Limit 200000, Used 199336. Please try again in 6m11.52s."
    c, posts = client(env, [(429, {}, body, 0.1)], [])
    with pytest.raises(DailyLimitReached):
        c.chat(MSG, "k", "t")
    c2, posts2 = client(env, [], [])
    with pytest.raises(DailyLimitReached):  # still paused: blocked before sending
        c2.chat(MSG, "k", "t")
    assert len(posts) == 1 and posts2 == []

@pytest.mark.parametrize("status,body", [(401, "Invalid API Key"), (402, "Payment required"),
                                         (403, "organization restricted"), (400, "Please upgrade your plan to use this model")])
def test_billing_or_auth_errors_stop_everything_without_retry(env, status, body):
    c, posts = client(env, [(status, {}, body, 0.1)], [])
    with pytest.raises(FatalProviderError):
        c.chat(MSG, "k", "t")
    assert len(posts) == 1

def test_every_call_is_recorded_with_headers(env):
    c, _ = client(env, [(200, {"x-ratelimit-remaining-tokens": "7850", "content-type": "json"}, OK_BODY, 0.2)], [])
    c.chat(MSG, "k", "t")
    rows = env.calls(MODEL)
    assert len(rows) == 1 and rows[0]["total_tokens"] == 150
    assert json.loads(rows[0]["headers"]) == {"x-ratelimit-remaining-tokens": "7850"}

def test_request_is_capped_and_uses_low_reasoning(env):
    c, posts = client(env, [(200, {}, OK_BODY, 0.1)], [])
    c.chat(MSG, "k", "t")
    assert posts[0]["max_completion_tokens"] == 1200 and posts[0]["reasoning_effort"] == "low"

def test_json_reply_parsing():
    assert parse_json_reply('```json\n{"action": "run_tests"}\n```') == {"action": "run_tests"}
    assert parse_json_reply('Sure! {"status": "success", "code": "x = {1: 2}"} done')["status"] == "success"
    assert parse_json_reply("no json here") is None

def test_classification():
    assert classify("success", False, []) == "false_success"
    assert classify("failure", False, []) == "true_failure"
    assert classify("success", True, ["line 1: uses ._exit"]) == "flagged"
    assert classify("unclear", True, []) == "unclear"

def test_store_ignores_line_cut_off_by_crash(tmp_path):
    s = Store(tmp_path)
    s.save({"key": "a"}, [])
    with open(s.runs_path, "a") as f:
        f.write('{"key": "b", "tok')  # crash mid-write
    assert s.done_keys() == {"a"}

def test_requests_identify_themselves_not_as_python_urllib(env, monkeypatch):
    """Cloudflare blocks Python's default User-Agent with HTTP 403 (error code 1010)."""
    seen = {}
    class FakeResp:
        status = 200
        headers = {}
        def read(self): return OK_BODY.encode()
        def __enter__(self): return self
        def __exit__(self, *a): return False
    def fake_urlopen(req, timeout=None):
        seen["ua"] = req.get_header("User-agent")
        seen["url"] = req.full_url
        return FakeResp()
    monkeypatch.setattr(providers.urllib.request, "urlopen", fake_urlopen)
    GroqClient(MODEL, env).chat(MSG, "k", "t")
    assert seen["ua"].startswith("claimcheck/") and "urllib" not in seen["ua"].lower()
    assert seen["url"].startswith("https://api.groq.com/")
