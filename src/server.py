"""Enhanced Ollama Chatbot Backend with Agent Capabilities
Supports both simple chat and agent mode with tool calling
"""

import json
from collections.abc import AsyncGenerator

import httpx
from config import ENABLE_AGENT_MODE, OLLAMA_API_BASE
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from logger import LOGGER, initialize_logger
from starlette.responses import StreamingResponse

from src.agent.graph import create_agent_graph, create_simple_llm
from src.types import AgentChatRequest, ChatRequest

# --- Init Logger ---
initialize_logger()

# --- FastAPI Setup ---
app = FastAPI(title="Ollama Chatbot Backend with Agents", version="2.0.0")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Endpoint Handlers ---

@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "FastAPI server running",
        "agent_mode": "enabled" if ENABLE_AGENT_MODE else "disabled",
    }


@app.get("/api/models")
async def list_models() -> dict:
    """Get available Ollama models."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags")
            response.raise_for_status()
            data = response.json()
            return {"models": data.get("models", [])}
    except Exception as e:
        LOGGER.error(f"Failed to fetch models: {e}")
        return {"models": [], "error": str(e)}


async def ollama_stream_generator(request_data: dict) -> AsyncGenerator[str, None]:
    """Generator for direct Ollama API streaming (backward compatible)."""
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


async def agent_stream_generator( # noqa: C901, PLR0912
        messages: list[dict],
        model_name: str,
        tool_choice: str,
) -> AsyncGenerator[str, None]:
    """Generator for agent mode with tool calling support.
    Streams reasoning steps, tool calls, and final responses.
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


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest) -> StreamingResponse:
    """Uses direct Ollama API streaming.
    Fallback for models that does not support tool call and agent mode.
    """
    LOGGER.info(
        "/api/chat request received | model=%s | messages=%s",
        request.model,
        len(request.messages),
    )
    ollama_payload = request.model_dump()
    return StreamingResponse(
        ollama_stream_generator(ollama_payload),
        media_type="application/json"
    )


@app.post("/api/agent/chat")
async def agent_chat_endpoint(request: AgentChatRequest) -> StreamingResponse:
    """Enhanced chat endpoint with agent capabilities.
    Supports tool calling and multistep reasoning.
    """
    LOGGER.info(
        "/api/agent/chat request received | model=%s | tool_choice=%s | messages=%s",
        request.model,
        request.tool_choice,
        len(request.messages),
    )
    return StreamingResponse(
        agent_stream_generator(
            messages=request.messages,
            model_name=request.model,
            tool_choice=request.tool_choice,
        ),
        media_type="application/json"
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
