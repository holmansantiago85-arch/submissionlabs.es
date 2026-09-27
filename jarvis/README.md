# Jarvis

James Holman's Jarvis: the four-part AI agent from Jared Rhodenizer's tour video (https://www.youtube.com/watch?v=FiOTrxq9ckM), pre-configured for James and ready to install on the Mac mini.

Upstream, all free and open (AGPL-3.0-or-later, copyright Jared Rhodenizer):

| Piece | Repo | What it is |
|---|---|---|
| Installer / launcher | https://github.com/jaredrhod/fullstack-agent | Assembles the four pieces, `start.sh`, `update.sh` |
| Memory | https://github.com/jaredrhod/ai-memory-vault | Obsidian vault of plain text files the agent reads and writes every session |
| Voice | https://github.com/jaredrhod/backtalk | Hold a key, talk, it answers through the speakers. Claude Agent SDK |
| Face | https://github.com/jaredrhod/ai-visualizer | Full-screen visualizer (circuit board default) that idles, listens, thinks, speaks |
| Hands (optional) | https://github.com/jaredrhod/barehands | Webcam hand tracking to move notes and images on screen |

Site and start page: https://jaredrhod.com . Discord: https://discord.gg/YSdsqMv3V8 . Videos: https://youtube.com/@jaredrhod

## What this folder adds

Jared's wizard normally interviews you for 10 to 15 minutes. This folder holds the answers already written, so the Mac install is one script.

- `home/CLAUDE.md`: Jarvis boot config. Jared's engine rules verbatim, identity door C: authoritative, direct, zero filler, addresses you as James or sir. Welcome line "Hello James, what are we working on today?". Your writing rules, Spain time, DD/MM/YYYY, bilingual output, the Trident Maritime Academy accreditation rule, co-parenting scheduling rule. Barehands board block and the "you are the mechanic" block.
- `home/backtalk.json`: push to talk on HOME, ask-before-acting permissions, built-in British voice `bm_lewis`, vault in `extra_dirs`, barehands ring wired.
- `home/ai-visualizer.json`: circuit board face, name JARVIS, bus pointed at backtalk.
- `home/barehands.json`: the vault as the Notes orb.
- `vault/`: seeded Obsidian vault. VAULT-INDEX with your profile, key people (Madi, Archie, Lucy), three business folders (Submission Labs, Trident Seas, Trident Maritime Academy), Personal, Archive, Resources, Active Priorities, daily note template, folder indexes, and five starter Jobs: WhatsApp Front Desk, Social Content, Course Pack Review, Bilingual Draft, plus a Writing Style Guide.
- `install_mac.sh`: clones the five repos into `~/my-agent`, drops the files above in with real paths, creates the vault at `~/HQ`, installs Obsidian and registers the vault, runs backtalk's installer, writes Desktop shortcuts. Idempotent. Never overwrites anything that already exists.

## Install on the Mac mini

Requires macOS 13 or later and Homebrew (https://brew.sh). Claude Code is installed by the script if missing. A Claude subscription is required (Pro is enough).

```bash
git clone https://github.com/holmansantiago85-arch/submissionlabs.es.git
cd submissionlabs.es
git checkout claude/youtube-video-link-56e55w
cd jarvis
./install_mac.sh
```

Flags: `--no-voice` skips the 1 GB speech-model download (run backtalk's `install.sh` later). `--no-hands` skips barehands. Override locations with `AGENT_HOME=... VAULT_PATH=... ./install_mac.sh`.

Roughly 10 minutes, most of it the model download.

## First run

1. System Settings, Privacy & Security: grant Terminal **Microphone** (prompted on first recording) and **Input Monitoring** (needed for the hold-to-talk key). Restart Terminal after adding Input Monitoring.
2. `cd ~/my-agent && claude`. Jarvis boots from CLAUDE.md, reads the vault, greets you.
3. Double-click **Talk to Jarvis** on the Desktop. The circuit board opens in the browser, Jarvis speaks the greeting. Hold HOME, talk, release. "Goodbye Jarvis" ends the session.

Desktop shortcuts written: Chat with Jarvis, Talk to Jarvis, Jarvis barehands, Update Jarvis. First double-click may ask permission; click Open.

## Voice console (spoken, exact phrases)

"go hands free" / "push to talk mode", "stop asking for permission" then "confirm" / "start asking again", "switch to the deep model" / "back to the fast model", "set effort to low|medium|high|max", "clear the session", "usage report".

## Optional after install

- **ElevenLabs voice** (the natural one from the videos, voice "Tarquin"): `cd ~/my-agent/backtalk && claude "read backtalk.md and set up ElevenLabs"`. The key goes in the macOS Keychain, never a file.
- **Jared's full wizard**: `cd ~/my-agent/fullstack-agent && claude "set me up"`. It finds the CLAUDE.md and vault, adopts them, and rebuilds nothing.
- **Updates**: double-click Update Jarvis, or `~/my-agent/fullstack-agent/update.sh`. Your CLAUDE.md, configs and vault are never touched.
- **Anything broken**: open Chat with Jarvis and describe it. Every repo ships a TROUBLESHOOTING.md written for the agent to read and act on.

## Layout of the agent home after install

```
~/my-agent/
  CLAUDE.md            Jarvis boot config (from home/)
  fullstack-agent/     start.sh, update.sh
  ai-memory-vault/     wizard + templates (reference only once the vault exists)
  backtalk/            voice; backtalk.json (from home/)
  ai-visualizer/       face; ai-visualizer.json (from home/)
  barehands/           hands; barehands.json (from home/)
~/HQ/                  the vault (from vault/)
```

## Notes

- Vault name `HQ` and home `my-agent` follow Jared's conventions (home folder, not Documents or iCloud, so background processes are not sandboxed by macOS).
- The vault is local only. Time Machine covers it; a private GitHub repo is the free off-machine option.
- Project folders are seeded thin on purpose. Fill them in conversation; Jarvis files everything itself.
