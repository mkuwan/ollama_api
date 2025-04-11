# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Greeting")

@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"