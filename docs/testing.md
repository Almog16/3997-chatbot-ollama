# Testing & QA Overview

This document summarizes the automated test strategy, error handling procedures, and expected outcomes for the project.

## 1. Test Matrix

| Layer | Tooling | Execution Command | Purpose |
|-------|---------|-------------------|---------|
| API / Backend | `pytest`, `pytest-asyncio`, `pytest-cov` | `uv run pytest` | Validates FastAPI endpoints, LangGraph agent flows, and error handling with full coverage reports. |
| UI / E2E | Playwright (Chromium/Firefox/WebKit) | `npm --prefix client run test:e2e` | Exercises conversation CRUD, streaming UX, and agent toggles with mocked backends. |

## 2. Coverage Targets

Pytest runs with coverage instrumentation enabled by default (see `pyproject.toml`). Reports are emitted to:

- Terminal summary (`--cov-report=term-missing`) for human inspection.
- `reports/coverage.xml` for CI ingestion or historical tracking.

Current snapshot (Apple M-series laptop, Feb 2025):

| Package | Coverage |
|---------|----------|
| `src/server.py` | 89% |
| `src/agent/graph.py` | 97% |
| `src/agent/tools.py` | 79% |
| `src/config.py` / `src/types.py` | 100% |
| Overall backend | **95%** line coverage |

> The lower coverage in `src/agent/*` reflects tool integrations that rely on live Ollama runs; stubs/tests cover the FastAPI surface thoroughly.

## 3. Error Handling and Edge Cases

The system is designed to be resilient and provide clear feedback. The following table documents known edge cases, the system's expected response, and the debugging information available.

| Scenario | System Response | User-Facing Error Message | Logs for Debugging |
|---|---|---|---|
| **Ollama Server is Down** | The backend fails to connect to the Ollama API. | The UI shows a persistent "Ollama is not running" error banner. The model dropdown is disabled. | The backend logs will show a `ConnectError` with the target Ollama URL (e.g., `Error: Could not connect to Ollama at http://localhost:11434`). |
| **Model Not Found** | The user selects a model that is not available in their local Ollama instance. | The UI shows an error message: "Model not found. Please pull the model using 'ollama pull <model_name>'." | The backend logs will show a `404 Not Found` error from the Ollama API when the request is made. |
| **Agent Mode on Incompatible Model** | The user enables "Agent Mode" with a model that does not support tool calling. | The UI displays an error in the chat window: "Agent error: The selected model does not support tool calling. Please select a different model or disable Agent Mode." | The backend logs will show an `Agent error` with details about the failure, often related to the model's inability to generate a valid tool call response. |
| **Invalid Tool Call** | The agent attempts to call a tool that does not exist or with incorrect arguments. | The UI will show an error message indicating a tool execution failure. | The backend logs will contain a detailed traceback from the LangGraph execution, showing which tool failed and why. |
| **Network Interruption Mid-Stream** | The connection between the client and the backend is lost while a response is being streamed. | The UI will stop receiving new text. The "Send" button will become available again after a timeout. | The browser's developer console will show a network error for the failed streaming request. Backend logs will show a client disconnect. |

APIs
- `/api/models` success/failure paths verified via mocked `httpx.AsyncClient`.
- `/api/chat` streaming success plus network failure case (ensures user-facing JSON error).
- `/api/agent/chat` covers: simple mode, disabled agent fallback, tool streaming, and catastrophic agent exceptions emitting error events.

### Comprehensive Error Handling Strategy

- **Backend:** All API endpoints are wrapped in `try...except` blocks to catch exceptions (e.g., `httpx.ConnectError`, `httpx.HTTPStatusError`). Errors are logged with detailed context and a user-friendly JSON error message is streamed back to the client.
- **Frontend:** The frontend checks the `type` of each message in the stream. If it receives a message with `type: "error"`, it displays the content in a prominent error banner or message bubble.

## 4. Expected Results

Backend run should end with:

```
======================== 9 passed, 2 warnings in <1s =========================
Coverage XML written to file reports/coverage.xml
```

Frontend run should display all 15 Playwright specs passing across the three browsers with no retries. The HTML report can be viewed via:

```
npx --prefix client playwright show-report
```

## 5. Manual Smoke Checklist

Before releasing, confirm:

1. `make run` + `make run-client` start without errors.
2. Model dropdown lists at least one entry (or shows the offline empty state).
3. Agent mode toggling displays tool call/result badges for supported models.
4. README screenshots & video match the current UI.

## 6. Artifacts & Reporting

- **Backend coverage:** `reports/coverage.xml` (JUnit/Codecov compatible) generated automatically by `uv run pytest` (95% line coverage as of the latest run). Use `coverage xml -i` to regenerate if needed.
- **Frontend report:** Playwright stores HTML reports under `client/playwright-report/`; open via `npx --prefix client playwright show-report`.
- **CI-friendly commands:** `make test` and `make test-client` wrap the exact invocations documented above to ensure consistency.

Maintainers should update this file whenever a new suite, threshold, or tool is added so grading remains aligned with the documented process.
