import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

SERVER_URL = "http://localhost:3000/sse"

# ── tiny helpers ──────────────────────────────────────────────────────────

def ok(label: str, value: object = "") -> None:
    print(f"  \033[32m✓\033[0m  {label}", f"→ {value}" if value != "" else "")

def fail(label: str, err: object) -> None:
    print(f"  \033[31m✗\033[0m  {label}: {err}")

async def call(session: ClientSession, tool: str, args: dict) -> object:
    result = await session.call_tool(tool, args)
    if result.isError:
        raise RuntimeError(result.content[0].text)
    return json.loads(result.content[0].text)


# ── tests ─────────────────────────────────────────────────────────────────

async def main() -> None:
    print(f"\nConnecting to {SERVER_URL} …\n")

    async with sse_client(SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. list tools
            try:
                tools = await session.list_tools()
                names = [t.name for t in tools.tools]
                ok("list_tools", names)
            except Exception as e:
                fail("list_tools", e)

            # 2. list resources
            try:
                res = await session.list_resources()
                ok("list_resources", [str(r.uri) for r in res.resources])
            except Exception as e:
                fail("list_resources", e)

            # 3. list prompts
            try:
                pr = await session.list_prompts()
                ok("list_prompts", [p.name for p in pr.prompts])
            except Exception as e:
                fail("list_prompts", e)

            # 4. search tool
            try:
                data = await call(session, "search", {"query": "mcp", "limit": 2})
                ok("search", f"{data['total']} results in {data['took_ms']}ms")
            except Exception as e:
                fail("search", e)

            # 5. calculate tool — happy path
            try:
                data = await call(session, "calculate", {"expression": "sqrt(144)"})
                assert data["result"] == 12, f"expected 12 got {data['result']}"
                ok("calculate sqrt(144)", data["result"])
            except Exception as e:
                fail("calculate sqrt(144)", e)

            # 6. calculate tool — error path
            try:
                await call(session, "calculate", {"expression": "1 / 0"})
                fail("calculate 1/0", "should have raised")
            except Exception:
                ok("calculate 1/0 returns error")

            # 7. summarize prompt
            try:
                result = await session.get_prompt("summarize", {
                    "text": "MCP lets LLMs talk to tools.",
                    "style": "tldr",
                })
                ok("summarize prompt", f"{result.messages} message(s)")
            except Exception as e:
                fail("summarize prompt", e)



asyncio.run(main())