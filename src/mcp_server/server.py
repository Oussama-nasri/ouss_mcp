import asyncio
from mcp.server.fastmcp import FastMCP
from .config import settings
from .handlers.tools import search, calculator
from .handlers.resources import file_resource
from .handlers.prompts import summarize_prompt
from .middleware.logging import configure_logging

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