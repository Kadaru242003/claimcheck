"""Single source of truth for providers, models, and free-tier limits.

HARD RULE: total API cost is $0. Only Groq's free plan is allowed. No other provider,
no paid fallback. Any model not listed here is refused before a request is sent.

Limits are Groq's published free-plan limits (read 2026-09-26): per model, per
organization. Check the limits page in your Groq console; if yours are lower, lower
them here. Never raise them above what the console shows.
"""

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
API_KEY_ENV = "GROQ_API_KEY"
# Groq sits behind Cloudflare, which blocks Python's default identity ("Python-urllib")
# with HTTP 403, error code 1010. Every request identifies itself with this instead.
USER_AGENT = "claimcheck/0.1 (+https://github.com/Kadaru242003/claimcheck)"

# Role of each model. The judge must stay a different model family from the agents.
AGENT_MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]
JUDGE_MODEL = "qwen/qwen3.8-27b"
ALLOWED_MODELS = set(AGENT_MODELS) | {JUDGE_MODEL}

FREE_LIMITS = {  # per model
    "rpm": 30,        # requests per minute
    "rpd": 1_000,     # requests per day
    "tpm": 8_000,     # tokens per minute
    "tpd": 200_000,   # tokens per day
}
SAFETY_FRACTION = 0.90  # never plan to use more than 90% of any limit

# Per-call caps, so one call can never blow a per-minute budget.
MAX_COMPLETION_TOKENS = 1_200
MAX_PROMPT_TOKENS = 5_500          # history is trimmed to stay under this
REASONING_EFFORT = "low"           # GPT-OSS reasoning tokens count as output

# Agent loop
AGENT_MAX_TURNS = 6
TOOL_OUTPUT_CHARS = 1_500          # test output shown to the model is cut to this
FILE_READ_CHARS = 3_000

# Bump this whenever prompts or the protocol change. Results from a different version
# are never mixed in or reused.
PROMPT_VERSION = "v1"

# Planning estimates (tokens per run). Replaced by measured averages after the pilot.
ESTIMATED_TOKENS = {"blind": 1_500, "agent": 8_000, "judge": 1_200}
