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
    """Render the XML system prompt from the Jinja2 template.

    Args:
    ----
        tools: Optional list of tools, e.g.:
                     [{"name": "web_search", "description": "Search the web"}]

    """
    template = jinja_env.get_template("agent_system_prompt.jinja2")
    return template.render(tools=tools or [])
