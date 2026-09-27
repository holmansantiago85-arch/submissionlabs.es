#!/bin/bash
# Jarvis installer for James's Mac mini.
#
# Assembles Jared Rhodenizer's fullstack-agent stack (memory, voice, face, hands)
# with James's identity, configs and vault already filled in, so the only
# interactive step left is the voice engine choice and the first hello.
#
# Repos (AGPL-3.0-or-later, (c) Jared Rhodenizer):
#   https://github.com/jaredrhod/fullstack-agent
#   https://github.com/jaredrhod/ai-memory-vault
#   https://github.com/jaredrhod/backtalk
#   https://github.com/jaredrhod/ai-visualizer
#   https://github.com/jaredrhod/barehands
#
# Usage:  ./install_mac.sh            full install
#         ./install_mac.sh --no-voice skip backtalk's model download (add later)
#         ./install_mac.sh --no-hands skip barehands
#         ./install_mac.sh --pin      check out the exact upstream commits this
#                                     bundle was validated against (30/08/2026)
#                                     instead of the latest main
#
# Env overrides: AGENT_HOME (default ~/my-agent), VAULT_PATH (default ~/HQ)
#
# Safe to re-run. Never overwrites a CLAUDE.md, config or vault that already exists.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
AGENT_HOME="${AGENT_HOME:-$HOME/my-agent}"
VAULT_PATH="${VAULT_PATH:-$HOME/HQ}"
WITH_VOICE=1
WITH_HANDS=1
PIN=0
for a in "$@"; do
  case "$a" in
    --no-voice) WITH_VOICE=0 ;;
    --no-hands) WITH_HANDS=0 ;;
    --pin)      PIN=1 ;;
    -h|--help) sed -n 2,20p "$0"; exit 0 ;;
  esac
done

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
IS_MAC=0; [ "$(uname -s)" = "Darwin" ] && IS_MAC=1

say_step() { printf '\n== %s\n' "$*"; }
note()     { printf '   %s\n' "$*"; }

# Replace the placeholders used in home/ and vault/ with the real paths.
fill() {  # fill <src> <dst>
  sed -e "s#__AGENT_HOME__#$AGENT_HOME#g" -e "s#__VAULT_PATH__#$VAULT_PATH#g" "$1" > "$2"
}

# ---------------------------------------------------------------- prerequisites
say_step "Prerequisites"
if [ "$IS_MAC" = 1 ]; then
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is required. Install it from https://brew.sh then re-run."; exit 1
  fi
  command -v git >/dev/null 2>&1 || brew install git
  if ! command -v claude >/dev/null 2>&1; then
    note "Installing Claude Code (native installer)"
    curl -fsSL https://claude.ai/install.sh | bash
    export PATH="$HOME/.local/bin:$PATH"
  fi
  command -v claude >/dev/null 2>&1 || { echo "claude not on PATH after install. Open a new terminal and re-run."; exit 1; }
  note "git, claude: ok"
else
  note "Not macOS: brew/claude/Obsidian/voice steps are skipped (dry run)."
  WITH_VOICE=0
fi

# ---------------------------------------------------------------- the repos
say_step "Agent home: $AGENT_HOME"
mkdir -p "$AGENT_HOME"
# Upstream commits this bundle was read and tested against (all dated 30/08/2026).
pinned_sha() {
  case "$1" in
    fullstack-agent)     echo 5bb159f47dbd6fa8f108651d0532a43aef16346b ;;
    ai-memory-vault)     echo 659bba9c8b351c937dd393b3042801d1ff1b502c ;;
    backtalk)            echo 84b3a6cd321060cabb74aad6ebe794621cf99bd3 ;;
    ai-visualizer)       echo 6921e1d ;;
    barehands)           echo eb23bed ;;
    ai-marketing-skills) echo 47b68a5 ;;
  esac
}
REPOS="fullstack-agent ai-memory-vault backtalk ai-visualizer"
[ "$WITH_HANDS" = 1 ] && REPOS="$REPOS barehands"
REPOS="$REPOS ai-marketing-skills"
for r in $REPOS; do
  if [ -d "$AGENT_HOME/$r/.git" ]; then
    note "$r: present"
  else
    note "$r: cloning"
    git clone -q "https://github.com/jaredrhod/$r" "$AGENT_HOME/$r"
    if [ "$PIN" = 1 ]; then
      git -C "$AGENT_HOME/$r" checkout -q "$(pinned_sha "$r")" && note "$r: pinned to validated commit"
    fi
  fi
