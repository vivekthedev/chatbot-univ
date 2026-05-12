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
    """
    lc_messages = [
        HumanMessage(content=m["content"]) if m["role"] == "user"
        else AIMessage(content=m["content"])
        for m in history
    ]
    lc_messages.append(HumanMessage(content=user_message))

    async for event in graph.astream_events({"messages": lc_messages}, version="v2"):
        if event["event"] == "on_chat_model_stream":
            chunk: AIMessageChunk = event["data"]["chunk"]
            # Skip tool-call tokens; only yield visible answer text
            if chunk.content and not chunk.tool_call_chunks:
                yield chunk.content
