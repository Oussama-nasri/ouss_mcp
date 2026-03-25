"""
src/mcp_server/app.py

Exposes the MCP server over SSE/HTTP using FastAPI.
Run with:
    uvicorn mcp_server.app:app --host 0.0.0.0 --port 3000 --reload
"""

from fastapi import FastAPI
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.responses import Response

from src.mcp_server.server import mcp

app = FastAPI(title="MCP Server")
sse = SseServerTransport("/messages/")


@app.get("/sse")
async def handle_sse(request: Request) -> Response:
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp._mcp_server.run(
            streams[0], streams[1], mcp._mcp_server.create_initialization_options()
        )
    return Response()


@app.post("/messages/")
async def handle_messages(request: Request) -> Response:
    await sse.handle_post_message(request.scope, request.receive, request._send)
    return Response()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}