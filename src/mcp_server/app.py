from fastapi import FastAPI
from mcp.server.sse import SseServerTransport
from starlette.types import Scope, Receive, Send
from viztracer import VizTracer
from src.mcp_server.server import mcp

app = FastAPI(title="MCP Server")

sse = SseServerTransport("/messages/")

tracer = VizTracer(output_file="mcp_trace.json")


# ✅ RAW ASGI HANDLER (not FastAPI route)
async def sse_app(scope: Scope, receive: Receive, send: Send):
    with tracer:
        if scope["type"] == "http" and scope["path"] == "/sse":
            async with sse.connect_sse(scope, receive, send) as streams:
                await mcp._mcp_server.run(
                    streams[0],
                    streams[1],
                    mcp._mcp_server.create_initialization_options(),
                )
            return

    if scope["type"] == "http" and scope["path"].startswith("/messages"):
        await sse.handle_post_message(scope, receive, send)
        return

    # fallback to FastAPI
    await app(scope, receive, send)


# expose this to uvicorn
application = sse_app


@app.get("/health")
async def health():
    return {"status": "ok"}