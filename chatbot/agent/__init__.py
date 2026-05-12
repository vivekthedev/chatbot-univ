from typing import Any, AsyncGenerator

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage

from .graph import graph


def _chunk_content_to_text(content: Any) -> str:
    """
    Normalize LLM stream `content` to a plain string.

    Google GenAI and other providers may emit list-shaped content blocks
    (e.g. [{"type": "text", "text": "..."}]) instead of a single string.
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                t = block.get("text")
                if isinstance(t, str):
                    parts.append(t)
                elif t is not None:
                    parts.append(str(t))
            else:
                t = getattr(block, "text", None)
                if isinstance(t, str):
                    parts.append(t)
        return "".join(parts)
    return str(content)


async def stream_response(
    user_message: str,
    history: list[dict],  # [{"role": "user"|"assistant", "content": "..."}]
) -> AsyncGenerator[str, None]:
    """
    Convert Streamlit session history to LangChain messages,
    append the new user message, and stream token chunks from the graph.

    Yields string token chunks as they arrive from the LLM.
    Tool-call tokens are filtered out — only final answer text is yielded.
    Restricts streaming to the `agent` node's chat model to avoid unrelated streams.
    """
    lc_messages = [
        HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"])
        for m in history
    ]
    lc_messages.append(HumanMessage(content=user_message))

    async for event in graph.astream_events({"messages": lc_messages}, version="v2"):
        if event["event"] != "on_chat_model_stream":
            continue
        # Prefer streams from the `agent` node; some providers omit `langgraph_node`.
        node = (event.get("metadata") or {}).get("langgraph_node")
        if node is not None and node != "agent":
            continue
        chunk: AIMessageChunk = event["data"]["chunk"]
        if not chunk.tool_call_chunks:
            text = _chunk_content_to_text(chunk.content)
            if text:
                yield text
