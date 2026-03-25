"""
SearchService — pure business logic, no MCP coupling.

Replace the in-memory store with your real backend:
  - Postgres full-text search (asyncpg / SQLAlchemy)
  - Elasticsearch / OpenSearch (elasticsearch-py async)
  - Pinecone / Weaviate for vector search
  - Any combination of the above
"""

import time
import structlog
from pydantic import BaseModel

log = structlog.get_logger(__name__)


class SearchResult(BaseModel):
    id: str
    title: str
    snippet: str
    score: float
    url: str | None = None


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[SearchResult]
    took_ms: float


# ---------------------------------------------------------------------------
# In-memory stub — swap this class body for your real backend
# ---------------------------------------------------------------------------
_STUB_DOCUMENTS = [
    {
        "id": "doc-1",
        "title": "Getting started with MCP",
        "body": "The Model Context Protocol (MCP) lets you expose tools, resources, and prompts to LLMs.",
        "url": "https://docs.example.com/mcp/getting-started",
    },
    {
        "id": "doc-2",
        "title": "FastMCP decorator reference",
        "body": "Use @mcp.tool(), @mcp.resource(), and @mcp.prompt() to register handlers.",
        "url": "https://docs.example.com/mcp/decorators",
    },
    {
        "id": "doc-3",
        "title": "Deploying to a VPS",
        "body": "Docker + Nginx + systemd is the recommended stack for self-hosted MCP servers.",
        "url": "https://docs.example.com/mcp/deployment",
    },
    {
        "id": "doc-4",
        "title": "Pydantic validation patterns",
        "body": "Always validate at the boundary using Pydantic v2 models for type safety.",
        "url": "https://docs.example.com/mcp/validation",
    },
    {
        "id": "doc-5",
        "title": "Rate limiting strategies",
        "body": "Use sliding window rate limiters backed by Redis in multi-replica deployments.",
        "url": "https://docs.example.com/mcp/rate-limiting",
    },
]


class SearchService:
    """
    Naive in-memory search service.
    Production: replace `_search` with asyncpg / elasticsearch / vector DB calls.
    """

    async def query(self, query: str, limit: int = 10) -> SearchResponse:
        start = time.perf_counter()

        log.info("search_service.query", query=query, limit=limit)

        results = await self._search(query.lower(), limit)

        took_ms = (time.perf_counter() - start) * 1000
        log.info("search_service.done", total=len(results), took_ms=round(took_ms, 2))

        return SearchResponse(
            query=query,
            total=len(results),
            results=results,
            took_ms=round(took_ms, 2),
        )

    async def _search(self, query: str, limit: int) -> list[SearchResult]:
        """Simple substring match — replace with your real search logic."""
        hits: list[SearchResult] = []

        for doc in _STUB_DOCUMENTS:
            score = self._score(query, doc["title"], doc["body"])
            if score > 0:
                hits.append(
                    SearchResult(
                        id=doc["id"],
                        title=doc["title"],
                        snippet=doc["body"][:150],
                        score=score,
                        url=doc.get("url"),
                    )
                )

        # Sort by score descending, apply limit
        hits.sort(key=lambda r: r.score, reverse=True)
        return hits[:limit]

    @staticmethod
    def _score(query: str, title: str, body: str) -> float:
        """Naive TF-style scoring — title matches worth 2×."""
        title_hits = title.lower().count(query)
        body_hits = body.lower().count(query)
        return float(title_hits * 2 + body_hits)