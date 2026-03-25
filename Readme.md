# MCP Server — Python

A production-ready Model Context Protocol server built with Python, FastMCP, Pydantic v2, and Docker.

## Quick start

```bash
# 1. Clone and enter the project
git clone https://github.com/you/mcp-server && cd mcp-server

# 2. Copy and fill in your environment variables
cp .env.example .env
# Edit .env — at minimum set API_KEY to a 32+ char random string:
#   python -c "import secrets; print(secrets.token_hex(32))"

# 3. Install dependencies (requires uv)
pip install uv && uv sync

# 4. Run in stdio mode (for Claude Desktop)
python -m mcp_server.server

# 5. Run in SSE mode (for remote access)
TRANSPORT=sse python -m mcp_server.server
```

## Project structure

```
src/mcp_server/
├── server.py               Entry point, server bootstrap
├── config.py               Typed settings via pydantic-settings
├── handlers/
│   ├── tools/
│   │   ├── search.py       search tool
│   │   └── calculator.py   calculate tool
│   ├── resources/
│   │   └── file_resource.py   file:// URI handler
│   └── prompts/
│       └── summarize_prompt.py   summarize + code_review prompts
├── middleware/
│   ├── auth.py             Constant-time API key verification
│   ├── rate_limiter.py     Sliding window rate limiter (in-process + Redis)
│   └── logging.py          Structured JSON logging via structlog
├── services/
│   ├── search_service.py   Search logic (swap for real backend)
│   └── calculator_service.py   AST-based safe math evaluator
└── utils/
    └── resilience.py       Retry + backoff helpers (tenacity)
```

## Available tools

| Tool | Description |
|------|-------------|
| `search` | Search the knowledge base. Args: `query` (str), `limit` (int, default 10) |
| `calculate` | Evaluate a math expression safely. Args: `expression` (str) |

## Available resources

| URI | Description |
|-----|-------------|
| `file://` | List all files in the file root |
| `file://{path}` | Read a specific file (UTF-8 text only, max 10 MB) |

## Available prompts

| Prompt | Description |
|--------|-------------|
| `summarize` | Structured summarization. Args: `text`, `style` (bullet/paragraph/tldr), `language`, `max_words` |
| `code_review` | Code review. Args: `code`, `language`, `focus` (security/performance/style/all) |

## Running tests

```bash
uv run pytest                          # all tests
uv run pytest tests/unit/              # unit tests only
uv run pytest tests/integration/       # integration tests only
uv run pytest --cov=src               # with coverage
```

## Docker deployment

```bash
# Build and start all services
cd docker
docker compose up -d

# View logs
docker compose logs -f mcp

# Stop
docker compose down
```

## VPS setup (one-time)

```bash
# On your VPS
sudo apt update && sudo apt install -y docker.io docker-compose-plugin nginx certbot python3-certbot-nginx

# Clone the repo
sudo git clone https://github.com/you/mcp-server /opt/mcp-server
sudo cp /opt/mcp-server/.env.example /opt/mcp-server/.env
# Fill in /opt/mcp-server/.env

# Install systemd service
sudo cp /opt/mcp-server/docker/mcp-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now mcp-server

# Set up Nginx + TLS
sudo cp /opt/mcp-server/docker/nginx.conf /etc/nginx/sites-available/mcp-server
sudo ln -s /etc/nginx/sites-available/mcp-server /etc/nginx/sites-enabled/
# Edit the server_name in nginx.conf, then:
sudo certbot --nginx -d mcp.yourdomain.com
sudo systemctl reload nginx
```

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEY` | Yes | — | 32+ char secret key |
| `TRANSPORT` | No | `stdio` | `stdio` or `sse` |
| `HOST` | No | `0.0.0.0` | Bind address |
| `PORT` | No | `3000` | Bind port |
| `LOG_LEVEL` | No | `INFO` | `DEBUG/INFO/WARNING/ERROR` |
| `DATABASE_URL` | No | `""` | Postgres async URL |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis URL |
| `RATE_LIMIT_PER_MINUTE` | No | `100` | Requests per minute |
| `FILE_ROOT` | No | `/data/files` | Root for file:// resources |

## Adding a new tool

1. Create `src/mcp_server/services/my_service.py` with pure async logic.
2. Create `src/mcp_server/handlers/tools/my_tool.py` with a `register(mcp)` function.
3. Import and call `my_tool.register(mcp)` in `server.py`.
4. Write tests in `tests/unit/test_my_service.py`.