"""Speech-to-text with faster-whisper, running fully offline on the Mac."""

from __future__ import annotations

import numpy as np

from jarvis.config import config

_model = None


def _load():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel

        # int8 on CPU is fast enough for short commands on an Apple Silicon Mac mini.
        _model = WhisperModel(config.stt_model, device="cpu", compute_type="int8")
    return _model


def transcribe(audio: np.ndarray, sample_rate: int = 16000) -> str:
    """audio: float32 mono in [-1, 1] at 16 kHz."""
    if audio.size == 0:
        return ""
    if sample_rate != 16000:
        raise ValueError("faster-whisper expects 16 kHz audio")
    model = _load()
    segments, _info = model.transcribe(
        audio,
        language=config.stt_language or None,
        beam_size=1,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    return " ".join(seg.text.strip() for seg in segments).strip()
