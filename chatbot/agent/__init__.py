from typing import AsyncGenerator

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage

from .graph import graph


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
        if chunk.content and not chunk.tool_call_chunks:
            yield chunk.content
