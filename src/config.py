# --- Configuration ---
import os

# The base URL for the Ollama API's chat endpoint. This is the endpoint
# the application will connect to for standard chat functionality.
OLLAMA_API_BASE = "http://localhost:11434/api/chat"

# The default language model to be used by the application. This can be
# overridden by setting the `OLLAMA_MODEL` environment variable.
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:8b")

# A flag to enable or disable the agent's tool-calling capabilities. When
# set to `true`, the agent will be able to use its tools. This can be
# controlled by the `ENABLE_TOOLS` environment variable.
ENABLE_AGENT_MODE = os.getenv("ENABLE_TOOLS", "true").lower() == "true"
