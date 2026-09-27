"""Entry point: `jarvis` (text REPL), `jarvis voice` (wake-word loop), `jarvis ptt` (push-to-talk)."""

from __future__ import annotations

import argparse
import logging
import sys

from jarvis.brain import Brain
from jarvis.config import config

log = logging.getLogger("jarvis")

EXIT_WORDS = {"exit", "quit", "goodbye", "stop listening", "shut down"}


def _brain() -> Brain:
    return Brain(
        on_tool=lambda name, args: print(f"  [tool] {name} {args}", file=sys.stderr),
    )


def run_text(brain: Brain, one_shot: str | None = None) -> None:
    if one_shot:
        print(brain.ask(one_shot))
        return
    print(f"{config.name} ready. Type 'exit' to quit, '/reset' to clear history.")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line.lower() in EXIT_WORDS:
            break
        if line == "/reset":
            brain.reset()
            print("History cleared.")
            continue
        try:
            print(brain.ask(line))
        except RuntimeError as exc:
            print(f"[error] {exc}")


def run_voice(brain: Brain, push_to_talk: bool) -> None:
    from jarvis.voice import listener, stt, tts

    tts.speak(f"{config.name} online.", block=False)
    threshold = None
    if not push_to_talk:
        print("Calibrating microphone...")
        threshold = listener.calibrate()
        print(f"Say '{config.wake_word}' followed by your request. Ctrl-C to quit.")
    else:
        print("Push-to-talk mode. Press Enter to start and stop recording. Ctrl-C to quit.")

    while True:
        try:
            if push_to_talk:
                input("Press Enter to talk...")
                audio = listener.push_to_talk()
            else:
                audio = listener.listen_for_phrase(threshold)
        except KeyboardInterrupt:
            print()
            break

        text = stt.transcribe(audio)
        if not text:
            continue
        lowered = text.lower()

        if not push_to_talk:
            idx = lowered.find(config.wake_word)
            if idx < 0:
                continue  # not addressed to us
            text = text[idx + len(config.wake_word):].strip(" ,.!?")
            if not text:
                tts.speak("Yes?")
                audio = listener.listen_for_phrase(threshold, start_timeout=6.0)
                text = stt.transcribe(audio)
                if not text:
                    continue
                lowered = text.lower()

        print(f"You: {text}")
        if lowered.strip(" .!") in EXIT_WORDS:
            tts.speak("Shutting down.")
            break

        try:
            reply = brain.ask(text)
        except RuntimeError as exc:
            reply = str(exc)
        print(f"{config.name}: {reply}")
        tts.speak(reply)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="jarvis", description="Local Claude-powered assistant.")
    sub = parser.add_subparsers(dest="mode")
    sub.add_parser("text", help="Text REPL (default)")
    sub.add_parser("voice", help="Always-on wake-word voice loop")
    sub.add_parser("ptt", help="Push-to-talk voice mode")
    ask = sub.add_parser("ask", help="One question, print the answer, exit")
    ask.add_argument("question", nargs="+")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    brain = _brain()
    mode = args.mode or "text"
    if mode == "text":
        run_text(brain)
    elif mode == "ask":
        run_text(brain, one_shot=" ".join(args.question))
    elif mode == "voice":
        run_voice(brain, push_to_talk=False)
    elif mode == "ptt":
        run_voice(brain, push_to_talk=True)


if __name__ == "__main__":
    main()
