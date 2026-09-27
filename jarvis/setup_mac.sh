#!/usr/bin/env bash
# One-shot setup for a Mac mini (Apple Silicon or Intel). Run from the jarvis/ directory.
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew not found. Install from https://brew.sh then re-run."; exit 1
fi

brew list python@3.12 >/dev/null 2>&1 || brew install python@3.12
brew list portaudio   >/dev/null 2>&1 || brew install portaudio   # needed by sounddevice

PY="$(brew --prefix python@3.12)/bin/python3.12"
[ -d .venv ] || "$PY" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -e ".[voice,dev]"

[ -f .env ] || { cp .env.example .env; echo "Created .env - add your ANTHROPIC_API_KEY."; }
mkdir -p data logs

echo
echo "Setup complete."
echo "  Text mode:   .venv/bin/jarvis"
echo "  Voice mode:  .venv/bin/jarvis voice"
echo "  Push-to-talk: .venv/bin/jarvis ptt"
echo
echo "macOS will ask for Microphone, Calendar, Reminders and Automation permissions on first use."
echo "Grant them in System Settings > Privacy & Security."
