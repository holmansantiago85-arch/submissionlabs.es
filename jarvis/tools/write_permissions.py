"""Write Jarvis's connector policy into ~/my-agent/.claude/settings.json (merge, never replace).

Reads are allowed silently so the voice line never stops to ask before looking something up.
Anything that sends, deletes, shares or edits is denied outright. Everything not listed
(labels, creating files or events, ...) falls through to ask-first.

claude.ai connectors reach Claude Code as MCP servers. The server prefix differs by surface
(`Gmail` in some, `claude_ai_Gmail` in Claude Code), so rules are written for both. A rule for
a server that is not connected does nothing. Fail-safe: an unrecognised name is simply asked about.
"""
import json, os, sys
from pathlib import Path

home = Path(os.environ.get("AGENT_HOME", Path.home() / "my-agent"))
extra = [d for d in sys.argv[1:] if d]

SERVERS = {
    "Gmail": {
        "allow": ["get_draft", "get_message", "get_thread", "list_drafts", "list_labels",
                  "search_threads", "create_draft", "update_draft"],
        "deny": ["send_message", "reply", "forward", "trash_message", "trash_thread",
                 "untrash_message", "untrash_thread", "delete_draft", "delete_label",
                 "mark_message_spam", "mark_thread_spam", "unmark_message_spam", "unmark_thread_spam"],
    },
    "Google_Drive": {
        "allow": ["download_file_content", "get_file_metadata", "get_file_permissions",
                  "list_recent_files", "read_file_content", "search_files"],
        "deny": ["share_file", "trash_file", "update_file"],
    },
    "Google_Calendar": {
        "allow": ["get_event", "list_calendars", "list_events", "search_events", "suggest_time"],
        "deny": ["delete_event", "update_event", "respond_to_event"],
    },
    "Dropbox": {
        "allow": ["check_job_status", "download_link", "fetch", "file_preview", "get_file_metadata",
                  "get_file_request", "get_shared_link_metadata", "list_file_requests", "list_folder",
                  "list_shared_links", "search", "who_am_i"],
        "deny": ["delete", "move", "create_shared_link"],
    },
}
PREFIXES = ("mcp__", "mcp__claude_ai_")

allow, deny = [], []
for server, pol in SERVERS.items():
    for pre in PREFIXES:
        allow += [f"{pre}{server}__{t}" for t in pol["allow"]]
        deny += [f"{pre}{server}__{t}" for t in pol["deny"]]

path = home / ".claude" / "settings.json"
path.parent.mkdir(parents=True, exist_ok=True)
cur = json.loads(path.read_text()) if path.exists() else {}
perms = cur.setdefault("permissions", {})

def union(key, items):
    have = perms.get(key, [])
    perms[key] = have + [i for i in items if i not in have]

union("allow", allow)
union("deny", deny)
union("additionalDirectories", extra)
path.write_text(json.dumps(cur, indent=2) + "\n")
print(f"   connector policy written: {path} ({len(allow)} read rules, {len(deny)} deny rules, {len(perms['additionalDirectories'])} extra folders)")
