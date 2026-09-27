"""The Claude-powered reasoning loop.

One `Brain.ask()` call = one user turn. Internally it loops while Claude requests
client-side tools, executes them via the registry, and returns the final spoken text.
Server-side web search runs on Anthropic's side and needs no handling here.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

import anthropic

from jarvis.config import config
from jarvis.memory import Memory
from jarvis.tools import registry

log = logging.getLogger("jarvis.brain")

MAX_TOOL_ROUNDS = 12

SYSTEM_PROMPT = """You are {name}, a personal assistant running locally on {user}'s Mac.

Style:
- Speak like a capable chief of staff: direct, factual, brief. No filler, no emotional language.
- Answers are spoken aloud, so use short sentences and no markdown, bullet symbols or code fences.
- Dates in DD/MM/YYYY. Times in 24-hour clock, Spain time ({tz}) unless told otherwise.
- If Spanish is requested, give English first, then formal European Spanish.

Operating rules:
- Call get_datetime before anything involving dates, days of the week or scheduling.
- Use tools to act rather than describing what the user could do.
- Confirm before sending messages, creating calendar events with uncertain details, or running shell commands that change state.
- If a tool returns an error, say what failed in one sentence and offer the next step.
- When the user states a durable fact or preference, store it with the remember tool.
- Keep spoken replies under 60 words unless the user asks for detail.

Long-term memory:
{notes}
"""


class Brain:
    def __init__(
        self,
        memory: Memory | None = None,
        session: str = "default",
        on_text: Callable[[str], None] | None = None,
        on_tool: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> None:
        self.client = anthropic.Anthropic()
        self.memory = memory or Memory()
        self.session = session
        self.on_text = on_text
        self.on_tool = on_tool

    # ---- public --------------------------------------------------------------------

    def ask(self, user_text: str) -> str:
        self.memory.append(self.session, "user", user_text)
        messages = self.memory.history(self.session)

        final_text = ""
        for _ in range(MAX_TOOL_ROUNDS):
            response = self._create(messages)

            if response.stop_reason == "refusal":
                detail = ""
                if response.stop_details is not None:
                    detail = f" ({response.stop_details.category})"
                final_text = f"I can't help with that request{detail}."
                self.memory.append(self.session, "assistant", [{"type": "text", "text": final_text}])
                return final_text

            content = [b.model_dump(exclude_none=True) for b in response.content]
            # Fallback blocks describe which model served the turn; they are not
            # replayable content, so drop them from stored history.
            content = [b for b in content if b.get("type") != "fallback"]
            self.memory.append(self.session, "assistant", content)
            messages.append({"role": "assistant", "content": content})

            text_parts = [b.text for b in response.content if b.type == "text"]
            if text_parts:
                final_text = "\n".join(text_parts).strip()

            tool_uses = [b for b in response.content if b.type == "tool_use"]

            if response.stop_reason == "pause_turn":
                continue

            if response.stop_reason == "max_tokens" and tool_uses:
                # Truncated mid tool call: inputs are unreliable. Do not execute.
                final_text = final_text or "My response was cut off. Please ask again."
                break

            if not tool_uses:
                break

            results = []
            for tu in tool_uses:
                if self.on_tool:
                    self.on_tool(tu.name, tu.input)
                out, is_err = registry.call(tu.name, tu.input)
                log.info("tool %s -> %s", tu.name, out[:200].replace("\n", " "))
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tu.id,
                        "content": out,
                        "is_error": is_err,
                    }
                )
            self.memory.append(self.session, "user", results)
            messages.append({"role": "user", "content": results})
        else:
            final_text = final_text or "I hit my tool-use limit for this request."

        if self.on_text and final_text:
            self.on_text(final_text)
        return final_text

    def reset(self) -> None:
        self.memory.clear(self.session)

    # ---- internals -----------------------------------------------------------------

    def _system(self) -> list[dict[str, Any]]:
        notes = self.memory.read_notes().strip() or "(empty)"
        return [
            {
                "type": "text",
                "text": SYSTEM_PROMPT.format(
                    name=config.name, user=config.user_name, tz=config.timezone, notes=notes
                ),
                "cache_control": {"type": "ephemeral"},
            }
        ]

    def _tools(self) -> list[dict[str, Any]]:
        tools: list[dict[str, Any]] = [
            {
                "type": "web_search_20260209",
                "name": "web_search",
                "max_uses": config.web_search_max_uses,
                "user_location": {
                    "type": "approximate",
                    "country": "ES",
                    "timezone": config.timezone,
                },
            }
        ]
        tools.extend(registry.schemas())
        return tools

    def _create(self, messages: list[dict[str, Any]]) -> Any:
        kwargs: dict[str, Any] = dict(
            model=config.model,
            max_tokens=config.max_tokens,
            system=self._system(),
            tools=self._tools(),
            messages=messages,
            thinking={"type": "adaptive"},
            output_config={"effort": config.effort},
        )
        try:
            if config.fallbacks:
                return self.client.beta.messages.create(
                    betas=["server-side-fallback-2026-07-01"],
                    fallbacks="default",
                    **kwargs,
                )
            return self.client.messages.create(**kwargs)
        except anthropic.AuthenticationError:
            raise SystemExit("ANTHROPIC_API_KEY is missing or invalid. Set it in .env.")
        except anthropic.RateLimitError as exc:
            wait = exc.response.headers.get("retry-after", "60")
            raise RuntimeError(f"Rate limited. Retry in {wait}s.") from exc
        except anthropic.APIStatusError as exc:
            raise RuntimeError(f"API error {exc.status_code}: {exc.message}") from exc
        except anthropic.APIConnectionError as exc:
            raise RuntimeError("Network error reaching the Claude API.") from exc
