# Testing & QA Overview

This document summarizes the automated test strategy and expected outcomes.

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

## 3. Error Handling & Edge Cases

- `/api/models` success/failure paths verified via mocked `httpx.AsyncClient`.
- `/api/chat` streaming success plus network failure case (ensures user-facing JSON error).
- `/api/agent/chat` covers: simple mode, disabled agent fallback, tool streaming, and catastrophic agent exceptions emitting error events.

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
