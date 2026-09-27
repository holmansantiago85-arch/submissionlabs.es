"""Text-to-speech using the built-in macOS `say` command. Zero dependencies."""

from __future__ import annotations

import platform
import subprocess
import threading

from jarvis.config import config

_lock = threading.Lock()
_current: subprocess.Popen | None = None


def speak(text: str, block: bool = True) -> None:
    global _current
    text = text.strip()
    if not text:
        return
    if platform.system() != "Darwin":
        print(f"[tts] {text}")
        return
    stop()
    with _lock:
        _current = subprocess.Popen(
            ["say", "-v", config.tts_voice, "-r", str(config.tts_rate), text],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    if block:
        _current.wait()


def stop() -> None:
    global _current
    with _lock:
        if _current and _current.poll() is None:
            _current.terminate()
        _current = None


def is_speaking() -> bool:
    return _current is not None and _current.poll() is None
