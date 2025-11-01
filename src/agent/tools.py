"""Tool Definitions
Provides various tools for the agent to use
"""

import re
from datetime import datetime

from langchain_core.tools import tool

# --- Mathematical & Computation Tools ---

@tool
def calculator(expression: str) -> str:
    """Perform mathematical calculations safely.

    Args:
    ----
        expression: Mathematical expression to evaluate (e.g., "2 + 2", "(75-32)*5/9")

    Returns:
    -------
        Result of the calculation or error message

    """
    try:
        # Remove any potentially dangerous characters/functions
        # Only allow numbers, operators, parentheses, and basic math functions
        safe_expression = re.sub(r"[^0-9+\-*/().\s]", "", expression)

        if not safe_expression:
            return "Error: Invalid expression"

        # Evaluate the expression
        result = eval(safe_expression, {"__builtins__": {}}, {}) # noqa: S307
        return f"Result: {result}"

    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error calculating expression: {e!s}"


@tool
def unit_converter(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between common units (temperature, length, weight).

    Args:
    ----
        value: The numeric value to convert
        from_unit: Source unit (e.g., 'celsius', 'fahrenheit', 'km', 'miles', 'kg', 'lbs')
        to_unit: Target unit

    Returns:
    -------
        Converted value with explanation

    """
    conversions = {
        # Temperature
        ("celsius", "fahrenheit"): lambda x: (x * 9 / 5) + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5 / 9,
        ("celsius", "kelvin"): lambda x: x + 273.15,
        ("kelvin", "celsius"): lambda x: x - 273.15,

        # Length
        ("km", "miles"): lambda x: x * 0.621371,
        ("miles", "km"): lambda x: x * 1.60934,
        ("meters", "feet"): lambda x: x * 3.28084,
        ("feet", "meters"): lambda x: x * 0.3048,
        ("cm", "inches"): lambda x: x * 0.393701,
        ("inches", "cm"): lambda x: x * 2.54,

        # Weight
        ("kg", "lbs"): lambda x: x * 2.20462,
        ("lbs", "kg"): lambda x: x * 0.453592,
    }

    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](value)
        return f"✓ {value} {from_unit} = {result:.2f} {to_unit}"
    available = ", ".join([f"{f}->{t}" for f, t in conversions])
    return f"Error: Conversion not supported. Available: {available}"


# --- Date & Time Tools ---

@tool
def get_current_time() -> str:
    """Get the current date and time.

    Returns
    -------
        Current date and time in a readable format

    """
    now = datetime.now()
    return f"📅 Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S %A')}"


@tool
def get_timezone_time(timezone: str) -> str:
    """Get current time in a specific timezone.

    Args:
    ----
        timezone: Timezone name (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo')

    Returns:
    -------
        Current time in the specified timezone

    """
    try:
        from zoneinfo import ZoneInfo

        tz = ZoneInfo(timezone)
        now = datetime.now(tz)
        return f"🌍 Time in {timezone}: {now.strftime('%Y-%m-%d %H:%M:%S %A %Z')}"

    except ImportError:
        return "Error: zoneinfo not available (Python 3.9+ required)"
    except Exception as e:
        return f"Error: {e!s}. Try timezones like 'America/New_York', 'Europe/London', 'Asia/Tokyo'"


@tool
def days_between_dates(date1: str, date2: str) -> str:
    """Calculate days between two dates.

    Args:
    ----
        date1: First date in YYYY-MM-DD format
        date2: Second date in YYYY-MM-DD format

    Returns:
    -------
        Number of days between the dates

    """
    try:
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")
        diff = abs((d2 - d1).days)
        return f"📆 Days between {date1} and {date2}: {diff} days"
    except Exception as e:
        return f"Error: {e!s}. Use format YYYY-MM-DD (e.g., 2024-12-31)"


# --- Text & String Tools ---

@tool
def text_analyzer(text: str) -> str:
    """Analyze text - count words, characters, sentences.

    Args:
    ----
        text: The text to analyze

    Returns:
    -------
        Analysis with word count, character count, and sentence count

    """
    words = len(text.split())
    chars = len(text)
    sentences = len([s for s in text.split(".") if s.strip()])

    return (f"📝 Text Analysis:\n"
            f"- Words: {words}\n"
            f"- Characters: {chars}\n"
            f"- Sentences: {sentences}\n"
            f"- Avg word length: {chars / words:.1f} chars")


@tool
def encode_decode_text(text: str, operation: str = "base64_encode") -> str:
    """Encode or decode text in various formats.

    Args:
    ----
        text: Text to encode/decode
        operation: One of 'base64_encode', 'base64_decode', 'url_encode', 'url_decode'

    Returns:
    -------
        Encoded or decoded text

    """
    try:
        import base64
        import urllib.parse

        if operation == "base64_encode":
            result = base64.b64encode(text.encode()).decode()
            return f"Base64 encoded: {result}"
        if operation == "base64_decode":
            result = base64.b64decode(text.encode()).decode()
            return f"Base64 decoded: {result}"
        if operation == "url_encode":
            result = urllib.parse.quote(text)
            return f"URL encoded: {result}"
        if operation == "url_decode":
            result = urllib.parse.unquote(text)
            return f"URL decoded: {result}"
        return "Error: Operation must be base64_encode, base64_decode, url_encode, or url_decode"
    except Exception as e:
        return f"Error: {e!s}"


# List of all available tools
def get_tools() -> list:
    """Return list of all available tools."""
    return [
        # Math & Conversion
        calculator,
        unit_converter,

        # Date & Time
        get_current_time,
        get_timezone_time,
        days_between_dates,

        # Text Processing
        text_analyzer,
        encode_decode_text
    ]
