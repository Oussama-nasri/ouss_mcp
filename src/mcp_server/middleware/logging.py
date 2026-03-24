# src/mcp_server/middleware/logging.py
import structlog

def configure_logging(level: str) -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),   # Machine-readable in prod
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(__import__("logging"), level)
        ),
    )