done

# ---------------------------------------------------------------- identity + configs
say_step "Identity and configs"
if [ -f "$AGENT_HOME/CLAUDE.md" ]; then
  note "CLAUDE.md exists: kept. New version written to CLAUDE.md.new for comparison."
  fill "$HERE/home/CLAUDE.md" "$AGENT_HOME/CLAUDE.md.new"
else
  fill "$HERE/home/CLAUDE.md" "$AGENT_HOME/CLAUDE.md"
  note "CLAUDE.md written (Jarvis identity, James's rules, vault path)"
fi
if [ "$WITH_HANDS" = 0 ]; then
  # Drop the board block when barehands is not installed.
  python3 - "$AGENT_HOME/CLAUDE.md" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]); t = p.read_text()
t = re.sub(r"\n## The barehands board\n.*?(?=\n## )", "\n", t, flags=re.S)
p.write_text(t)
PY
fi

put_cfg() {  # put_cfg <repo> <file>
  if [ -f "$AGENT_HOME/$1/$2" ]; then note "$1/$2: exists, kept"
  else fill "$HERE/home/$2" "$AGENT_HOME/$1/$2"; note "$1/$2: written"; fi
}
put_cfg backtalk backtalk.json
put_cfg ai-visualizer ai-visualizer.json
[ "$WITH_HANDS" = 1 ] && put_cfg barehands barehands.json
if [ "$WITH_HANDS" = 0 ] && [ -f "$AGENT_HOME/backtalk/backtalk.json" ]; then
  python3 - "$AGENT_HOME/backtalk/backtalk.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p)); d.pop("barehands_state_dir", None)
json.dump(d, open(p, "w"), indent=2); open(p, "a").write("\n")
PY
fi

# ---------------------------------------------------------------- the vault
say_step "Vault: $VAULT_PATH"
if [ -e "$VAULT_PATH/VAULT-INDEX.md" ]; then
  note "vault exists: kept untouched"
else
  mkdir -p "$VAULT_PATH"
  (cd "$HERE/vault" && find . -type d -exec mkdir -p "$VAULT_PATH/{}" \;)
  (cd "$HERE/vault" && find . -type f | while IFS= read -r f; do fill "$f" "$VAULT_PATH/$f"; done)
  note "seeded: index, priorities, 8 folders, starter Jobs"
fi

