"""Long-term memory tools backed by data/memory.md."""

from __future__ import annotations

from jarvis.memory import Memory
from jarvis.tools import registry

_memory: Memory | None = None


def _mem() -> Memory:
    global _memory
    if _memory is None:
        _memory = Memory()
    return _memory


@registry.register(
    name="remember",
    description=(
        "Save a durable fact or preference about the user to long-term memory "
        "(e.g. 'Kids BJJ class is Tuesday and Thursday 17:30'). One fact per call."
    ),
    properties={"fact": {"type": "string"}},
    required=["fact"],
)
def remember(fact: str) -> str:
    _mem().add_note(fact)
    return "Saved."


@registry.register(
    name="recall",
    description="Read everything in long-term memory. Use when a question may depend on stored facts.",
)
def recall() -> str:
    text = _mem().read_notes().strip()
    return text or "Long-term memory is empty."
