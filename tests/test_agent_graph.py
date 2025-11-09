import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src.agent import graph as agent_graph
from src.agent.tools import calculator


def test_create_agent_graph_without_tools_uses_simple_graph(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyLLM:
        def __init__(self, *args, **kwargs) -> None:  # pragma: no cover - no behavior needed
            return None

    sentinel = object()

    monkeypatch.setattr(agent_graph, "ChatOllama", DummyLLM)
    monkeypatch.setattr(agent_graph, "get_tools", lambda: [])
    monkeypatch.setattr(agent_graph, "create_simple_graph", lambda llm: sentinel)

    result = agent_graph.create_agent_graph("mock-model")
    assert result is sentinel


def test_create_simple_graph_invokes_llm_once() -> None:
    class RecordingLLM:
        def __init__(self) -> None:
            self.calls = 0

        def invoke(self, messages) -> AIMessage:
            self.calls += 1
            return AIMessage(content="Simple response")

    llm = RecordingLLM()
    workflow = agent_graph.create_simple_graph(llm)
    state = {
        "messages": [HumanMessage(content="Hello")],
        "reasoning_steps": [],
        "tool_results": [],
        "iteration_count": 0,
    }

    result = workflow.invoke(state)

    assert llm.calls == 1
    assert result["messages"][-1].content == "Simple response"
    assert result["iteration_count"] == 1


def test_create_agent_graph_with_tools_executes_tool(monkeypatch: pytest.MonkeyPatch) -> None:
    class ToolAwareLLM:
        def __init__(self, *args, **kwargs) -> None:
            self.calls = 0
            self.bound_tools: list | None = None

        def bind_tools(self, tools: list) -> "ToolAwareLLM":
            self.bound_tools = tools
            return self

        def invoke(self, messages) -> AIMessage:
            self.calls += 1
            if self.calls == 1:
                tool_name = self.bound_tools[0].name
                return AIMessage(
                    content="",
                    tool_calls=[{
                        "id": "tool-1",
                        "name": tool_name,
                        "args": {"expression": "2+2"},
                    }],
                )
            return AIMessage(content="Final answer")

    monkeypatch.setattr(agent_graph, "ChatOllama", ToolAwareLLM)
    monkeypatch.setattr(agent_graph, "get_tools", lambda: [calculator])

    workflow = agent_graph.create_agent_graph("mock-model")
    state = {
        "messages": [HumanMessage(content="Compute 2+2")],
        "reasoning_steps": [],
        "tool_results": [],
        "iteration_count": 0,
    }

    result = workflow.invoke(state)

    assert result["messages"][-1].content == "Final answer"
    assert result["tool_results"][-1]["tool"] == calculator.name
    assert result["tool_results"][-1]["result"].startswith("Result:")
