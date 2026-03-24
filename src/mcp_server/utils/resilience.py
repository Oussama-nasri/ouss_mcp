# src/mcp_server/utils/resilience.py
import httpx
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log,
)
import structlog

log = structlog.get_logger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    before_sleep=before_sleep_log(log, log.warning),
)
async def resilient_get(client: httpx.AsyncClient, url: str, **kwargs):
    response = await client.get(url, timeout=10.0, **kwargs)
    response.raise_for_status()
    return response