#!/usr/bin/env python3
"""Off-robot test harness — run the REAL publish pipeline on a local photo. No robot needed.

    python test_post.py selfie.jpg --handle alison --working-on "a knowledge graph"

With keys in .env it really: enhances (Magnific) -> captions (Claude) -> pushes to Akamai/Linode
-> posts to X. Without a given key, that step mocks gracefully so you can still see the flow.
This proves the entire publishing half before Mars's camera/arm are ever involved.
"""
from __future__ import annotations

import argparse
import sys

from mars.config import EventContext, Settings
from mars.content import compose_post
from mars.interview import Transcript
from mars.publish import build_publishers


def main() -> None:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="Test the Mars publish pipeline on a local photo.")
    ap.add_argument("image", help="path to a photo (jpg)")
    ap.add_argument("--handle", default="", help="guest @ to tag")
    ap.add_argument("--working-on", default="", help="what they're working on")
    ap.add_argument("--event", default="", help="event name (else from .env / MARS_EVENT_NAME)")
    args = ap.parse_args()

    with open(args.image, "rb") as f:
        frame = f.read()

    settings = Settings()
    event = EventContext()
    if args.event:
        event.name = args.event

    print(
        f"[test] magnific={'REAL' if settings.magnific_api_key else 'mock'}  "
        f"caption={'claude' if not settings.mock_llm else 'mock'}  "
        f"gallery={'AKAMAI' if settings.s3_configured else 'mock(./out)'}  "
        f"x={'REAL' if all(settings.x_keys.values()) else 'mock'}"
    )

    post = compose_post(
        Transcript(turns=[("guest", args.working_on)]), frame, event, settings, handle=args.handle
    )
    print("\n--- CAPTION ---\n" + post.caption + "\n--------------\n")

    for pub in build_publishers(settings):
        try:
            url = pub.publish(post)
            print(f"  -> {pub.name}: {url}")
        except Exception as e:
            print(f"  -> {pub.name} FAILED: {e}")


if __name__ == "__main__":
    main()
