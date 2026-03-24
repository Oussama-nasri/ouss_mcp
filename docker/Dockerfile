# docker/Dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml .
RUN uv sync --no-dev

FROM python:3.12-slim AS runner
WORKDIR /app

# Non-root user — security best practice
RUN groupadd -r mcp && useradd -r -g mcp mcp

COPY --from=builder /app/.venv .venv
COPY src/ src/

ENV PATH="/app/.venv/bin:$PATH"
USER mcp
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import httpx; httpx.get('http://localhost:3000/health')" || exit 1

CMD ["uvicorn", "mcp_server.server:app", "--host", "0.0.0.0", "--port", "3000"]