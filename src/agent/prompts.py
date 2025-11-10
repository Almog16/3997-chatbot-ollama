from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

# Path setup
TEMPLATE_DIR = Path(__file__).parent / "templates"

# Jinja2 environment
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["jinja", "xml"])
)


def get_system_prompt(tools: list[dict] | None = None) -> str:
    """Renders the system prompt for the agent from a Jinja2 template.

    This function dynamically generates the system prompt that instructs the
    agent on how to behave. It uses a Jinja2 template to structure the prompt
    and can optionally include a list of available tools, which allows the
    agent to know which functions it can call.

    Args:
    ----
        tools: An optional list of dictionaries, where each dictionary
               describes a tool with its name and description. This allows
               the agent to be aware of the tools it can use.
               Example: [{"name": "web_search", "description": "Search the web"}]

    Returns:
    -------
        A string containing the rendered system prompt, ready to be used in
        the conversation.

    """
    template = jinja_env.get_template("agent_system_prompt.jinja2")
    return template.render(tools=tools or [])
