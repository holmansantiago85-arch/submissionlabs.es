"""Find out why push-to-talk misbehaves. Run with backtalk's Python:
   ~/my-agent/backtalk/.venv/bin/python tools/diagnose_talk.py
Watches the keyboard for 20 seconds, prints every key backtalk could bind, and
says what it means. No audio, nothing stored."""
import json, os, sys, time
from pathlib import Path

AGENT_HOME = Path(os.environ.get("AGENT_HOME", Path.home() / "my-agent"))
CFG = AGENT_HOME / "backtalk" / "backtalk.json"
try:
    from pynput import keyboard
except Exception as e:                                     # noqa: BLE001
    sys.exit(f"pynput not importable ({e}). Run this with backtalk's venv python.")

try:
    want = json.loads(CFG.read_text()).get("ptt_key", "home")
except Exception:                                          # noqa: BLE001
    want = "home"

def label(k):
    return f"Key.{k.name}" if hasattr(k, "name") else repr(k)

events = []
t0 = time.monotonic()
def on_press(k):   events.append((time.monotonic() - t0, "down", label(k)))
def on_release(k): events.append((time.monotonic() - t0, "up", label(k)))

print(f"Configured talk key: {want!r}")
print("For the next 20 seconds: press and HOLD your talk key for about 2 seconds, release, "
      "then try Right Option, Right Command and any other key you might use.\n")
with keyboard.Listener(on_press=on_press, on_release=on_release):
    time.sleep(20)

if not events:
    print("RESULT: no keyboard events reached this program at all.")
    print("Fix: System Settings > Privacy & Security > Input Monitoring > add the app you ran this from "
          "(Terminal, iTerm). Then QUIT that app completely and reopen it. This is the most common cause.")
    sys.exit(1)

names = sorted({n for _, _, n in events})
print("Keys seen:", ", ".join(names))

sys.path.insert(0, str(AGENT_HOME / "backtalk"))
try:
    from backtalk.ptt import resolve_key
    target = label(resolve_key(want))
except Exception:                                          # noqa: BLE001
    target = f"Key.{want}"
print(f"Your configured key resolves to: {target}")

mine = [(t, d) for t, d, n in events if n == target]
downs = [t for t, d in mine if d == "down"]
ups = [t for t, d in mine if d == "up"]
if not mine:
    print(f"\nRESULT: {target} never registered. That key is not reaching the listener.")
    print("Most likely it does not exist on your keyboard (Apple keyboards have no Home key; fn+arrow does not count).")
    others = [n for n in names if n in ("Key.alt_r", "Key.cmd_r", "Key.alt_l", "Key.cmd_l", "Key.ctrl_r", "Key.ctrl_l", "Key.shift_r")]
    print("Keys that DID register and are safe to use:", ", ".join(others) or "none of the usual modifiers; press them and re-run")
    print("Set one with:  ./talk_config.sh key right_alt")
elif len(downs) > 1 or len(ups) > 1:
    print(f"\nRESULT: {len(downs)} presses and {len(ups)} releases for what should be one hold.")
    print("Your keyboard sends auto-repeat as separate press/release pairs. backtalk filters this (0.12 s grace), "
          "but if the voice still cuts you off, use a modifier key: ./talk_config.sh key right_alt")
else:
    hold = (ups[0] - downs[0]) if ups and downs else 0
    print(f"\nRESULT: {target} works. One press, one release, held {hold:.1f}s.")
    print("If talking still feels bad the cause is elsewhere: run `tail -40 ~/my-agent/backtalk/logs/backtalk.log` "
          "and look at the lines around '[ptt] recording' and 'heard:'.")
