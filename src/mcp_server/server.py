from mcp.server.fastmcp import FastMCP
from src.mcp_server.config import settings
from src.mcp_server.handlers.tools import search, calculator
from src.mcp_server.handlers.resources import file_resource
from src.mcp_server.handlers.prompts import summarize_prompt
from src.mcp_server.middleware.logging import configure_logging

configure_logging(settings.log_level)

mcp = FastMCP(settings.app_name)

# Register handlers
search.register(mcp)
calculator.register(mcp)
file_resource.register(mcp)
summarize_prompt.register(mcp)

if __name__ == "__main__":
    if settings.transport == "sse":
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")