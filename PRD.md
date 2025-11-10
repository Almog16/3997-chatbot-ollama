# Product Requirements Document — 3997 Chatbot Ollama

## 1. Summary

A local-first chat experience that lets power users converse with Ollama-hosted LLMs through a polished web UI backed by a FastAPI streaming service. The product emphasizes privacy (everything stays on-device), multi-conversation management, and optional tool-enhanced agent runs.

## 2. Goals & Success Criteria

| Goal | Success Metric |
|------|----------------|
| Provide a delightful local chat UI | Users can create/rename/delete chats, see streaming responses, and toggle agent mode without page reloads. |
| Support multiple Ollama models | Dropdown lists locally-available models and ensures the selected value is honored in every request. |
| Offer deterministic testing | Playwright E2E suite and pytest backend suite run without an actual Ollama instance. |
| Showcase capabilities | Screenshots/video provide a shareable reference for stakeholders. |

Out of scope: hosted inference, user auth, cloud sync, telemetry.

## 3. Users & Use Cases

1. **Local tinkerer** – wants a beautiful UI over their local Ollama install for note taking and quick ideation. Needs multi-chat and simple streaming responses.
2. **Power experimenter** – tests different models or LangGraph tool execution. Needs to see tool call indicators and error feedback when models lack tool support.
3. **Project stakeholder** – reviews documentation, screenshots, and video to understand final quality without running the stack.

## 4. User Journey

1. Launch FastAPI backend (`make run`) and React frontend (`make run-client`).
2. UI fetches `/api/models`; dropdown auto-selects first available model (e.g., `gemma3:4b`).
3. User creates a conversation, sends a prompt, and sees streaming updates.
4. Optional: toggle Agent Mode → backend proxies `/api/agent/chat`, displays tool call/result indicators.
5. User switches models; subsequent prompts log the new model on the backend.
6. Screenshots/video are consumed via README for demo purposes.

## 5. Functional Requirements

1. **Model management**
   - Fetch `/api/models` on load; show graceful error if backend unreachable.
   - Selecting a model updates state and every subsequent request payload.
2. **Conversation lifecycle**
   - Create, rename, delete, clear chats; sidebar persists the order and shows message counts.
3. **Chat streaming**
   - Simple mode posts to `/api/chat` and streams SSE lines into the transcript.
   - Agent mode posts to `/api/agent/chat`, rendering tool call/result badges before final response.
4. **Backend services**
   - `/api/chat` logs the model, streams Ollama `/api/chat`, and (future) falls back to `/api/generate`.
   - `/api/agent/chat` orchestrates LangGraph agent flow and streams events.
5. **Testing**
   - Playwright E2E suite (Chromium/Firefox/WebKit) uses service-level mocks.
   - Pytest suite mounts the FastAPI app via httpx `ASGITransport` and mocks httpx calls to Ollama.

## 6. Non-Functional Requirements

| Category | Expectation |
|----------|-------------|
| Performance | First response in <2s once model is warmed up; streaming updates surface as received. |
| Privacy | No network calls beyond localhost; everything resolvable offline. |
| Documentation | README covers setup/testing/visuals; prompts directory lists ideation inputs. |
| UX polish | Tailwind-driven styling, animations, and responsive layout. |

## 7. Model Considerations (Negatives & Trade-offs)

| Model | Positives | Negatives / Mitigations |
|-------|-----------|-------------------------|
| `gemma3:4b` | Lightweight, fast startup, good for simple Q&A. | No tool-calling support → Agent Mode must stay off, or backend should warn. Knowledge cutoff may produce outdated facts. |
| `qwen3:8b` | Supports tool calling and richer reasoning. | Large download (≈8B) and higher VRAM/CPU demands. Initial inference latency is higher. |

Future work: surface model metadata (tool support, parameter size) in the dropdown to guide user choice.

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Ollama model not installed → 404 | UI spins forever waiting for SSE | Autodetect models list, log model per request, document install commands, and add `/api/generate` fallback. |
| Agent mode used with non-tool model | User sees error and no response | Frontend check (list of tool-compatible models) guards send; backend logs still show attempts. |
| Media assets drift | README references broken links | Store screenshots/videos under `resources/` tracked in git; instruct contributors to update when UX changes. |

## 9. Acceptance Checklist

- [ ] Backend and frontend boot instructions verified on clean machine.
- [ ] README Visual Preview shows the five screenshots plus the video link.
- [ ] Tests: `npm --prefix client run test:e2e` and `.venv/bin/python -m pytest` both pass locally.
- [ ] Backend logs display `Streaming request -> model=...` for each request.
- [ ] Model dropdown updates the request payload (confirmed via Playwright assertion).
