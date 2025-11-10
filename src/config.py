"""
Configuration management for the Ollama Chatbot Backend.

This module reads settings from environment variables and provides
default values for easy setup. It centralizes all configuration
parameters to avoid hardcoding them in the application logic.
"""
import os

# --- Model Configuration ---

# The default model to use for chat requests if not specified by the client.
# This can be overridden by setting the DEFAULT_MODEL environment variable.
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "qwen3:8b")

# --- Environment Variables ---

# Get Ollama connection details from environment variables
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost")
OLLAMA_PORT = int(os.environ.get("OLLAMA_PORT", 11434))

# Construct the base URL for the Ollama API
OLLAMA_API_BASE = f"{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat"
OLLAMA_TAGS_URL = f"{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags"

# --- Feature Flags ---

# Enable or disable agent mode (tool calling)
# Set to "true" or "1" to enable
ENABLE_AGENT_MODE = os.environ.get("ENABLE_AGENT_MODE", "true").lower() in ("true", "1")
