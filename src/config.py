# --- Configuration ---
import os

OLLAMA_API_BASE = "http://localhost:11434/api/chat"
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:8b")
ENABLE_AGENT_MODE = os.getenv("ENABLE_TOOLS", "true").lower() == "true"
