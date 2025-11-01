import json
from collections.abc import AsyncIterator
from typing import Any

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src import server


@pytest_asyncio.fixture
async def async_client() -> AsyncIterator[AsyncClient]:
    """Provide an httpx client bound to the FastAPI ASGI app."""
    transport = ASGITransport(app=server.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "agent_mode" in payload


@pytest.mark.asyncio
async def test_list_models_success(
    monkeypatch: pytest.MonkeyPatch,
    async_client: AsyncClient,
) -> None:
    models_payload = {"models": [{"name": "qwen3:8b"}]}

    class DummyResponse:
        def __init__(self, data: dict[str, Any]) -> None:
            self._data = data

        def raise_for_status(self) -> None:  # pragma: no cover - nothing to do
            return None

        def json(self) -> dict[str, Any]:
            return self._data

    class DummyAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> "DummyAsyncClient":
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

        async def get(self, url: str) -> DummyResponse:
            assert url == "http://localhost:11434/api/tags"
            return DummyResponse(models_payload)

    monkeypatch.setattr(server.httpx, "AsyncClient", DummyAsyncClient)

    response = await async_client.get("/api/models")

    assert response.status_code == 200
    assert response.json() == {"models": models_payload["models"]}


@pytest.mark.asyncio
async def test_list_models_failure(
    monkeypatch: pytest.MonkeyPatch,
    async_client: AsyncClient,
) -> None:
    request = httpx.Request("GET", "http://localhost:11434/api/tags")

    class FailingAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> "FailingAsyncClient":
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

        async def get(self, url: str) -> None:
            raise httpx.ConnectError("boom", request=request)

    monkeypatch.setattr(server.httpx, "AsyncClient", FailingAsyncClient)

    response = await async_client.get("/api/models")

    assert response.status_code == 200
    payload = response.json()
    assert payload["models"] == []
    assert "boom" in payload["error"]


@pytest.mark.asyncio
async def test_chat_endpoint_streams_response(
    monkeypatch: pytest.MonkeyPatch,
    async_client: AsyncClient,
) -> None:
    chunks = [
        json.dumps({"message": {"content": "Hello"}}),
        json.dumps({"done": True}),
    ]

    class DummyStreamResponse:
        async def __aenter__(self) -> "DummyStreamResponse":
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

        def raise_for_status(self) -> None:
            return None

        async def aiter_lines(self) -> AsyncIterator[str]:
            for entry in chunks:
                yield entry

    class StreamingAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> "StreamingAsyncClient":
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

        def stream(self, method: str, url: str, json: dict[str, Any]) -> DummyStreamResponse:
            assert method == "POST"
            assert url == server.OLLAMA_API_BASE
            assert json["model"] == "test-model"
            return DummyStreamResponse()

    monkeypatch.setattr(server.httpx, "AsyncClient", StreamingAsyncClient)

    payload = {"model": "test-model", "messages": [], "stream": True}

    response = await async_client.post("/api/chat", json=payload)
    received = []
    async for line in response.aiter_lines():
        if line:
            received.append(json.loads(line))

    assert received == [
        {"message": {"content": "Hello"}},
        {"done": True},
    ]


@pytest.mark.asyncio
async def test_agent_endpoint_simple_mode(
    monkeypatch: pytest.MonkeyPatch,
    async_client: AsyncClient,
) -> None:
    monkeypatch.setattr(server, "ENABLE_AGENT_MODE", True)

    class DummyLLM:
        def __init__(self) -> None:
            self.invocations: list[list[dict[str, str]]] = []

        def invoke(self, messages: list[Any]) -> Any:
            self.invocations.append(messages)
            return type("Response", (), {"content": "Simple reply"})

    dummy_llm = DummyLLM()
    monkeypatch.setattr(server, "create_simple_llm", lambda model_name: dummy_llm)

    response = await async_client.post(
        "/api/agent/chat",
        json={
            "model": "test-model",
            "messages": [{"role": "user", "content": "Ping"}],
            "tool_choice": "none",
            "stream": True,
        },
    )
    received = []
    async for line in response.aiter_lines():
        if line:
            received.append(json.loads(line))

    assert any(entry.get("type") == "status" for entry in received)
    assert {"type": "message", "content": "Simple reply"} in received
    assert received[-1]["type"] == "done"


@pytest.mark.asyncio
async def test_agent_endpoint_tool_flow(
    monkeypatch: pytest.MonkeyPatch,
    async_client: AsyncClient,
) -> None:
    monkeypatch.setattr(server, "ENABLE_AGENT_MODE", True)

    class DummyMessage:
        def __init__(self, content: str = "", tool_calls: list | None = None) -> None:
            self.content = content
            self.tool_calls = tool_calls or []

    class DummyAgent:
        async def astream(self, initial_state: dict) -> AsyncIterator[dict]:
            yield {
                "agent": {
                    "messages": [
                        DummyMessage(
                            tool_calls=[
                                {"name": "calculator", "args": {"expression": "2+2"}},
                            ]
                        )
                    ]
                }
            }
            yield {
                "tools": {
                    "tool_results": [
                        {"tool": "calculator", "result": "4"},
                    ]
                }
            }
            yield {
                "agent": {
                    "messages": [
                        DummyMessage(content="All done")
                    ]
                }
            }
        def invoke(self, initial_state: dict) -> dict:
            return {
                "messages": [
                    DummyMessage(content="All done"),
                ]
            }

    monkeypatch.setattr(server, "create_agent_graph", lambda model_name: DummyAgent())

    response = await async_client.post(
        "/api/agent/chat",
        json={
            "model": "test-model",
            "messages": [{"role": "user", "content": "Use tools please"}],
            "tool_choice": "auto",
            "stream": True,
        },
    )

    events = []
    async for line in response.aiter_lines():
        if line:
            events.append(json.loads(line))

    assert {"type": "status", "content": "Agent mode activated"} in events
    assert {"type": "tool_call", "tool": "calculator", "args": {"expression": "2+2"}} in events
    assert {"type": "tool_result", "tool": "calculator", "result": "4"} in events
    assert {"type": "message", "content": "All done"} in events
    assert events[-1]["type"] == "done"
