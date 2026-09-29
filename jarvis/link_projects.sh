#!/bin/bash
# Give Jarvis access to project folders (text and voice sessions) and list them in the vault.
#   ./link_projects.sh ~/Projects/site ~/Developer/app
#   ./link_projects.sh --scan        show likely project folders on this Mac (adds nothing)
AGENT_HOME="${AGENT_HOME:-$HOME/my-agent}"
VAULT_PATH="${VAULT_PATH:-$HOME/HQ}"
HERE="$(cd "$(dirname "$0")" && pwd)"
if [ "${1:-}" = "--scan" ] || [ $# -eq 0 ]; then
  echo "Likely project folders (git repos, two levels deep):"
  for base in "$HOME/Projects" "$HOME/Developer" "$HOME/Code" "$HOME/dev" "$HOME/src" "$HOME/Documents/GitHub" "$HOME"; do
    [ -d "$base" ] || continue
    find "$base" -maxdepth 2 -name .git -type d 2>/dev/null | sed 's#/.git$##' | grep -v "$AGENT_HOME"
  done | sort -u
  echo; echo "Add with: ./link_projects.sh <folder> [<folder> ...]"; exit 0
fi
python3 - "$AGENT_HOME" "$VAULT_PATH" "$@" <<'PY'
import json, os, sys
from pathlib import Path
home, vault, dirs = Path(sys.argv[1]), Path(sys.argv[2]), [os.path.abspath(os.path.expanduser(d)) for d in sys.argv[3:]]
bad = [d for d in dirs if not os.path.isdir(d)]
if bad: sys.exit("Not a folder: " + ", ".join(bad))
cfgp = home / "backtalk" / "backtalk.json"
if cfgp.exists():
    c = json.loads(cfgp.read_text()); ed = c.setdefault("extra_dirs", [])
    for d in dirs:
        if d not in ed: ed.append(d)
    cfgp.write_text(json.dumps(c, indent=2) + "\n"); print("   voice access:", len(dirs), "folder(s)")
sp = home / ".claude" / "settings.json"; sp.parent.mkdir(parents=True, exist_ok=True)
s = json.loads(sp.read_text()) if sp.exists() else {}
ad = s.setdefault("permissions", {}).setdefault("additionalDirectories", [])
for d in dirs:
    if d not in ad: ad.append(d)
sp.write_text(json.dumps(s, indent=2) + "\n"); print("   text access: settings.json updated")
idx = vault / "07 - Resources" / "Projects Index.md"
if idx.exists():
    t = idx.read_text()
    for d in dirs:
        short = d.replace(str(Path.home()), "~")
        if f"`{short}`" not in t:
            t = t.replace("\n## Add a project", f"- `{short}` — (Jarvis: read it and replace this with one sentence on what it is)\n\n## Add a project", 1) if "\n## Add a project" in t else t + f"\n- `{short}`\n"
    idx.write_text(t); print("   listed in Projects Index")
PY
echo "Restart 'Talk to Jarvis' to apply."
