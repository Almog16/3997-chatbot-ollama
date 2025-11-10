"""
@file server.py
@description This is the main entry point for the backend server.
It is responsible for:
- Initializing the FastAPI application.
- Configuring CORS middleware.
- Including the API routes defined in `src/routes.py`.
- Running the Uvicorn server for development.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.logger import initialize_logger
from src.routes import router

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

# Include API routes
app.include_router(router)

# --- Main Execution ---
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
