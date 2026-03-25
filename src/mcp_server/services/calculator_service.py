"""
CalculatorService — safe expression evaluator.

Uses Python's ast module to parse and evaluate mathematical expressions
without calling eval() on arbitrary user input.
"""

import ast
import math
import operator
import structlog
from pydantic import BaseModel

log = structlog.get_logger(__name__)

# Whitelist of safe operators
_OPERATORS: dict[type, object] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Whitelist of safe math functions
_FUNCTIONS: dict[str, object] = {
    "abs": abs,
    "round": round,
    "sqrt": math.sqrt,
    "ceil": math.ceil,
    "floor": math.floor,
    "log": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "pi": math.pi,
    "e": math.e,
    "inf": math.inf,
}


class CalculationResult(BaseModel):
    expression: str
    result: float | int
    result_str: str
    steps: list[str]


class CalculatorService:
    """Safe arithmetic expression evaluator using AST-based parsing."""

    async def evaluate(self, expression: str) -> CalculationResult:
        log.info("calculator.evaluate", expression=expression)

        cleaned = expression.strip()
        steps: list[str] = [f"Input: {cleaned}"]

        try:
            tree = ast.parse(cleaned, mode="eval")
        except SyntaxError as exc:
            raise ValueError(f"Invalid expression syntax: {exc}") from exc

        try:
            result = self._eval_node(tree.body)
        except ZeroDivisionError:
            raise ValueError("Division by zero")
        except (TypeError, KeyError) as exc:
            raise ValueError(f"Unsupported operation: {exc}") from exc

        # Round floats that are very close to integers
        if isinstance(result, float) and result.is_integer() and abs(result) < 1e15:
            result = int(result)

        steps.append(f"Result: {result}")

        log.info("calculator.result", expression=cleaned, result=result)

        return CalculationResult(
            expression=cleaned,
            result=result,
            result_str=str(result),
            steps=steps,
        )

    def _eval_node(self, node: ast.expr) -> float | int:
        match node:
            case ast.Constant(value=v) if isinstance(v, int | float):
                return v

            case ast.Name(id=name) if name in _FUNCTIONS:
                val = _FUNCTIONS[name]
                if isinstance(val, float | int):
                    return val
                raise ValueError(f"'{name}' is a function, not a value")

            case ast.BinOp(left=left, op=op, right=right):
                op_fn = _OPERATORS.get(type(op))
                if op_fn is None:
                    raise ValueError(f"Unsupported operator: {type(op).__name__}")
                l_val = self._eval_node(left)
                r_val = self._eval_node(right)
                return op_fn(l_val, r_val)  # type: ignore[operator]

            case ast.UnaryOp(op=op, operand=operand):
                op_fn = _OPERATORS.get(type(op))
                if op_fn is None:
                    raise ValueError(f"Unsupported unary operator: {type(op).__name__}")
                return op_fn(self._eval_node(operand))  # type: ignore[operator]

            case ast.Call(func=ast.Name(id=name), args=args, keywords=[]):
                fn = _FUNCTIONS.get(name)
                if fn is None or not callable(fn):
                    raise ValueError(f"Unknown function: {name}")
                evaluated_args = [self._eval_node(a) for a in args]
                return fn(*evaluated_args)  # type: ignore[operator]

            case _:
                raise ValueError(
                    f"Unsupported expression type: {type(node).__name__}. "
                    "Only arithmetic operations and whitelisted math functions are allowed."
                )