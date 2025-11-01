"""LangGraph Agent Workflow
Defines the agent execution graph with tool calling capabilities
"""

import os
from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from logger import LOGGER

from src.agent.prompts import get_system_prompt
from src.agent.state import AgentState
from src.agent.tools import get_tools

# Maximum iterations to prevent infinite loops
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "2"))


def create_agent_graph(model_name: str = "llama3.1") -> StateGraph:
    """Create the LangGraph workflow for the agent.

    Args:
    ----
        model_name: Name of the Ollama model to use

    Returns:
    -------
        Compiled StateGraph ready for execution

    """
    # Initialize the LLM with faster settings
    llm = ChatOllama(
        model=model_name,
        temperature=0.7,
        num_predict=512,  # Limit response length for speed
    )

    # Get all available tools
    tools = get_tools()

    if not tools:
        # No tools available, return simple LLM
        LOGGER.info("No tools available. Agent will work in simple mode.")
        return create_simple_graph(llm)

    llm_with_tools = llm.bind_tools(tools)

    # Create tool node for executing tools
    tool_node = ToolNode(tools)

    # Define graph nodes
    def call_model(state: AgentState) -> AgentState:
        """Call the LLM with current state."""
        messages = state["messages"]

        # Add system prompt if not present
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            messages = [SystemMessage(content=get_system_prompt())] + messages

        # Call the model
        response = llm_with_tools.invoke(messages)

        # Increment iteration count
        iteration_count = state.get("iteration_count", 0) + 1

        return {
            "messages": [response],
            "iteration_count": iteration_count,
            "reasoning_steps": state.get("reasoning_steps", []),
            "tool_results": state.get("tool_results", []),
        }

    def execute_tools(state: AgentState) -> AgentState:
        """Execute the tools requested by the model."""
        # Get the last message (should be AIMessage with tool calls)
        last_message = state["messages"][-1]

        # Execute tools using ToolNode
        tool_outputs = tool_node.invoke({"messages": [last_message]})

        # Store tool results for transparency
        tool_results = state.get("tool_results", [])
        for tool_msg in tool_outputs["messages"]:
            if isinstance(tool_msg, ToolMessage):
                tool_results.append({
                    "tool": tool_msg.name,
                    "result": tool_msg.content,
                })

        return {
            "messages": tool_outputs["messages"],
            "tool_results": tool_results,
            "reasoning_steps": state.get("reasoning_steps", []),
            "iteration_count": state.get("iteration_count", 0),
        }

    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        """Determine if we should continue or end the workflow."""
        messages = state["messages"]
        last_message = messages[-1]
        iteration_count = state.get("iteration_count", 0)

        # Check if we've exceeded max iterations
        if iteration_count >= MAX_ITERATIONS:
            return "end"

        # If the last message has tool calls, continue to tools
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tools"

        # Otherwise, end
        return "end"

    # Build the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", execute_tools)

    # Set entry point
    workflow.set_entry_point("agent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        },
    )

    # After tools, always go back to agent
    workflow.add_edge("tools", "agent")

    # Compile the graph
    return workflow.compile()


def create_simple_graph(llm: ChatOllama) -> StateGraph:
    """Create a simple graph without tools (fallback when no plugins enabled).

    Args:
    ----
        llm: ChatOllama instance

    Returns:
    -------
        Compiled StateGraph

    """

    def call_model(state: AgentState) -> AgentState:
        """Call the LLM without tools."""
        messages = state["messages"]

        # Add system prompt if not present
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            messages = [SystemMessage(content=get_system_prompt())] + messages

        response = llm.invoke(messages)

        return {
            "messages": [response],
            "iteration_count": state.get("iteration_count", 0) + 1,
            "reasoning_steps": state.get("reasoning_steps", []),
            "tool_results": state.get("tool_results", []),
        }

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)

    return workflow.compile()


def create_simple_llm(model_name: str = "llama3.1") -> ChatOllama:
    """Create a simple LLM without tools for non-agent mode.

    Args:
    ----
        model_name: Name of the Ollama model to use

    Returns:
    -------
        ChatOllama instance

    """
    return ChatOllama(
        model=model_name,
        temperature=0.7,
    )
