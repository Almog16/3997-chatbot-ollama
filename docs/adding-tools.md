# How to Add a New Tool to the Agent

## The Importance of Extensibility

A key design goal of this project is **extensibility**. The agent's true power comes from the tools it can use to interact with the outside world. This document serves as the primary guide for developers looking to extend the agent's capabilities by adding new tools.

Following this guide demonstrates that the agent is not a closed system but a flexible framework designed for growth.

## Step 1: Define the Tool Function (`The Extension Point`)

The core of adding a new feature is defining a Python function that will serve as the tool. This function is the "hook" into our agent system.

**Location:** Place your new tool function in a relevant module inside `src/agent/tools/`. If no existing file fits, create a new one (e.g., `src/agent/tools/my_new_tool.py`).

**Requirements for a Tool Function:**
1.  **`@tool` Decorator:** The function *must* be decorated with `@tool` from `langchain_core.tools`. This is how LangChain identifies it as a tool.
2.  **Descriptive Name:** The function name should be clear and verb-oriented (e.g., `get_stock_price`, `calculate_days_between_dates`).
3.  **Critical Docstring:** The function's docstring is not just for humans; **the agent reads it** to understand what the tool does, what its arguments are, and when to use it. It must be detailed and precise.
4.  **Type Hinting:** All arguments and the return value must have clear Python type hints.

### Example: A Simple Weather Tool

```python
# In `src/agent/tools/weather.py`

from langchain_core.tools import tool

@tool
def get_current_weather(city: str) -> str:
    """
    Use this tool to get the current weather for a specified city.

    Args:
        city: The name of the city for which to get the weather.

    Returns:
        A string describing the current weather. For example, "The weather in London is 7°C and sunny."
    """
    # In a real implementation, you would call a weather API here.
    # For this example, we'll return a mock response.
    if "london" in city.lower():
        return "The weather in London is 7°C and sunny."
    elif "paris" in city.lower():
        return "The weather in Paris is 10°C and cloudy."
    else:
        return f"Sorry, I don't know the weather for {city}."
```

## Step 2: Register the Tool with the Agent

Once the tool is defined, you must register it with the agent so it knows it exists.

1.  **Open `src/agent/graph.py`**. This file is responsible for constructing the agent.
2.  **Import** your new tool function at the top of the file.
    ```python
    from src.agent.tools.weather import get_current_weather
    ```
3.  **Add the tool to the `tools` list** inside the `create_agent_graph` function. This list is the central registry for all of the agent's capabilities.
    ```python
    def create_agent_graph(model_name: str) -> CompiledGraph:
        # ... (other code) ...

        # Define the tools the agent can use
        tools = [
            web_search,
            get_webpage_content,
            calculator,
            # ... (other existing tools) ...
            get_current_weather,  # <-- Register your new tool here
        ]

        # ... (rest of the function) ...
    ```

## Step 3: Test the New Tool

With the tool defined and registered, the agent can now use it.

1.  Run the application (`make run`).
2.  Enable "Agent Mode" in the UI.
3.  Ask a question that should trigger your tool, for example:
    > "What's the weather like in London?"

You should see the UI indicate that the `get_current_weather` tool was used, and the agent should provide an answer based on its output.

This process confirms that our system is successfully extensible.