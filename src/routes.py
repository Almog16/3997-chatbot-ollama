"""
@file routes.py
@description This module defines the API routes for the backend server.
It includes endpoints for health checks, listing available models, and handling
both simple and agent-based chat requests. All routes are collected under a
single FastAPI APIRouter.
"""
import httpx
from fastapi import APIRouter
from starlette.responses import StreamingResponse

from src.config import ENABLE_AGENT_MODE, OLLAMA_TAGS_URL
from src.logger import LOGGER
from src.streaming import agent_stream_generator, ollama_stream_generator
from src.types import AgentChatRequest, ChatRequest

router = APIRouter()


@router.get("/api/health")
async def health_check() -> dict[str, str]:
    """
    Performs a health check on the API.

    This endpoint can be used to verify that the FastAPI server is running and
    to check the status of agent mode.

    Returns:
        A dictionary containing the health status, a message, and the current
        agent mode status ('enabled' or 'disabled').
    """
    return {
        "status": "ok",
        "message": "FastAPI server running",
        "agent_mode": "enabled" if ENABLE_AGENT_MODE else "disabled",
    }


@router.get("/api/models")
async def list_models() -> dict:
    """
    Retrieves the list of available models from the Ollama API.

    This endpoint fetches model tags from the local Ollama instance and returns
    them as a list. It includes error handling for network issues or if the
    Ollama server is not accessible.

    Returns:
        A dictionary containing a list of model objects, or an error message
        if the request fails.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(OLLAMA_TAGS_URL)
            response.raise_for_status()
            data = response.json()
            return {"models": data.get("models", [])}
    except Exception as e:
        LOGGER.error(f"Failed to fetch models: {e}")
        return {"models": [], "error": str(e)}


@router.post("/api/chat")
async def chat_endpoint(request: ChatRequest) -> StreamingResponse:
    """
    Handles standard chat requests by streaming directly from Ollama.

    This endpoint is a fallback for models that do not support tool calling
    or when agent mode is disabled. It streams the response directly from
    the Ollama API.

    Args:
        request: A `ChatRequest` object containing the model and messages.

    Returns:
        A `StreamingResponse` that streams the Ollama API's output.
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


@router.post("/api/agent/chat")
async def agent_chat_endpoint(request: AgentChatRequest) -> StreamingResponse:
    """
    Handles chat requests using the agent, with support for tool calling.

    This endpoint activates the agent to process user messages. It supports
    multi-step reasoning and tool execution, streaming the agent's state
    back to the client in real-time.

    Args:
        request: An `AgentChatRequest` object with model, messages, and
                 tool choice.

    Returns:
        A `StreamingResponse` that streams the agent's execution events.
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
