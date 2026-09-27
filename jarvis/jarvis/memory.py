"""Persistent storage: conversation history (SQLite) and long-term notes (Markdown)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jarvis.config import config

MAX_HISTORY_MESSAGES = 40  # messages kept in the live context window


class Memory:
    def __init__(self, db_path: Path | None = None, notes_path: Path | None = None) -> None:
        self.db_path = db_path or config.db_path
        self.notes_path = notes_path or config.notes_path
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session TEXT NOT NULL,
                ts TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    # ---- conversation history -------------------------------------------------

    def append(self, session: str, role: str, content: Any) -> None:
        self._conn.execute(
            "INSERT INTO messages (session, ts, role, content) VALUES (?, ?, ?, ?)",
            (session, datetime.now(timezone.utc).isoformat(), role, json.dumps(content, default=_jsonable)),
        )
        self._conn.commit()

    def history(self, session: str, limit: int = MAX_HISTORY_MESSAGES) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT role, content FROM messages WHERE session = ? ORDER BY id DESC LIMIT ?",
            (session, limit),
        ).fetchall()
        rows.reverse()
        messages = [{"role": role, "content": json.loads(content)} for role, content in rows]
        return _trim_to_user_start(messages)

    def clear(self, session: str) -> None:
        self._conn.execute("DELETE FROM messages WHERE session = ?", (session,))
        self._conn.commit()

    # ---- long-term notes --------------------------------------------------------

    def read_notes(self) -> str:
        if not self.notes_path.exists():
            return ""
        return self.notes_path.read_text(encoding="utf-8")

    def add_note(self, text: str) -> None:
        stamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        with self.notes_path.open("a", encoding="utf-8") as fh:
            fh.write(f"- [{stamp}] {text.strip()}\n")

    def replace_notes(self, text: str) -> None:
        self.notes_path.write_text(text, encoding="utf-8")


def _trim_to_user_start(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The API requires the first message to be a user turn and tool_result blocks to
    follow their tool_use. Drop leading messages until we start on a plain user text turn."""
    while messages:
        first = messages[0]
        if first["role"] != "user":
            messages.pop(0)
            continue
        content = first["content"]
        if isinstance(content, list) and any(
            isinstance(b, dict) and b.get("type") == "tool_result" for b in content
        ):
            messages.pop(0)
            continue
        break
    return messages


def _jsonable(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return str(obj)
