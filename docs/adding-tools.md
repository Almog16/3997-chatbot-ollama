# How to Add a New Tool to the Agent

This guide explains how to extend the agent's capabilities by adding a new custom tool. The agent uses tools to perform actions beyond its core language model, such as searching the web, performing calculations, or accessing other APIs.

Our agent's tool system is built using LangChain's `@tool` decorator, which makes it easy to convert a standard Python function into a tool that the agent can use.

## Step 1: Define the Tool Function

First, you need to create the Python function that will perform the desired action. This function should be placed in a relevant module within the `src/agent/tools/` directory. If no existing file fits, you can create a new one.

A tool function should have the following characteristics:
- It is decorated with the `@tool` decorator from `langchain_core.tools`.
- It has a clear, descriptive name that tells the agent what it does.
- It has a detailed docstring that explains its purpose, arguments, and what it returns. **This docstring is critical**, as the agent uses it to decide when and how to use the tool.
- It has type hints for all its arguments and its return value.

### Example: A Simple Weather Tool

Let's say we want to create a tool that gets the weather for a specific city.

1.  Create a new file: `src/agent/tools/weather.py`.
2.  Add the following code:

```python
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

## Step 2: Register the New Tool with the Agent

After defining the tool, you need to make the agent aware of it. This is done by adding the tool to the list of tools that are passed to the agent's constructor.

1.  Open the `src/agent/graph.py` file.
2.  Import your new tool function at the top of the file:

    ```python
    from src.agent.tools.weather import get_current_weather
    ```

3.  Find the `create_agent_graph` function. Inside this function, there is a list named `tools`. Add your new tool to this list:

    ```python
    def create_agent_graph(model_name: str) -> CompiledGraph:
        # ... (other code) ...

        # Define the tools the agent can use
        tools = [
            web_search,
            get_webpage_content,
            calculator,
            # ... (other existing tools) ...
            get_current_weather,  # <-- Add your new tool here
        ]

        # ... (rest of the function) ...
    ```

## Step 3: Test the New Tool

That's it! The agent is now aware of your new tool and can use it to answer relevant questions.

To test it, run the application, make sure "Agent Mode" is enabled, and ask a question that should trigger your new tool. For our example, you could ask:

> "What's the weather like in London?"

You should see the agent call the `get_current_weather` tool in the UI and then provide the answer based on the tool's output.

By following this process, you can easily extend the agent with a wide range of custom capabilities.
