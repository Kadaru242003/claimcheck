"""Ledger of every API call: requests, tokens, latency, rate-limit headers, errors.

Windows are rolling (last 60 s, last 24 h) rather than calendar days. That is the
conservative choice: it never assumes a limit has reset before it actually has.

Before each call, `check()` answers: can this call fit under 90% of every limit?
  - If only a per-minute limit is in the way, it says how long to wait.
  - If a per-day limit is in the way, it says the model is done for now.
"""
import contextlib, json, sqlite3, threading, time
from pathlib import Path
from .config import FREE_LIMITS, SAFETY_FRACTION

MINUTE, DAY = 60.0, 86_400.0

class Ledger:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        with self._conn() as c:
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("""CREATE TABLE IF NOT EXISTS calls (
                ts REAL, model TEXT, run_key TEXT, purpose TEXT,
                prompt_tokens INTEGER, completion_tokens INTEGER, reasoning_tokens INTEGER,
                total_tokens INTEGER, latency_s REAL, status TEXT, http_status INTEGER,
                headers TEXT, error TEXT)""")
            c.execute("""CREATE TABLE IF NOT EXISTS pauses (
                model TEXT PRIMARY KEY, until_ts REAL, reason TEXT)""")

    @contextlib.contextmanager
    def _conn(self):
        """Open a connection, commit on success, and ALWAYS close it.
        (sqlite3's own `with` block commits but never closes, which leaks one
        file handle per call until the process hits the open-file limit.)"""
        conn = sqlite3.connect(self.path, timeout=30)
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    # ---------- recording ----------
    def record(self, *, model, run_key, purpose, usage, latency_s, status, http_status, headers, error=""):
        usage = usage or {}
        details = usage.get("completion_tokens_details") or {}
        row = (time.time(), model, run_key, purpose,
               int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0)),
               int(details.get("reasoning_tokens", 0) or 0), int(usage.get("total_tokens", 0)),
               float(latency_s), status, int(http_status or 0), json.dumps(headers or {}), error[:500])
        with self._lock, self._conn() as c:
            c.execute("INSERT INTO calls VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", row)

    def pause(self, model: str, until_ts: float, reason: str):
        with self._lock, self._conn() as c:
            c.execute("INSERT OR REPLACE INTO pauses VALUES (?,?,?)", (model, until_ts, reason))

    # ---------- reading ----------
    def usage(self, model: str, window: float, now: float | None = None) -> dict:
        now = now or time.time()
        with self._conn() as c:
            req, tok = c.execute(
                "SELECT COUNT(*), COALESCE(SUM(total_tokens),0) FROM calls WHERE model=? AND ts>=?",
                (model, now - window)).fetchone()
        return {"requests": req, "tokens": tok}

    def oldest_in_window(self, model: str, window: float, now: float) -> float | None:
        with self._conn() as c:
            row = c.execute("SELECT MIN(ts) FROM calls WHERE model=? AND ts>=?", (model, now - window)).fetchone()
        return row[0]

    def paused_until(self, model: str) -> tuple[float, str]:
        with self._conn() as c:
            row = c.execute("SELECT until_ts, reason FROM pauses WHERE model=?", (model,)).fetchone()
        return (row[0], row[1]) if row and row[0] > time.time() else (0.0, "")

    def check(self, model: str, est_tokens: int, now: float | None = None) -> dict:
        """Return {"ok": bool, "wait_s": float, "daily_blocked": bool, "reason": str}."""
        now = now or time.time()
        until, why = self.paused_until(model)
        if until:
            return {"ok": False, "wait_s": until - now, "daily_blocked": True, "reason": f"paused by provider: {why}"}
        cap = lambda k: int(FREE_LIMITS[k] * SAFETY_FRACTION)
        day, minute = self.usage(model, DAY, now), self.usage(model, MINUTE, now)
        if day["requests"] + 1 > cap("rpd"):
            return {"ok": False, "wait_s": 0, "daily_blocked": True, "reason": "requests/day at 90% cap"}
        if day["tokens"] + est_tokens > cap("tpd"):
            return {"ok": False, "wait_s": 0, "daily_blocked": True, "reason": "tokens/day at 90% cap"}
        if minute["requests"] + 1 > cap("rpm") or minute["tokens"] + est_tokens > cap("tpm"):
            oldest = self.oldest_in_window(model, MINUTE, now) or now
            return {"ok": False, "wait_s": max(1.0, oldest + MINUTE - now + 0.5), "daily_blocked": False,
                    "reason": "per-minute cap"}
        return {"ok": True, "wait_s": 0, "daily_blocked": False, "reason": "ok"}

    def summary(self, model: str) -> dict:
        d = self.usage(model, DAY)
        cap = lambda k: int(FREE_LIMITS[k] * SAFETY_FRACTION)
        return {"requests_24h": d["requests"], "tokens_24h": d["tokens"],
                "requests_left": max(0, cap("rpd") - d["requests"]),
                "tokens_left": max(0, cap("tpd") - d["tokens"])}

    def calls(self, model: str | None = None) -> list[dict]:
        q = "SELECT ts, model, run_key, purpose, prompt_tokens, completion_tokens, reasoning_tokens, total_tokens, latency_s, status, http_status, headers, error FROM calls"
        args = ()
        if model:
            q += " WHERE model=?"; args = (model,)
        cols = ["ts", "model", "run_key", "purpose", "prompt_tokens", "completion_tokens", "reasoning_tokens",
                "total_tokens", "latency_s", "status", "http_status", "headers", "error"]
        with self._conn() as c:
            return [dict(zip(cols, r)) for r in c.execute(q, args).fetchall()]
