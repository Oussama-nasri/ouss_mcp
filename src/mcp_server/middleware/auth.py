# src/mcp_server/middleware/auth.py
import hmac
from mcp.types import McpError, ErrorCode
from ..config import settings

async def verify_api_key(token: str) -> None:
    expected = settings.api_key.encode()
    provided = token.encode()
    # Constant-time comparison — prevents timing attacks
    if not hmac.compare_digest(expected, provided):
        raise McpError(ErrorCode.INVALID_REQUEST, "Unauthorized")
