#!/bin/bash
# Apply this bundle's latest identity, configs and faces to an EXISTING Jarvis
# install (one made by install_mac.sh). Run from the jarvis/ folder after
# `git pull`. Backs up what it replaces; never touches the vault.
#
#   ./apply_updates.sh            everything
#   ./apply_updates.sh --keep-claude-md   leave CLAUDE.md alone (configs + faces only)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
AGENT_HOME="${AGENT_HOME:-$HOME/my-agent}"
VAULT_PATH="${VAULT_PATH:-$HOME/HQ}"
KEEP_CLAUDE=0
[ "${1:-}" = "--keep-claude-md" ] && KEEP_CLAUDE=1
STAMP="$(date +%Y%m%d-%H%M%S)"
note() { printf '   %s\n' "$*"; }
fill() { sed -e "s#__AGENT_HOME__#$AGENT_HOME#g" -e "s#__VAULT_PATH__#$VAULT_PATH#g" "$1" > "$2"; }

[ -d "$AGENT_HOME" ] || { echo "No agent home at $AGENT_HOME. Run install_mac.sh first."; exit 1; }
echo "== Updating Jarvis in $AGENT_HOME"

# 1. Boot config (identity + rules). Backup, then replace.
if [ "$KEEP_CLAUDE" = 0 ]; then
  [ -f "$AGENT_HOME/CLAUDE.md" ] && cp "$AGENT_HOME/CLAUDE.md" "$AGENT_HOME/CLAUDE.md.bak-$STAMP"
  fill "$HERE/home/CLAUDE.md" "$AGENT_HOME/CLAUDE.md"
  note "CLAUDE.md replaced (backup: CLAUDE.md.bak-$STAMP). If Jarvis had added rules to 'Make it yours', copy them back from the backup."
fi

# 2. Faces: every folder in faces/ goes into ai-visualizer/faces/
if [ -d "$AGENT_HOME/ai-visualizer/faces" ]; then
  for f in "$HERE"/faces/*/; do
    n="$(basename "$f")"
    rm -rf "$AGENT_HOME/ai-visualizer/faces/$n"
    cp -R "$f" "$AGENT_HOME/ai-visualizer/faces/$n"
    note "face installed: $n"
  done
fi

# 3. Configs: merge this bundle's keys over the existing file (existing extra keys survive).
merge_json() {  # merge_json <bundle-src> <target>
  local tmp; tmp="$(mktemp)"; fill "$1" "$tmp"
  python3 - "$tmp" "$2" <<'PY'
import json, sys, shutil, os
src, dst = sys.argv[1], sys.argv[2]
new = json.load(open(src))
old = json.load(open(dst)) if os.path.exists(dst) else {}
if os.path.exists(dst): shutil.copy(dst, dst + ".bak")
# keep the person's ElevenLabs choice if they already enabled it
if old.get("elevenlabs", {}).get("enabled"):
    new["elevenlabs"] = old["elevenlabs"]
for k in ("permission_mode", "mic_mode", "resume_last_session", "voice", "speed", "mic_device"):
    if k in old: new[k] = old[k]          # settings the voice console may have saved
old.update(new)
json.dump(old, open(dst, "w"), indent=2); open(dst, "a").write("\n")
print("   merged:", dst.split("/")[-2] + "/" + dst.split("/")[-1])
PY
  rm -f "$tmp"
}
merge_json "$HERE/home/backtalk.json"      "$AGENT_HOME/backtalk/backtalk.json"
merge_json "$HERE/home/ai-visualizer.json" "$AGENT_HOME/ai-visualizer/ai-visualizer.json"
[ -d "$AGENT_HOME/barehands" ] && merge_json "$HERE/home/barehands.json" "$AGENT_HOME/barehands/barehands.json"

cat <<TXT

== Done ==
Restart the stack for the changes to land: Ctrl-C the running "Talk to Jarvis" window,
then double-click it again. Text sessions pick up the new CLAUDE.md on their next launch.
Other faces are one line away: set "face" in ai-visualizer/ai-visualizer.json to
bridge | board | radial | rain | neural, or open http://127.0.0.1:8790/ for the gallery.
TXT
