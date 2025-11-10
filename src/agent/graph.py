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
    """
    Creates and compiles a LangGraph agent workflow.

    This function constructs a stateful graph that defines the agent's
    behavior, including when to call the language model and when to execute
    tools. The graph is designed to handle multi-turn conversations and
    prevents infinite loops by setting a maximum number of iterations.

    Args:
        model_name: The name of the Ollama model to be used by the agent.

    Returns:
        A compiled `StateGraph` instance ready for execution. If no tools are
        available, it returns a simpler graph that bypasses the tool execution
        logic.
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
        """
        Invokes the language model with the current conversation state.

        This node is responsible for generating the AI's response, which may
        include tool calls. It also ensures that a system prompt is present
        at the beginning of the conversation.

        Args:
            state: The current state of the agent, including all messages.

        Returns:
            An updated `AgentState` with the model's response and an
            incremented iteration count.
        """
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
        """
        Executes the tools requested by the model in the previous turn.

        This node takes the tool calls from the latest AI message and runs
        them using the `ToolNode`. The results are then added back to the
        agent's state.

        Args:
            state: The current state of the agent, which should include an
                   AIMessage with tool calls.

        Returns:
            An updated `AgentState` with the results of the tool execution.
        """
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
        """
        Determines the next step in the agent's workflow.

        This conditional edge checks if the agent should continue to the tool
        execution node or end the conversation turn. It also enforces the
        maximum iteration limit to prevent infinite loops.

        Args:
            state: The current state of the agent.

        Returns:
            'tools' if the agent should execute tools, 'end' otherwise.
        """
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
    """
    Creates a simplified agent graph for when no tools are available.

    This function constructs a graph with only a single node for calling the
    language model. It is used as a fallback to ensure the agent can still
    provide responses even when no tools are configured.

    Args:
        llm: An initialized `ChatOllama` instance.

    Returns:
        A compiled `StateGraph` that only includes the model-calling node.
    """

    def call_model(state: AgentState) -> AgentState:
        """Invokes the language model without any tool-calling capabilities."""
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
    """
    Initializes a `ChatOllama` instance for use in non-agentic mode.

    This function provides a straightforward way to create a language model
    instance for simple chat functionalities, without the overhead of tool
    binding.

    Args:
        model_name: The name of the Ollama model to be used.

    Returns:
        An initialized `ChatOllama` instance.
    """
    return ChatOllama(
        model=model_name,
        temperature=0.7,
    )
