import base64
from datetime import datetime as dt_datetime

import pytest

from src.agent import tools as agent_tools


def test_calculator_handles_basic_expression_and_invalid_input() -> None:
    assert "Result: 4" in agent_tools.calculator.func("2+2")
    assert "invalid" in agent_tools.calculator.func("").lower()


def test_unit_converter_success_and_error() -> None:
    success = agent_tools.unit_converter.func(1, "km", "miles")
    assert "✓ 1 km" in success

    failure = agent_tools.unit_converter.func(10, "parsec", "mile")
    assert "Conversion not supported" in failure


def test_get_current_time_uses_patched_datetime(monkeypatch: pytest.MonkeyPatch) -> None:
    class FixedDateTime:
        @staticmethod
        def now(*_, **__) -> dt_datetime:
            return dt_datetime(2024, 1, 1, 12, 0, 0)

    monkeypatch.setattr(agent_tools, "datetime", FixedDateTime)
    message = agent_tools.get_current_time.func()
    assert "2024-01-01" in message


def test_get_timezone_time_valid_and_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    class FixedDateTime:
        @staticmethod
        def now(tz=None) -> dt_datetime:
            return dt_datetime(2024, 1, 1, 12, 0, 0, tzinfo=tz)

    monkeypatch.setattr(agent_tools, "datetime", FixedDateTime)
    success = agent_tools.get_timezone_time.func("UTC")
    assert "UTC" in success

    failure = agent_tools.get_timezone_time.func("Not/AZone")
    assert "Error" in failure


def test_days_between_dates() -> None:
    result = agent_tools.days_between_dates.func("2024-01-01", "2024-01-11")
    assert "10 days" in result


def test_text_analyzer_reports_counts() -> None:
    analysis = agent_tools.text_analyzer.func("Hello world. Bye.")
    assert "Words: 3" in analysis
    assert "Sentences: 2" in analysis


def test_encode_decode_text_round_trip() -> None:
    encoded = agent_tools.encode_decode_text.func("hi", operation="base64_encode")
    payload = encoded.split(": ").pop()
    assert payload == base64.b64encode(b"hi").decode()

    decoded = agent_tools.encode_decode_text.func(payload, operation="base64_decode")
    assert "Base64 decoded: hi" in decoded


def test_get_tools_contains_known_tool() -> None:
    tools = agent_tools.get_tools()
    tool_names = {tool.name for tool in tools}
    assert "calculator" in tool_names
