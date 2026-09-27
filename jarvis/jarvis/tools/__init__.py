"""Tool registry. Each tool module registers functions with a JSON schema.

A tool is a plain function taking keyword arguments and returning a string.
Errors are returned as strings prefixed with "Error:" and flagged is_error to Claude.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

ToolFn = Callable[..., str]


@dataclass
class Tool:
    name: str
    description: str
    fn: ToolFn
    properties: dict[str, Any] = field(default_factory=dict)
    required: list[str] = field(default_factory=list)

    def schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": self.properties,
                "required": self.required,
                "additionalProperties": False,
            },
        }


class Registry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(
        self,
        name: str,
        description: str,
        properties: dict[str, Any] | None = None,
        required: list[str] | None = None,
    ) -> Callable[[ToolFn], ToolFn]:
        def deco(fn: ToolFn) -> ToolFn:
            self._tools[name] = Tool(
                name=name,
                description=description,
                fn=fn,
                properties=properties or {},
                required=required or [],
            )
            return fn

        return deco

    def schemas(self) -> list[dict[str, Any]]:
        # Deterministic order keeps the prompt-cache prefix stable.
        return [self._tools[k].schema() for k in sorted(self._tools)]

    def names(self) -> list[str]:
        return sorted(self._tools)

    def call(self, name: str, raw_input: Any) -> tuple[str, bool]:
        """Run a tool. Returns (result_text, is_error)."""
        tool = self._tools.get(name)
        if tool is None:
            return f"Error: unknown tool '{name}'", True
        if isinstance(raw_input, str):
            try:
                raw_input = json.loads(raw_input)
            except json.JSONDecodeError as exc:
                return f"Error: invalid JSON input ({exc})", True
        if not isinstance(raw_input, dict):
            return "Error: tool input must be an object", True
        try:
            result = tool.fn(**raw_input)
        except TypeError as exc:
            return f"Error: bad arguments for {name}: {exc}", True
        except Exception as exc:  # noqa: BLE001 - surface any tool failure to the model
            return f"Error: {type(exc).__name__}: {exc}", True
        result = result if isinstance(result, str) else json.dumps(result, default=str)
        return result, result.startswith("Error:")


registry = Registry()

# Import tool modules so they register themselves.
from jarvis.tools import macos, notes, system  # noqa: E402,F401

__all__ = ["registry", "Registry", "Tool"]
