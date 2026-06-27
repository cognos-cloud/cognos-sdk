"""
@tool decorator — register any Python function as a Cognos Cloud tool.

Usage:
    from cognos import tool

    @tool(name="send-invoice", description="Sends an invoice via Stripe")
    def send_invoice(customer_id: str, amount_usd: float) -> str:
        # your implementation
        return f"Invoice sent to {customer_id} for ${amount_usd}"
"""

from __future__ import annotations

import inspect
from typing import Callable


def tool(
    name: str,
    description: str = "",
) -> Callable:
    """
    Decorator that registers a Python function as a tool available to agents.

    The decorated function must:
      - Accept only str, int, float, or bool parameters
      - Return a str (the tool result passed back to the LLM)
      - Be importable from the project root

    Args:
        name:        Tool identifier used in the Agent tools list.
        description: Plain-language description of what the tool does.
                     This is shown to the LLM when it decides whether to call it.

    Example:
        @tool(name="get-price", description="Returns the current SOL price in USD")
        def get_sol_price() -> str:
            response = requests.get("https://api.coingecko.com/...")
            return str(response.json()["solana"]["usd"])
    """

    def decorator(fn: Callable) -> Callable:
        sig = inspect.signature(fn)

        fn._cognos_tool_name        = name
        fn._cognos_tool_description = description
        fn._cognos_tool_schema      = _build_schema(fn, sig)
        fn._is_cognos_tool          = True

        return fn

    return decorator


def _build_schema(fn: Callable, sig: inspect.Signature) -> dict:
    """Build a JSON schema for the tool parameters from type annotations."""
    type_map = {
        str:   "string",
        int:   "integer",
        float: "number",
        bool:  "boolean",
    }

    properties = {}
    required   = []

    for param_name, param in sig.parameters.items():
        annotation = param.annotation
        json_type  = type_map.get(annotation, "string")

        properties[param_name] = {"type": json_type}

        if param.default is inspect.Parameter.empty:
            required.append(param_name)

    return {
        "type":       "object",
        "properties": properties,
        "required":   required,
    }
