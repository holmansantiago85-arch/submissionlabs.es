"""Configuration loaded from environment / .env."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _list(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass
class Config:
    model: str = os.getenv("JARVIS_MODEL", "claude-opus-5")
    effort: str = os.getenv("JARVIS_EFFORT", "medium")
    fallbacks: bool = _bool("JARVIS_FALLBACKS", True)
    max_tokens: int = int(os.getenv("JARVIS_MAX_TOKENS", "16000"))

    name: str = os.getenv("JARVIS_NAME", "Jarvis")
    user_name: str = os.getenv("JARVIS_USER_NAME", "James")
    timezone: str = os.getenv("JARVIS_TIMEZONE", "Europe/Madrid")

    wake_word: str = os.getenv("JARVIS_WAKE_WORD", "jarvis").lower()
    tts_voice: str = os.getenv("JARVIS_TTS_VOICE", "Daniel")
    tts_rate: int = int(os.getenv("JARVIS_TTS_RATE", "190"))
    stt_model: str = os.getenv("JARVIS_STT_MODEL", "small")
    stt_language: str = os.getenv("JARVIS_STT_LANGUAGE", "en")

    shell_allowlist: list[str] = field(
        default_factory=lambda: _list(
            "JARVIS_SHELL_ALLOWLIST",
            "ls,cat,head,tail,pwd,date,cal,df,du,uptime,whoami,open,say,osascript,ping,curl,brew list,git status,git log",
        )
    )
    shell_unrestricted: bool = _bool("JARVIS_SHELL_UNRESTRICTED", False)

    data_dir: Path = Path(os.getenv("JARVIS_DATA_DIR", "./data")).expanduser().resolve()

    # Server-side web search cap per turn
    web_search_max_uses: int = int(os.getenv("JARVIS_WEB_SEARCH_MAX_USES", "5"))

    def __post_init__(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

    @property
    def db_path(self) -> Path:
        return self.data_dir / "jarvis.db"

    @property
    def notes_path(self) -> Path:
        return self.data_dir / "memory.md"


config = Config()
