# src/mcp_server/handlers/resources/file_resource.py
from mcp.server.fastmcp import FastMCP
from mcp.types import McpError, ErrorCode
import aiofiles

def register(mcp: FastMCP) -> None:

    @mcp.resource("file://{path}")
    async def read_file(path: str) -> str:
        # Sanitize — never trust user-supplied paths
        safe_path = Path(path).resolve()
        allowed_root = Path("/data/files").resolve()

        if not safe_path.is_relative_to(allowed_root):
            raise McpError(ErrorCode.INVALID_PARAMS, "Access denied")

        async with aiofiles.open(safe_path) as f:
            return await f.read()