# ---------------------------------------------------------------- marketing playbook
say_step "Marketing playbook (ai-marketing-skills)"
MK_SRC="$AGENT_HOME/ai-marketing-skills/jaredrhod-marketing"
MK_VAULT="$VAULT_PATH/07 - Resources/Marketing"
if [ -d "$MK_SRC" ]; then
  mkdir -p "$MK_VAULT"
  n=0
  for f in "$MK_SRC"/*.md; do
    b="$(basename "$f")"
    [ "$b" = "SKILL.md" ] && continue           # the index note replaces it in a vault
    if [ ! -f "$MK_VAULT/$b" ]; then cp "$f" "$MK_VAULT/$b"; n=$((n+1)); fi
  done
  note "vault: $n playbook files added to 07 - Resources/Marketing (index note already there)"
  SKILL_DIR="$HOME/.claude/skills/jaredrhod-marketing"
  if [ ! -d "$SKILL_DIR" ]; then
    mkdir -p "$HOME/.claude/skills"
    cp -R "$MK_SRC" "$SKILL_DIR"
    note "skill: installed at ~/.claude/skills/jaredrhod-marketing (every project)"
  else
    note "skill: present"
  fi
else
  note "ai-marketing-skills not found; skipped"
fi

# ---------------------------------------------------------------- Obsidian
if [ "$IS_MAC" = 1 ]; then
  say_step "Obsidian"
  if [ ! -d /Applications/Obsidian.app ] && [ ! -d "$HOME/Applications/Obsidian.app" ]; then
    note "installing Obsidian"
    brew install --cask obsidian
  else
    note "installed"
  fi
  # Register the vault so Obsidian opens straight into it. Merge, never replace.
  OBS_DIR="$HOME/Library/Application Support/obsidian"
  mkdir -p "$OBS_DIR"
  [ -f "$OBS_DIR/obsidian.json" ] && cp "$OBS_DIR/obsidian.json" "$OBS_DIR/obsidian.json.bak"
  python3 - "$OBS_DIR/obsidian.json" "$VAULT_PATH" <<'PY'
import json, os, secrets, sys, time
cfg_path, vault = sys.argv[1], os.path.realpath(sys.argv[2])
data = {}
if os.path.exists(cfg_path):
    try:
        data = json.load(open(cfg_path))
    except json.JSONDecodeError:
        data = {}
vaults = data.setdefault("vaults", {})
if not any(os.path.realpath(v.get("path", "")) == vault for v in vaults.values()):
    for v in vaults.values():
        v["open"] = False
    vaults[secrets.token_hex(8)] = {"path": vault, "ts": int(time.time() * 1000), "open": True}
    json.dump(data, open(cfg_path, "w"), indent=2)
# Verify by reading the path back out of the file and checking it exists on disk.
check = json.load(open(cfg_path))
assert any(os.path.isdir(v["path"]) and os.path.realpath(v["path"]) == vault for v in check["vaults"].values()), "vault registration failed"
print("   registered in obsidian.json")
PY
fi

# ---------------------------------------------------------------- the voice
if [ "$WITH_VOICE" = 1 ]; then
  say_step "Voice (backtalk): uv, espeak-ng, ~1 GB of local speech models"
  (cd "$AGENT_HOME/backtalk" && ./install.sh)
fi

# ---------------------------------------------------------------- Desktop shortcuts
if [ "$IS_MAC" = 1 ]; then
  say_step "Desktop shortcuts"
  mk() {  # mk <name> <command...>
    f="$HOME/Desktop/$1.command"
    { echo '#!/bin/bash'
      echo 'export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"'
      echo "$2"; } > "$f"
    chmod +x "$f"; note "$1"
  }
  mk "Chat with Jarvis"  "cd \"$AGENT_HOME\" && claude"
  mk "Talk to Jarvis"    "cd \"$AGENT_HOME\" && ./fullstack-agent/start.sh voice"
  [ "$WITH_HANDS" = 1 ] && mk "Jarvis barehands" "cd \"$AGENT_HOME\" && ./fullstack-agent/start.sh hands"
  mk "Update Jarvis"     "cd \"$AGENT_HOME/fullstack-agent\" && ./update.sh"
fi

# ---------------------------------------------------------------- done
cat <<TXT

== Installed ==

Agent home : $AGENT_HOME
Vault      : $VAULT_PATH
Pieces     : $REPOS

Next, on the Mac:
  1. System Settings > Privacy & Security:
       Microphone      -> Terminal (asked on first recording)
       Input Monitoring -> Terminal (needed for the hold-to-talk key)
  2. cd $AGENT_HOME && claude
       Jarvis boots from CLAUDE.md, reads the vault, and greets you.
  3. Double-click "Talk to Jarvis" on the Desktop for the voice and the face.
       Hold HOME to talk. Say "goodbye Jarvis" to end.

Optional: ElevenLabs voice, or a full guided pass with Jared's wizard
(it adopts everything above and rebuilds nothing):
  cd $AGENT_HOME/fullstack-agent && claude "set me up"
TXT
