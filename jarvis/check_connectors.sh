#!/bin/bash
# Show what Jarvis can actually reach from this Mac. Run in a normal Terminal.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
AGENT_HOME="${AGENT_HOME:-$HOME/my-agent}"
command -v claude >/dev/null || { echo "claude is not installed."; exit 1; }
cd "$AGENT_HOME" || exit 1
echo "== Signed-in account and MCP servers (connectors added at claude.ai appear here when you are signed in with the same account)"
claude mcp list 2>&1 | head -40
echo
echo "== Connector policy file"
if [ -f .claude/settings.json ]; then
  python3 - <<'PY'
import json; s = json.load(open(".claude/settings.json")); p = s.get("permissions", {})
print(f"   allow rules: {len(p.get('allow', []))}   deny rules: {len(p.get('deny', []))}   extra folders: {p.get('additionalDirectories', [])}")
PY
else echo "   missing: run ./apply_updates.sh"; fi
cat <<'TXT'

If Gmail, Google Drive or Google Calendar are NOT listed above:
  1. Open Claude Code in this folder and run /login. Sign in with the SAME account as claude.ai.
  2. On claude.ai, Settings > Connectors: confirm Gmail, Google Drive and Google Calendar show Connected.
  3. Run this script again.
TXT
