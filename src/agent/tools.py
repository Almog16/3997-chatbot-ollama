"""A collection of tools designed to extend the agent's capabilities.

This module provides a variety of utilities that the agent can use to perform
tasks such as mathematical calculations, unit conversions, and date and time
operations. Each tool is decorated with `@tool` to make it discoverable by
the LangGraph agent. The `get_tools` function at the end of the file gathers
all defined tools into a list for the agent to use.
"""

import re
from datetime import datetime

from langchain_core.tools import tool

# --- Mathematical & Computation Tools ---

@tool
def calculator(expression: str) -> str:
    """Performs mathematical calculations on a given expression.

    This tool evaluates a string containing a mathematical expression and returns
    the result. To ensure safety, it sanitizes the input by removing any
    characters that are not numbers, operators, or parentheses.

    Args:
    ----
        expression: A string representing the mathematical expression to be
                    evaluated (e.g., "2 + 2", "(75-32)*5/9").

    Returns:
    -------
        A string containing the result of the calculation or an error message
        if the expression is invalid or causes an error.

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
    """Converts a value from one unit to another.

    This tool supports conversions between common units of temperature (Celsius,
    Fahrenheit, Kelvin), length (km, miles, meters, feet, cm, inches), and
    weight (kg, lbs).

    Args:
    ----
        value: The numeric value to be converted.
        from_unit: The source unit (e.g., 'celsius', 'km', 'kg').
        to_unit: The target unit to convert to.

    Returns:
    -------
        A string with the converted value and its unit, or an error message if
        the conversion is not supported.

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
    """Retrieves the current date and time.

    This tool returns a formatted string with the current date, time, and day
    of the week, providing a quick way for the agent to access temporal
    information.

    Returns
    -------
        A string representing the current date and time (e.g.,
        "📅 Current date and time: 2024-07-14 10:30:00 Sunday").

    """
    now = datetime.now()
    return f"📅 Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S %A')}"


@tool
def get_timezone_time(timezone: str) -> str:
    """Gets the current time in a specified timezone.

    This tool leverages the `zoneinfo` library to provide the current time in
    any IANA timezone, such as 'America/New_York' or 'Europe/London'.

    Args:
    ----
        timezone: The name of the timezone to get the current time for.

    Returns:
    -------
        A string with the current time in the requested timezone, or an error
        message if the timezone is invalid or `zoneinfo` is not available.

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
    """Calculates the number of days between two dates.

    This tool takes two dates in 'YYYY-MM-DD' format and computes the absolute
    difference in days between them.

    Args:
    ----
        date1: The first date in 'YYYY-MM-DD' format.
        date2: The second date in 'YYYY-MM-DD' format.

    Returns:
    -------
        A string indicating the number of days between the two dates, or an
        error message if the date format is incorrect.

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
    """Analyzes a given text to provide statistics.

    This tool counts the number of words, characters, and sentences in a piece
    of text. It also calculates the average word length.

    Args:
    ----
        text: The text to be analyzed.

    Returns:
    -------
        A formatted string with the text analysis, including word count,
        character count, sentence count, and average word length.

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
    """Encodes or decodes text using various formats.

    This tool supports Base64 and URL encoding and decoding. The desired
    operation is specified via the `operation` argument.

    Args:
    ----
        text: The text to be encoded or decoded.
        operation: The operation to perform. Must be one of 'base64_encode',
                   'base64_decode', 'url_encode', or 'url_decode'.

    Returns:
    -------
        A string with the result of the encoding or decoding, or an error
        message if the operation is not supported or fails.

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
    """Collects and returns a list of all available tools.

    This function gathers all the functions decorated with `@tool` in this
    module and returns them as a list. This list is then used to initialize
    the agent with its available toolset.

    Returns
    -------
        A list of all tool functions.

    """
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
