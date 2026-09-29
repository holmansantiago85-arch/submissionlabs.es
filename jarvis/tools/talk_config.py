"""Change how you talk to Jarvis without editing JSON by hand.
   ./talk_config.sh show
   ./talk_config.sh key right_alt        (right_alt | right_cmd | left_alt | f13..f19 | any single character)
   ./talk_config.sh mode open            (open = hands-free, ptt = hold to talk)
Takes effect the next time the voice line starts."""
import json, os, sys
from pathlib import Path

AGENT_HOME = Path(os.environ.get("AGENT_HOME", Path.home() / "my-agent"))
CFG = AGENT_HOME / "backtalk" / "backtalk.json"
KEYS_OK = {"right_alt", "left_alt", "right_option", "left_option", "right_cmd", "left_cmd",
           "right_ctrl", "left_ctrl", "right_shift", "left_shift", "home", "end", "insert",
           "page_up", "page_down", "caps_lock", "tab", "space", "pause", "scroll_lock", "menu"} \
          | {f"f{i}" for i in range(1, 21)}

def load():
    return json.loads(CFG.read_text())

def save(d):
    CFG.write_text(json.dumps(d, indent=2) + "\n")

def main(a):
    if not CFG.exists():
        sys.exit(f"No config at {CFG}. Run install_mac.sh first.")
    d = load()
    if not a or a[0] == "show":
        print(f"ptt_key  = {d.get('ptt_key')}\nmic_mode = {d.get('mic_mode')}  (ptt = hold to talk, open = hands-free)")
        return
    if a[0] == "key" and len(a) == 2:
        k = a[1].lower()
        if len(k) != 1 and k not in KEYS_OK:
            sys.exit(f"Unknown key {k!r}. Try: right_alt, right_cmd, f13..f19, or a single character.")
        if k in ("home", "end", "page_up", "page_down", "insert"):
            print("Warning: Apple keyboards do not have this key. If nothing happens, choose right_alt.")
        d["ptt_key"] = k; save(d); print(f"ptt_key -> {k}")
    elif a[0] == "mode" and len(a) == 2 and a[1] in ("ptt", "open"):
        d["mic_mode"] = a[1]; save(d)
        print(f"mic_mode -> {a[1]}" + ("  (hands-free: room audio can trigger it; headphones recommended)" if a[1] == "open" else ""))
    else:
        sys.exit(__doc__)
    print("Restart 'Talk to Jarvis' for it to apply.")

main(sys.argv[1:])
