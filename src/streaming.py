"""@file streaming.py
@description This module handles the core streaming logic for the application.
It contains two main generator functions: one for streaming responses directly
from the Ollama API (for simple chat) and another for streaming the complex,
multi-step output of the LangGraph agent.
"""
import json
from collections.abc import AsyncGenerator

import httpx
from langchain_core.messages import HumanMessage

from src.agent.graph import create_agent_graph, create_simple_llm
from src.config import ENABLE_AGENT_MODE, OLLAMA_API_BASE
from src.logger import LOGGER


async def ollama_stream_generator(request_data: dict) -> AsyncGenerator[str, None]:
    """Streams responses directly from the Ollama API.

    This generator function is used for backward compatibility, connecting to
    Ollama's standard chat endpoint and streaming the response line by line.

    Args:
    ----
        request_data: The payload to be sent to the Ollama API, including
                      the model name and messages.

    Yields:
    ------
        A string for each line of the response from the Ollama API.

    """
    LOGGER.info("Streaming request -> model=%s", request_data.get("model"))
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream(
                    "POST",
                    OLLAMA_API_BASE,
                    json=request_data
            ) as response:
                response.raise_for_status()

                async for chunk in response.aiter_lines():
                    if chunk:
                        try:
                            yield f"{chunk}\n"
                        except json.JSONDecodeError:
                            LOGGER.warning(f"Failed to decode JSON chunk: {chunk}")
                            continue
    except httpx.ConnectError:
        error_msg = f"Error: Could not connect to Ollama at {OLLAMA_API_BASE}"
        yield json.dumps({"error": error_msg}) + "\n"
    except httpx.HTTPStatusError as e:
        error_msg = f"Error: HTTP {e.response.status_code}"
        yield json.dumps({"error": error_msg}) + "\n"
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        yield json.dumps({"error": error_msg}) + "\n"


async def agent_stream_generator(  # noqa: C901, PLR0912
        messages: list[dict],
        model_name: str,
        tool_choice: str,
) -> AsyncGenerator[str, None]:
    """Streams responses from the agent, including tool calls and reasoning steps.

    This function orchestrates the agent's workflow, streaming each step of
    the process, from tool calls and results to the final message. It can
    operate in either agent mode or a simple LLM mode if tools are not required.

    Args:
    ----
        messages: A list of messages in the current chat session.
        model_name: The name of the language model to use.
        tool_choice: The user's preference for using tools ('auto', 'none', etc.).

    Yields:
    ------
        A JSON string for each event in the agent's execution, such as
        status updates, tool calls, tool results, and the final message.

    """
    try:
        # Convert messages to LangChain format
        lc_messages = [HumanMessage(content=msg["content"]) for msg in messages if msg["role"] == "user"]

        # Decide whether to use agent or simple mode
        use_agent = tool_choice != "none" and ENABLE_AGENT_MODE

        if use_agent:
            # Stream with agent and tools
            yield json.dumps({
                "type": "status",
                "content": "Agent mode activated"
            }) + "\n"

            # Create agent graph
            agent = create_agent_graph(model_name)

            # Initial state
            initial_state = {
                "messages": lc_messages,
                "reasoning_steps": [],
                "tool_results": [],
                "iteration_count": 0,
            }

            # Stream agent execution
            async for event in agent.astream(initial_state):
                for node_name, node_output in event.items():

                    # Stream tool calls
                    if node_name == "agent":
                        messages_output = node_output.get("messages", [])
                        if messages_output:
                            last_msg = messages_output[-1]

                            # Check for tool calls
                            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                                for tool_call in last_msg.tool_calls:
                                    yield json.dumps({
                                        "type": "tool_call",
                                        "tool": tool_call["name"],
                                        "args": tool_call["args"],
                                    }) + "\n"

                    # Stream tool results
                    elif node_name == "tools":
                        tool_results = node_output.get("tool_results", [])
                        if tool_results:
                            latest_result = tool_results[-1]
                            yield json.dumps({
                                "type": "tool_result",
                                "tool": latest_result["tool"],
                                "result": latest_result["result"][:500],  # Truncate long results
                            }) + "\n"

            # Get final state
            final_state = agent.invoke(initial_state)
            final_messages = final_state.get("messages", [])

            if final_messages:
                final_response = final_messages[-1]
                if hasattr(final_response, "content"):
                    # Stream final response
                    yield json.dumps({
                        "type": "message",
                        "content": final_response.content,
                    }) + "\n"

        else:
            # Simple mode without tools
            yield json.dumps({
                "type": "status",
                "content": "Simple chat mode"
            }) + "\n"

            llm = create_simple_llm(model_name)
            response = llm.invoke(lc_messages)

            yield json.dumps({
                "type": "message",
                "content": response.content,
            }) + "\n"

        # Done
        yield json.dumps({"type": "done", "complete": True}) + "\n"

    except Exception as e:
        LOGGER.error(f"Agent error: {e}")
        yield json.dumps({
            "type": "error",
            "content": f"Agent error: {e!s}"
        }) + "\n"
