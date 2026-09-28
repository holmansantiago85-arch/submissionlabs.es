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

- `home/CLAUDE.md`: Jarvis boot config. Jared's engine rules verbatim. Character: a sharp-witted British butler with a fire-crew past, dry and sardonic, calls you sir or boss, profanity on (one line turns it off). His own voice and the copy he drafts for you are kept separate: drafts follow your Writing Style Guide. Welcome line "Hello James, what are we working on today?". Your writing rules, Spain time, DD/MM/YYYY, bilingual output, the Trident Maritime Academy accreditation rule, co-parenting scheduling rule. Barehands board block and the "you are the mechanic" block.
- `home/backtalk.json`: push to talk on HOME, ask-before-acting permissions, built-in British voice `bm_lewis`, vault in `extra_dirs`, barehands ring wired.
- `home/ai-visualizer.json`: default face is The Bridge (below), name JARVIS, bus pointed at backtalk.
- `faces/bridge/`: a custom face for Jared's visualizer. One thin ring and a horizon line on near-black, Spain clock and DD/MM/YYYY date, the academy motto. Breathes at idle, amber when listening, segmented spin when thinking, pulses with the voice when speaking. Installed into `ai-visualizer/faces/` so it sits in the gallery beside Jared's four. Switch faces by changing `face` in the config: `bridge`, `board`, `radial`, `rain`, `neural`.
- `home/barehands.json`: the vault as the Notes orb.
- `vault/`: seeded Obsidian vault. VAULT-INDEX with your profile, key people (Madi, Archie, Lucy), three business folders (Submission Labs, Trident Seas, Trident Maritime Academy), Personal, Archive, Resources, Active Priorities, daily note template, folder indexes, and five starter Jobs: WhatsApp Front Desk, Social Content, Course Pack Review, Bilingual Draft, plus a Writing Style Guide.
- `vault/07 - Resources/Marketing/` and `Integrations Plan.md`: Jared's marketing playbook wired in as AI Priming (the agent reads the principles before any marketing work), and a phased plan for connecting Calendar, Gmail, WhatsApp, Metricool and the website the way Jared connects his services: read-only first, ask-first permissions, one policy note per service.
- `install_mac.sh`: clones the six repos into `~/my-agent`, drops the files above in with real paths, creates the vault at `~/HQ`, installs Obsidian and registers the vault, runs backtalk's installer, writes Desktop shortcuts. Idempotent. Never overwrites anything that already exists.

## Install on the Mac mini

