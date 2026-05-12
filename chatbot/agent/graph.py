from langgraph.graph import StateGraph, END

from .state import GraphState
from .nodes import agent_node, tool_node


def should_continue(state: GraphState) -> str:
    """
    Router: if the last AIMessage has pending tool calls → execute tools.
    Otherwise → end and stream the final response to the user.
    """
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


def build_graph():
    g = StateGraph(GraphState)

    g.add_node("agent", agent_node)
    g.add_node("tools", tool_node)

    g.set_entry_point("agent")

    # After agent: either call tools or finish
    g.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", END: END},
    )

    # After tools always return to agent for synthesis / further reasoning
    g.add_edge("tools", "agent")

    return g.compile()


# Module-level graph instance — imported by agent/__init__.py
graph = build_graph()
