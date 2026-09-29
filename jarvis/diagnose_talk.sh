#!/bin/bash
# Diagnose push-to-talk. Run from a normal Terminal window.
AGENT_HOME="${AGENT_HOME:-$HOME/my-agent}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="$AGENT_HOME/backtalk/.venv/bin/python"
[ -x "$PY" ] || { echo "backtalk's Python not found at $PY. Run install_mac.sh first."; exit 1; }
exec "$PY" "$HERE/tools/diagnose_talk.py"
