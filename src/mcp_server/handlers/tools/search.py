# src/mcp_server/handlers/tools/search.py
import structlog
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from pydantic import BaseModel, Field
from src.mcp_server.services.search_service import SearchService

log = structlog.get_logger(__name__)

class SearchInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=10, ge=1, le=100)

def register(mcp: FastMCP) -> None:
    service = SearchService()

    @mcp.tool(description="Search the knowledge base for relevant documents")
    async def search(query: str, limit: int = 10) -> str:
        # Pydantic validates at the boundary
        params = SearchInput(query=query, limit=limit)

        log.info("tool.search.called", query=params.query, limit=params.limit)
        try:
            results = await service.query(params.query, params.limit)
            return results.model_dump_json(indent=2)
        except Exception as e:
            log.error("tool.search.failed", error=str(e))
            # Never leak internal errors to the LLM
            raise McpError(-32603, "Search failed. Please try again.")