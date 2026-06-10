#!/usr/bin/env python3
"""Entry point. Runs the whole Mars roving-interviewer loop.

MOCK by default — no robot, no keys needed. `say` prints, answers are typed, every external
tool no-ops with a log. So you can play the entire flow right now:

    python run_mars.py --rounds 1

Then drop real keys into .env and wire the Innate SDK in mars/robot.py to go live.
"""
from __future__ import annotations

import argparse
import logging

from mars.agent import MarsAgent
from mars.config import EventContext, Settings
from mars.interview import InterviewBrain
from mars.media import LiveStream
from mars.publish import build_publishers
from mars.robot import MarsClient
from mars.voice import Voice


def main() -> None:
    import sys
    for stream in (sys.stdout, sys.stderr):  # Windows consoles default to cp1252; emoji/em-dash need utf-8
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ap = argparse.ArgumentParser(description="Mars — roving robot interviewer")
    ap.add_argument("--rounds", type=int, default=1, help="interviews to run (default 1; 0 = loop forever)")
    ap.add_argument("--real", action="store_true", help="use the real Innate Mars SDK instead of mock")
    args = ap.parse_args()

    settings = Settings()
    event = EventContext()
    robot = MarsClient(mock=not args.real)
    voice = Voice(robot, settings)
    brain = InterviewBrain(settings, event)
    publishers = build_publishers(settings)
    live = LiveStream(settings)

    print("=" * 60)
    print("  MARS — roving robot interviewer")
    print(f"  llm={'real' if not settings.mock_llm else 'MOCK'}  "
          f"voice={'real' if not (voice.mock_tts or voice.mock_stt) else 'MOCK'}  "
          f"live={'on' if settings.live else 'off'}  "
          f"targets={[p.name for p in publishers]}")
    print("=" * 60)

    agent = MarsAgent(settings, event, robot, voice, brain, publishers, live)
    agent.run(max_rounds=None if args.rounds == 0 else args.rounds)


if __name__ == "__main__":
    main()
