"""System tools: clock, shell, filesystem reads."""

from __future__ import annotations

import shlex
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from jarvis.config import config
from jarvis.tools import registry

SHELL_TIMEOUT = 30


@registry.register(
    name="get_datetime",
    description=(
        "Current date and time in the user's timezone. Call this before any scheduling, "
        "date arithmetic or 'what day is it' question."
    ),
)
def get_datetime() -> str:
    now = datetime.now(ZoneInfo(config.timezone))
    return now.strftime(f"%A %d/%m/%Y %H:%M:%S %Z ({config.timezone})")


def _is_allowed(command: str) -> bool:
    if config.shell_unrestricted:
        return True
    cmd = command.strip()
    return any(cmd == p or cmd.startswith(p + " ") for p in config.shell_allowlist)


@registry.register(
    name="run_shell",
    description=(
        "Run a shell command on the Mac and return stdout/stderr. Only allow-listed "
        "read-only commands run without confirmation; anything else is refused. "
        "Prefer dedicated tools (calendar, reminders, apps) where they exist."
    ),
    properties={
        "command": {"type": "string", "description": "The exact command line to execute."}
    },
    required=["command"],
)
def run_shell(command: str) -> str:
    if not _is_allowed(command):
        return (
            "Error: command not in allowlist. Allowed prefixes: "
            + ", ".join(config.shell_allowlist)
            + ". Ask the user to run it manually or to extend JARVIS_SHELL_ALLOWLIST."
        )
    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=SHELL_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {SHELL_TIMEOUT}s"
    out = proc.stdout.strip()
    err = proc.stderr.strip()
    parts = []
    if out:
        parts.append(out[:8000])
    if err:
        parts.append("stderr: " + err[:2000])
    parts.append(f"exit code: {proc.returncode}")
    return "\n".join(parts)


@registry.register(
    name="read_file",
    description="Read a text file from the Mac (UTF-8). Returns at most 20,000 characters.",
    properties={"path": {"type": "string", "description": "Absolute or ~-relative path."}},
    required=["path"],
)
def read_file(path: str) -> str:
    p = Path(path).expanduser()
    if not p.is_file():
        return f"Error: no such file {p}"
    try:
        return p.read_text(encoding="utf-8", errors="replace")[:20000]
    except OSError as exc:
        return f"Error: {exc}"


@registry.register(
    name="list_directory",
    description="List entries in a directory on the Mac.",
    properties={"path": {"type": "string", "description": "Absolute or ~-relative path."}},
    required=["path"],
)
def list_directory(path: str) -> str:
    p = Path(path).expanduser()
    if not p.is_dir():
        return f"Error: no such directory {p}"
    entries = sorted(p.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
    lines = [("[dir]  " if e.is_dir() else "       ") + e.name for e in entries[:500]]
    return "\n".join(lines) or "(empty)"


def quote(s: str) -> str:
    return shlex.quote(s)