Requires macOS 13 or later and Homebrew (https://brew.sh). Claude Code is installed by the script if missing. A Claude subscription is required (Pro is enough).

```bash
git clone https://github.com/holmansantiago85-arch/submissionlabs.es.git
cd submissionlabs.es
git checkout claude/youtube-video-link-56e55w
cd jarvis
./install_mac.sh
```

Flags: `--no-voice` skips the 1 GB speech-model download (run backtalk's `install.sh` later). `--no-hands` skips barehands. `--pin` checks out the exact upstream commits this bundle was validated against instead of latest main (then `Update Jarvis` will not fast-forward until you `git checkout main` in each repo). Override locations with `AGENT_HOME=... VAULT_PATH=... ./install_mac.sh`.

Roughly 10 minutes, most of it the model download.

## Updating an existing install

After a `git pull` of this repo on the Mac:

```bash
cd ~/submissionlabs.es/jarvis && git pull && ./apply_updates.sh
```

Replaces CLAUDE.md (backup kept), installs any new faces, merges config keys while keeping settings the voice console saved (permission mode, mic mode, voice, ElevenLabs). Never touches the vault. Restart "Talk to Jarvis" afterwards.

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

## Version check and research (27/09/2026)

YouTube and Jared's site and Substack are blocked from the build environment, so this was done from his GitHub account (seven public repos, full commit history), web search results, and third-party write-ups. Findings:

**The correct version is upstream `main` as of 30/08/2026.** The tour video (FiOTrxq9ckM) was added to the fullstack-agent README on 20/08/2026. Every repo received fixes after that, through 30/08/2026, and nothing has changed since. The installer pulls `main`, so you get all of them. Validated commits: fullstack-agent `5bb159f`, ai-memory-vault `659bba9`, backtalk `84b3a6c`, ai-visualizer `6921e1d`, barehands `eb23bed`, ai-marketing-skills `47b68a5`.

**What changed after the video, and is in this bundle:**

- backtalk: speech recognition on the Apple Silicon GPU via mlx-whisper (0.88 s to 0.12 s per transcript on Jared's M4). Relevant to the Mac mini.
- backtalk: never reads file paths aloud; recovers the mic when a headset connects or disconnects; `mic_device` pins the microphone by name; `show_usage` can draw plan usage on the face; `visible_skills` hides skill descriptions on a shared screen; `BACKTALK_CONFIG` runs a second agent from the same install; `discipline_append` adds your own spoken-delivery rules.
- ai-visualizer: plan usage rows on every face; board F key fullscreen; Space key cinematic flythrough.
- barehands: `present` verb (show-me lands centre stage), positioned cards, Props folder anywhere.
- ai-memory-vault: fresh vault goes in the home folder (not Documents or iCloud, which macOS sandboxes for background work); the Obsidian registration step was hardened after it corrupted a user's config; the Claude Code memory redirect now names the right project folder.
- fullstack-agent: Update shortcut, incoming changelog on update, Obsidian never optional, interview covers mic mode, permission mode and voice engine.

**Retired:** the `prompts` repo (voice-line, visualizer, cinematic camera prompts) is marked retired by Jared. Do not use it; the repos replaced it.

**Upgrades applied here beyond the stock install:**

- `ai-marketing-skills` installed both ways Jared recommends: as vault files under `07 - Resources/Marketing` with the index note, and as a Claude Code skill at `~/.claude/skills/jaredrhod-marketing`. His wizard offers this at the end of every install.
- `discipline_append` in backtalk carries your spoken rules (no filler, Spain time, English then Spanish, no Trident Maritime Academy accreditations).
- ElevenLabs block pre-written and disabled, with the voice name from the videos (Tarquin) noted so nobody hunts for it.
- Integrations Plan note modelled on how Jared runs his: a dedicated Mac on 24/7, its own email and phone number, four inboxes each with a written policy, membership platform monitoring, newsletter auto-unsubscribe, a phone line answered in a British butler voice (Substack, "Six Weeks With Jarvis", 07/2026). Your equivalents are listed in priority order.

**Available, not switched on (your call, one line each to Jarvis):**

- ElevenLabs voice. Free tier auditions it; daily use is the paid starter plan. Needs `ffmpeg`.
- Hands-free microphone (`mic_mode: open`). Room audio and speakers can trigger it; headphones recommended.
- Auto-approve permissions (`bypassPermissions`). Faster, no checkpoint on a mistake. Jared's default is ask.
- `resume_last_session: true` so the morning voice session remembers last night.
- `show_usage: true` to draw your plan usage on the circuit board.
- Deep model for the voice line. Jared pins the fast tier on purpose; use "switch to the deep model" per session instead.

**Sources:** github.com/jaredrhod (all repos and commit logs), https://jaredrhod.substack.com/p/six-weeks-with-jarvis , https://jaredrhod.substack.com/p/how-to-make-a-jarvis , https://www.youtube.com/watch?v=6Tb41ORADgs (visualizer demo), https://youtu.be/cV02finVi4o (barehands demo), playlists How To Build A Jarvis https://youtube.com/playlist?list=PLPv0hMv8Uwt4 and The AI Marketing Machine https://youtube.com/playlist?list=PLdNHCeiXnovo , memory vault walkthrough https://www.youtube.com/playlist?list=PLN7lTYpeRLOc . Jared's own tip: give Claude Code any of his video links and it can read the transcript.

## Notes

- Vault name `HQ` and home `my-agent` follow Jared's conventions (home folder, not Documents or iCloud, so background processes are not sandboxed by macOS).
- The vault is local only. Time Machine covers it; a private GitHub repo is the free off-machine option.
- Project folders are seeded thin on purpose. Fill them in conversation; Jarvis files everything itself.
