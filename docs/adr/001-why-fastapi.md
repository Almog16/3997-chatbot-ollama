# ADR 001: Why FastAPI was Chosen for the Backend

## Status

Accepted

## Context

The project required a modern, high-performance Python web framework to serve as the backend for the chatbot application. The primary responsibilities of the backend are to handle API requests, manage communication with the Ollama service, and stream responses back to the client in real-time.

Key requirements included:
- Asynchronous support for efficient I/O operations (streaming, API calls).
- Automatic generation of interactive API documentation.
- Data validation using modern Python type hints.
- A clean, intuitive syntax for defining routes.

## Decision

We decided to use **FastAPI** as the web framework for the backend.

## Consequences

### Positive:
- **High Performance:** FastAPI is built on top of Starlette and Pydantic, making it one of the fastest Python frameworks available, which is ideal for I/O-bound operations like streaming.
- **Asynchronous by Default:** `async` and `await` are first-class citizens, which simplified the implementation of the streaming endpoints and communication with Ollama.
- **Automatic Docs:** FastAPI automatically generates OpenAPI (Swagger UI) and ReDoc documentation from the code. This significantly reduces the effort required for API documentation and provides an interactive way to test endpoints.
- **Type-Safe:** By leveraging Pydantic, FastAPI provides robust data validation and serialization using standard Python type hints, which improves code quality and reduces runtime errors.
- **Developer Experience:** The framework's design is simple and intuitive, leading to faster development cycles and more maintainable code.
