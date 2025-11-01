from typing import Literal

from config import DEFAULT_MODEL
from pydantic import BaseModel, Field

# --- Pydantic Models for API Request/Response ---

class Message(BaseModel):
    """Represents a single message in the chat history."""

    role: str = Field(..., description="The role of the message sender (e.g., 'user', 'assistant', 'system').")
    content: str = Field(..., description="The text content of the message.")


class ChatRequest(BaseModel):
    """The request body for the /api/chat endpoint."""

    model: str = Field(DEFAULT_MODEL, description="The name of the model to use (e.g., 'llama3', 'mistral').")
    messages: list[Message] = Field(..., description="The full conversation history.")
    stream: bool = Field(default=True, description="Whether to stream the response back.")


class AgentChatRequest(BaseModel):
    """Request model for agent chat endpoint."""

    messages: list[dict]
    model: str = Field(default=DEFAULT_MODEL)
    tool_choice: Literal["auto", "required", "none"] = Field(default="auto")
    stream: bool = Field(default=True)
