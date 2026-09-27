"""Microphone capture with simple energy-based voice activity detection.

Two modes:
- push_to_talk(): record until the user presses Enter.
- listen_for_phrase(): wait for speech, record until silence, return audio.
"""

from __future__ import annotations

import queue
import time

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000
BLOCK_MS = 30
BLOCK = SAMPLE_RATE * BLOCK_MS // 1000


def _rms(block: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(block)))) if block.size else 0.0


def calibrate(seconds: float = 1.0) -> float:
    """Measure ambient noise floor and return a speech threshold."""
    frames = sd.rec(int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="float32")
    sd.wait()
    floor = _rms(frames[:, 0])
    return max(floor * 3.5, 0.01)


def listen_for_phrase(
    threshold: float,
    max_seconds: float = 15.0,
    silence_after: float = 1.0,
    start_timeout: float | None = None,
) -> np.ndarray:
    """Block until speech starts, then return the utterance as float32 mono.

    Returns an empty array if `start_timeout` elapses with no speech.
    """
    q: queue.Queue[np.ndarray] = queue.Queue()

    def cb(indata, frames, time_info, status):  # noqa: ANN001
        q.put(indata[:, 0].copy())

    voiced: list[np.ndarray] = []
    pre_roll: list[np.ndarray] = []
    started = False
    last_voice = 0.0
    t0 = time.monotonic()

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32", blocksize=BLOCK, callback=cb):
        while True:
            try:
                block = q.get(timeout=1.0)
            except queue.Empty:
                block = np.zeros(BLOCK, dtype="float32")
            now = time.monotonic()
            loud = _rms(block) > threshold

            if not started:
                pre_roll.append(block)
                pre_roll = pre_roll[-10:]  # ~300 ms of context before speech
                if loud:
                    started = True
                    last_voice = now
                    voiced.extend(pre_roll)
                elif start_timeout is not None and now - t0 > start_timeout:
                    return np.zeros(0, dtype="float32")
                continue

            voiced.append(block)
            if loud:
                last_voice = now
            if now - last_voice > silence_after or now - t0 > max_seconds:
                break

    return np.concatenate(voiced) if voiced else np.zeros(0, dtype="float32")


def push_to_talk(prompt: str = "Recording. Press Enter to stop.") -> np.ndarray:
    q: queue.Queue[np.ndarray] = queue.Queue()

    def cb(indata, frames, time_info, status):  # noqa: ANN001
        q.put(indata[:, 0].copy())

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32", blocksize=BLOCK, callback=cb):
        input(prompt)
    chunks = []
    while not q.empty():
        chunks.append(q.get_nowait())
    return np.concatenate(chunks) if chunks else np.zeros(0, dtype="float32")
