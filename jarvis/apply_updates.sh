#!/bin/bash
# Apply this bundle's latest identity, configs, faces, jobs and connector policy to an
# EXISTING Jarvis install. Run from the jarvis/ folder after `git pull`. Backs up what it
# replaces. Never overwrites or deletes anything in the vault.
#
#   ./apply_updates.sh                    everything
#   ./apply_updates.sh --keep-claude-md   leave CLAUDE.md alone
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
  note "CLAUDE.md replaced (backup: CLAUDE.md.bak-$STAMP). Rules Jarvis added himself are in the backup."
fi

# 2. Faces
if [ -d "$AGENT_HOME/ai-visualizer/faces" ]; then
  for f in "$HERE"/faces/*/; do
    n="$(basename "$f")"; rm -rf "$AGENT_HOME/ai-visualizer/faces/$n"; cp -R "$f" "$AGENT_HOME/ai-visualizer/faces/$n"; note "face installed: $n"
  done
fi

# 3. Configs: bundle keys win, except settings the person or the voice console chose.
merge_json() {  # merge_json <bundle-src> <target>
  local tmp; tmp="$(mktemp)"; fill "$1" "$tmp"
  python3 - "$tmp" "$2" <<'PY'
import json, sys, shutil, os
src, dst = sys.argv[1], sys.argv[2]
new = json.load(open(src))
old = json.load(open(dst)) if os.path.exists(dst) else {}
if os.path.exists(dst): shutil.copy(dst, dst + ".bak")
if old.get("elevenlabs", {}).get("enabled"): new["elevenlabs"] = old["elevenlabs"]
for k in ("permission_mode", "mic_mode", "resume_last_session", "voice", "speed", "mic_device", "show_usage"):
    if k in old: new[k] = old[k]
# keep a talk key the person chose, but replace "home": Apple keyboards have no Home key
if old.get("ptt_key") not in (None, "home"): new["ptt_key"] = old["ptt_key"]
# folder lists are unioned so folders added later are never lost
if isinstance(new.get("extra_dirs"), list):
    new["extra_dirs"] = new["extra_dirs"] + [d for d in old.get("extra_dirs", []) if d not in new["extra_dirs"]]
old.update(new)
json.dump(old, open(dst, "w"), indent=2); open(dst, "a").write("\n")
print("   merged:", dst.split("/")[-2] + "/" + dst.split("/")[-1])
PY
  rm -f "$tmp"
}
merge_json "$HERE/home/backtalk.json"      "$AGENT_HOME/backtalk/backtalk.json"
merge_json "$HERE/home/ai-visualizer.json" "$AGENT_HOME/ai-visualizer/ai-visualizer.json"
[ -d "$AGENT_HOME/barehands" ] && merge_json "$HERE/home/barehands.json" "$AGENT_HOME/barehands/barehands.json"

# 4. Vault additions: new notes only, never overwrite. Then make sure the indexes list them.
if [ -d "$VAULT_PATH" ]; then
  added=0
  for rel in "07 - Resources/Connectors.md" "07 - Resources/Projects Index.md" \
             "07 - Resources/Jobs/Life Briefing.md" "07 - Resources/Jobs/Inbox Triage.md" \
             "07 - Resources/Jobs/Drive Reader.md" "07 - Resources/Jobs/Claude History Import.md"; do
    if [ ! -e "$VAULT_PATH/$rel" ]; then
      mkdir -p "$(dirname "$VAULT_PATH/$rel")"; fill "$HERE/vault/$rel" "$VAULT_PATH/$rel"; added=$((added+1))
    fi
  done
  note "vault: $added new notes added (nothing overwritten)"
  python3 - "$VAULT_PATH" <<'PY'
import pathlib, sys
v = pathlib.Path(sys.argv[1])
idx = v / "07 - Resources" / "Resources.md"
if idx.exists():
    t = idx.read_text()
    lines = ["- [[Connectors]] — what each connected source may read and change",
             "- [[Projects Index]] — local project folders Jarvis can work in",
             "- [[Jobs/Life Briefing]] — Job: learn what is going on and keep Current Situation up to date",
             "- [[Jobs/Inbox Triage]] — Job: read, sort and draft replies, never send",
             "- [[Jobs/Drive Reader]] — Job: find, read and summarise files",
             "- [[Jobs/Claude History Import]] — Job: bring Claude Code projects and claude.ai exports into the vault"]
    missing = [l for l in lines if l.split("]]")[0] not in t]
    if missing and "## Notes in this folder\n" in t:
        t = t.replace("## Notes in this folder\n", "## Notes in this folder\n" + "\n".join(missing) + "\n", 1); idx.write_text(t)
ap = v / "Active Priorities.md"
if ap.exists() and "Life Briefing" not in ap.read_text():
    t = ap.read_text()
    item = "- [ ] Run the Life Briefing job so Jarvis learns what is going on: calendar, inbox, Drive, Claude projects. (meta)\n"
    t = t.replace("### Completed Tasks", item + "\n### Completed Tasks", 1) if "### Completed Tasks" in t else t + item
    ap.write_text(t)
PY
else
  note "vault not found at $VAULT_PATH: skipped"
fi

# 5. Connector policy (read-only) + project folders for the text session
EXTRA=()
[ -d "$HOME/submissionlabs.es" ] && EXTRA+=("$HOME/submissionlabs.es")
[ -d "$HOME/.claude/projects" ]  && EXTRA+=("$HOME/.claude/projects")
[ -d "$VAULT_PATH" ] && EXTRA+=("$VAULT_PATH")
AGENT_HOME="$AGENT_HOME" python3 "$HERE/tools/write_permissions.py" "${EXTRA[@]}"

cat <<TXT

== Done ==
Restart the stack: Ctrl-C the "Talk to Jarvis" window, then double-click it again.

Now check what Jarvis can reach:      ./check_connectors.sh
First job after that, say to Jarvis:  "Run the life briefing."
Talk key is Right Option. If it still misbehaves: ./diagnose_talk.sh
Hands-free instead of holding a key:  ./talk_config.sh mode open
TXT
