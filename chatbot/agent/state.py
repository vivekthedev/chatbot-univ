from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    """
    The state that flows through the LangGraph agent.

    messages: accumulated conversation + tool call/result turns.
    add_messages reducer appends new messages instead of replacing,
    which is what enables the agent → tools → agent loop to work correctly.
    """
    messages: Annotated[list[BaseMessage], add_messages]
