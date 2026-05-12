import os
from pathlib import Path
from dotenv import load_dotenv

# Load the root-level .env (one level up from chatbot/)
load_dotenv(Path(__file__).parent.parent / ".env")


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(f"Missing required environment variable: {key}")
    return val


# ── Database ───────────────────────────────────────────────────────────────────
DB_HOST     = _require("DB_HOST")
DB_USER     = _require("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")   # empty password is valid
DB_NAME     = _require("DB_NAME")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# ── LLM ───────────────────────────────────────────────────────────────────────
LLM_PROVIDER    = _require("LLM_PROVIDER")    # google_genai | openai | anthropic | groq
LLM_MODEL       = _require("LLM_MODEL")       # gemini-1.5-pro | gpt-4o | claude-3-5-sonnet ...
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))

# ── Tavily ────────────────────────────────────────────────────────────────────
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")  # optional — Tavily tool disabled if empty
