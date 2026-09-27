"""macOS integration via `open` and AppleScript (osascript).

Everything here is a no-op error on non-macOS hosts so the text mode still runs
elsewhere for development.
"""

from __future__ import annotations

import platform
import subprocess

from jarvis.tools import registry

IS_MAC = platform.system() == "Darwin"


def osascript(script: str, timeout: int = 30) -> str:
    if not IS_MAC:
        return "Error: AppleScript is only available on macOS"
    try:
        proc = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return "Error: AppleScript timed out"
    if proc.returncode != 0:
        return f"Error: {proc.stderr.strip() or 'osascript failed'}"
    return proc.stdout.strip() or "OK"


def _as_str(s: str) -> str:
    """Escape a Python string for embedding inside AppleScript double quotes."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


@registry.register(
    name="open_app",
    description="Launch or bring to front a macOS application by name, e.g. 'Safari', 'Music'.",
    properties={"name": {"type": "string"}},
    required=["name"],
)
def open_app(name: str) -> str:
    if not IS_MAC:
        return "Error: only available on macOS"
    proc = subprocess.run(["open", "-a", name], capture_output=True, text=True)
    return "OK" if proc.returncode == 0 else f"Error: {proc.stderr.strip()}"


@registry.register(
    name="open_url",
    description="Open a URL in the default browser.",
    properties={"url": {"type": "string"}},
    required=["url"],
)
def open_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        return "Error: URL must start with http:// or https://"
    if not IS_MAC:
        return "Error: only available on macOS"
    proc = subprocess.run(["open", url], capture_output=True, text=True)
    return "OK" if proc.returncode == 0 else f"Error: {proc.stderr.strip()}"


@registry.register(
    name="calendar_events",
    description=(
        "List events from the macOS Calendar app for the next N days (default 1 = today). "
        "Returns one line per event: start, end, calendar, title."
    ),
    properties={
        "days": {"type": "integer", "description": "How many days ahead, 1-30.", "minimum": 1, "maximum": 30}
    },
    required=["days"],
)
def calendar_events(days: int) -> str:
    days = max(1, min(int(days), 30))
    script = f"""
    set startDate to current date
    set time of startDate to 0
    set endDate to startDate + ({days} * days)
    set output to ""
    tell application "Calendar"
        repeat with cal in calendars
            set evs to (every event of cal whose start date >= startDate and start date < endDate)
            repeat with ev in evs
                set output to output & (start date of ev as string) & " | " & (end date of ev as string) & " | " & (name of cal) & " | " & (summary of ev) & linefeed
            end repeat
        end repeat
    end tell
    return output
    """
    result = osascript(script, timeout=60)
    return result if result and result != "OK" else "No events in that window."


@registry.register(
    name="create_calendar_event",
    description=(
        "Create an event in the macOS Calendar app. Dates must be ISO 8601 local time, "
        "e.g. 2026-10-03T09:30. Call get_datetime first to resolve relative dates."
    ),
    properties={
        "title": {"type": "string"},
        "start": {"type": "string", "description": "ISO 8601 local start, YYYY-MM-DDTHH:MM"},
        "end": {"type": "string", "description": "ISO 8601 local end, YYYY-MM-DDTHH:MM"},
        "calendar": {"type": "string", "description": "Calendar name. Use 'Home' if unsure."},
        "notes": {"type": "string"},
    },
    required=["title", "start", "end", "calendar", "notes"],
)
def create_calendar_event(title: str, start: str, end: str, calendar: str, notes: str) -> str:
    from datetime import datetime

    try:
        s = datetime.fromisoformat(start)
        e = datetime.fromisoformat(end)
    except ValueError as exc:
        return f"Error: bad date ({exc})"
    if e <= s:
        return "Error: end must be after start"

    def as_date(var: str, d: datetime) -> str:
        # Set day to 1 first so changing month/year never overflows (e.g. 31 -> Feb).
        return (
            f"set {var} to current date\n"
            f"set day of {var} to 1\n"
            f"set year of {var} to {d.year}\n"
            f"set month of {var} to {d.month}\n"
            f"set day of {var} to {d.day}\n"
            f"set time of {var} to {d.hour * 3600 + d.minute * 60}\n"
        )

    script = f"""
    {as_date("s", s)}
    {as_date("e", e)}
    tell application "Calendar"
        tell calendar {_as_str(calendar)}
            make new event with properties {{summary:{_as_str(title)}, start date:s, end date:e, description:{_as_str(notes)}}}
        end tell
    end tell
    return "Created"
    """
    return osascript(script, timeout=60)


@registry.register(
    name="create_reminder",
    description="Add a reminder to the macOS Reminders app. Optional due date in ISO 8601 local time.",
    properties={
        "title": {"type": "string"},
        "due": {"type": "string", "description": "YYYY-MM-DDTHH:MM or empty string for none"},
        "list_name": {"type": "string", "description": "Reminders list. Use 'Reminders' if unsure."},
    },
    required=["title", "due", "list_name"],
)
def create_reminder(title: str, due: str, list_name: str) -> str:
    props = f"name:{_as_str(title)}"
    due_setup = ""
    if due:
        from datetime import datetime

        try:
            d = datetime.fromisoformat(due)
        except ValueError as exc:
            return f"Error: bad due date ({exc})"
        due_setup = f"""
        set d to current date
        set day of d to 1
        set year of d to {d.year}
        set month of d to {d.month}
        set day of d to {d.day}
        set time of d to {d.hour * 3600 + d.minute * 60}
        """
        props += ", due date:d, remind me date:d"
    script = f"""
    {due_setup}
    tell application "Reminders"
        tell list {_as_str(list_name)}
            make new reminder with properties {{{props}}}
        end tell
    end tell
    return "Created"
    """
    return osascript(script)


@registry.register(
    name="send_imessage",
    description=(
        "Send an iMessage/SMS via the Messages app to a phone number or Apple ID. "
        "Only use when the user explicitly asks to send a message and has confirmed the text."
    ),
    properties={"recipient": {"type": "string"}, "text": {"type": "string"}},
    required=["recipient", "text"],
)
def send_imessage(recipient: str, text: str) -> str:
    script = f"""
    tell application "Messages"
        set targetService to 1st account whose service type = iMessage
        set targetBuddy to participant {_as_str(recipient)} of targetService
        send {_as_str(text)} to targetBuddy
    end tell
    return "Sent"
    """
    return osascript(script)


@registry.register(
    name="set_volume",
    description="Set system output volume, 0-100.",
    properties={"level": {"type": "integer", "minimum": 0, "maximum": 100}},
    required=["level"],
)
def set_volume(level: int) -> str:
    level = max(0, min(int(level), 100))
    return osascript(f"set volume output volume {level}")


@registry.register(
    name="notify",
    description="Show a macOS notification banner.",
    properties={"title": {"type": "string"}, "message": {"type": "string"}},
    required=["title", "message"],
)
def notify(title: str, message: str) -> str:
    return osascript(f"display notification {_as_str(message)} with title {_as_str(title)}")
