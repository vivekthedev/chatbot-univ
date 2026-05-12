from langchain.chat_models import init_chat_model
from config import LLM_PROVIDER, LLM_MODEL, LLM_TEMPERATURE


def get_llm():
    """
    Return a streaming ChatModel based on .env LLM_PROVIDER + LLM_MODEL.

    Supported providers (set LLM_PROVIDER in .env):
        google_genai  → requires GOOGLE_API_KEY
        openai        → requires OPENAI_API_KEY
        anthropic     → requires ANTHROPIC_API_KEY
        groq          → requires GROQ_API_KEY
        ollama        → no key needed, local server

    Switching providers requires only .env changes — no code edits.
    """
    return init_chat_model(
        model=LLM_MODEL,
        model_provider=LLM_PROVIDER,
        temperature=LLM_TEMPERATURE,
        streaming=True,
    )
