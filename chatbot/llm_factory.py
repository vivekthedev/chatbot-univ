from typing import Any

from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GOOGLE_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_PROVIDER, LLM_TEMPERATURE


def get_llm():
    """
    Return a streaming ChatModel based on .env LLM_PROVIDER + LLM_MODEL.

    Google GenAI is constructed explicitly with ``api_key`` from ``GOOGLE_API_KEY``
    or ``GEMINI_API_KEY`` so the key is never dropped by factory indirection.

    Other providers use ``init_chat_model``; optional ``LLM_BASE_URL`` is passed
    as ``base_url`` for OpenAI-compatible gateways.
    """
    if LLM_PROVIDER == "google_genai":
        if not GOOGLE_API_KEY:
            raise EnvironmentError(
                "Missing GOOGLE_API_KEY or GEMINI_API_KEY. "
                "Set one in .env (project root or chatbot/) when LLM_PROVIDER=google_genai."
            )
        return ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            streaming=True,
            api_key=GOOGLE_API_KEY,
        )

    kwargs: dict[str, Any] = {
        "model": LLM_MODEL,
        "model_provider": LLM_PROVIDER,
        "temperature": LLM_TEMPERATURE,
        "streaming": True,
    }
    if LLM_BASE_URL:
        kwargs["base_url"] = LLM_BASE_URL
    return init_chat_model(**kwargs)
