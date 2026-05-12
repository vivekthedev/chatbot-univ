import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

# Load env: project root first, then chatbot/ (so Streamlit cwd does not matter)
_root = Path(__file__).resolve().parent.parent
_chatbot = Path(__file__).resolve().parent
load_dotenv(_root / ".env")
load_dotenv(_chatbot / ".env")  # fills keys missing from root .env


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(f"Missing required environment variable: {key}")
    return val


# ── Database ───────────────────────────────────────────────────────────────────
DB_HOST = _require("DB_HOST")
DB_USER = _require("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")  # empty password is valid
DB_NAME = _require("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

_safe_pw = quote_plus(DB_PASSWORD) if DB_PASSWORD else ""
_auth = f"{DB_USER}:{_safe_pw}@" if DB_PASSWORD else f"{DB_USER}@"
DATABASE_URL = f"mysql+pymysql://{_auth}{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ── LLM ───────────────────────────────────────────────────────────────────────
LLM_PROVIDER    = _require("LLM_PROVIDER").strip().lower().replace("-", "_")  # e.g. google-genai → google_genai
LLM_MODEL       = _require("LLM_MODEL").strip()       # gemini-1.5-pro | gpt-4o | claude-3-5-sonnet ...
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))
# Optional: custom API root (OpenAI-compatible gateways, vLLM, LiteLLM proxy, Azure-style paths, etc.)
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "").strip() or None
# Google Gemini (when LLM_PROVIDER=google_genai); either env name works
GOOGLE_API_KEY = (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()

# ── Tavily ────────────────────────────────────────────────────────────────────
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")  # optional — Tavily tool disabled if empty
