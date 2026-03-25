import structlog
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from pydantic import BaseModel, Field

from ...services.calculator_service import CalculatorService
from ...middleware.rate_limiter import rate_limiter

log = structlog.get_logger(__name__)


class CalculatorInput(BaseModel):
    expression: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="A mathematical expression to evaluate",
        examples=["2 + 2", "sqrt(144)", "sin(pi / 2)", "(10 * 3.5) / 2"],
    )


def register(mcp: FastMCP) -> None:
    service = CalculatorService()

    @mcp.tool(
        description=(
            "Safely evaluate a mathematical expression. "
            "Supports: +, -, *, /, //, %, ** and functions: "
            "abs, round, sqrt, ceil, floor, log, log2, log10, sin, cos, tan. "
            "Constants: pi, e, inf."
        )
    )
    async def calculate(expression: str) -> str:
        """
        Args:
            expression: A math expression e.g. 'sqrt(2) * pi' or '(100 / 3) ** 2'
        """
        params = CalculatorInput(expression=expression)

        await rate_limiter.check(key="calculate")

        log.info("tool.calculate.called", expression=params.expression)

        try:
            result = await service.evaluate(params.expression)
            return result.model_dump_json(indent=2)
        except ValueError as exc:
            # ValueError = user error (bad expression) — return as tool error, not server error
            log.warning("tool.calculate.invalid", expression=params.expression, error=str(exc))
            raise McpError(-32603, str(exc))
        except Exception as exc:
            log.error("tool.calculate.failed", error=str(exc), exc_info=True)
            raise McpError(-32603, "Calculation failed. Please try again.")