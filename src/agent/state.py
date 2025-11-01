"""Agent State Management
Defines the state structure for the LangGraph agent workflow
"""

from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State for the agent workflow.

    Attributes
    ----------
        messages: Conversation history with add_messages reducer for appending
        reasoning_steps: List of reasoning/thinking steps for transparency
        tool_results: Results from tool executions
        iteration_count: Track iterations to prevent infinite loops

    """

    messages: Annotated[list[AnyMessage], add_messages]
    reasoning_steps: list[str]
    tool_results: list[dict]
    iteration_count: int
