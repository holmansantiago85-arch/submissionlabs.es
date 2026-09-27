# Jarvis

Local voice and text assistant for macOS, powered by Claude (Opus 5 by default). Runs on a Mac mini, listens for a wake word, speaks replies through the built-in `say` voice, and acts on the machine through Calendar, Reminders, Messages, the shell and web search.

## What it does

- **Voice**: offline speech-to-text (faster-whisper), wake word "Jarvis", macOS text-to-speech.
- **Text**: REPL or one-shot `jarvis ask "..."`.
- **Tools**: date/time, Calendar (list and create), Reminders, iMessage, open apps and URLs, notifications, volume, allow-listed shell, file reads, web search.
- **Memory**: conversation history in SQLite, long-term facts in `data/memory.md` that Jarvis reads every turn and updates when told something durable.
- **Behaviour**: brief spoken replies, DD/MM/YYYY dates, Spain time, English then formal Spanish when Spanish is requested.

## Install on the Mac mini

Requires macOS 13 or later and Homebrew.

```bash
git clone https://github.com/holmansantiago85-arch/submissionlabs.es.git
cd submissionlabs.es/jarvis
./setup_mac.sh
```

Then put your key in `.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Run

```bash
source .venv/bin/activate
jarvis                 # text REPL
jarvis ask "what is on my calendar tomorrow"
jarvis ptt             # push-to-talk: Enter to start, Enter to stop
jarvis voice           # always-on, say "Jarvis, ..." 
```

First run downloads the whisper model (about 500 MB for `small`) and macOS prompts for Microphone, Calendar, Reminders and Automation access. Grant them in System Settings, Privacy & Security.

## Run at login

```bash
sed "s#__JARVIS_DIR__#$PWD#g" launchd/com.jarvis.assistant.plist > ~/Library/LaunchAgents/com.jarvis.assistant.plist
launchctl load ~/Library/LaunchAgents/com.jarvis.assistant.plist
```

Logs go to `logs/`. Unload with `launchctl unload` on the same path.

## Configuration

All settings live in `.env` (see `.env.example`).

| Variable | Default | Purpose |
|---|---|---|
| `JARVIS_MODEL` | `claude-opus-5` | Claude model |
| `JARVIS_EFFORT` | `medium` | `low` to `max`. Raise for harder tasks, lower for speed |
| `JARVIS_FALLBACKS` | `1` | Server-side refusal fallback to another Claude model |
| `JARVIS_WAKE_WORD` | `jarvis` | Wake word, matched in the transcript |
| `JARVIS_TTS_VOICE` | `Daniel` | Any voice from `say -v '?'` |
| `JARVIS_STT_MODEL` | `small` | `tiny`, `base`, `small`, `medium`, `large-v3` |
| `JARVIS_SHELL_ALLOWLIST` | read-only commands | Command prefixes `run_shell` may execute |
| `JARVIS_SHELL_UNRESTRICTED` | `0` | Set `1` to allow any command. Not recommended |

## Layout

```
jarvis/
  brain.py        Claude loop: system prompt, tools, refusal handling, history
  memory.py       SQLite history + memory.md notes
  cli.py          text / ask / ptt / voice modes
  tools/          registry + system, macOS (AppleScript), notes tools
  voice/          listener (mic + VAD), stt (faster-whisper), tts (say)
launchd/          login agent
setup_mac.sh      Homebrew + venv + deps
tests/            offline unit tests (pytest)
```

## Adding a tool

Register a function in any module under `jarvis/tools/` and import it in `jarvis/tools/__init__.py`:

```python
@registry.register(
    name="my_tool",
    description="What it does and when to use it.",
    properties={"arg": {"type": "string"}},
    required=["arg"],
)
def my_tool(arg: str) -> str:
    return "result text"
```

Return a string starting with `Error:` to flag a failure to the model.

## Tests

```bash
pytest
```

## Roadmap

- Wake-word engine (openWakeWord) instead of transcript matching, for lower latency.
- Streaming TTS so long replies start speaking before generation ends.
- Gmail, Google Calendar and WhatsApp connectors.
- Menu-bar app wrapper.
