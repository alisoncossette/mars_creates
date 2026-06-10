#!/usr/bin/env python3
"""publish_interview — Innate integration skill (posts a photo + text to gallery + X).

Matches the real on-robot convention (innate-os/skills/send_email.py, send_picture_via_email.py):
  from brain_client.skill_types import Skill, SkillResult
  __init__(self, logger) -> super().__init__(logger) | @property name | guidelines()
  execute(...) -> (message, SkillResult) | cancel()

Used by both the Phase-0 selfie agent (working_on + handle) and the Phase-1 interviewer (quote).
Grabs a frame if no image_path is given (falls back to the main camera via ~/mars_camera_feed.py).

DEPLOY:
  • drop in ~/skills/  (auto-discovered as local/publish_interview)
  • copy the mars/ lib to ~/mars_lib/  (this file adds it to sys.path)
  • keys via env / .env: MAGNIFIC_API_KEY, ANTHROPIC_API_KEY, X_*, AKAMAI_GALLERY_*
    (anything missing -> that step degrades to mock, skill still succeeds)
"""
from __future__ import annotations

import os
import subprocess
import sys

from brain_client.skill_types import Skill, SkillResult

# Make the mars lib importable (copy mars/ -> ~/mars_lib/ on the robot).
sys.path.insert(0, os.path.expanduser("~/mars_lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CAM_SCRIPT = os.path.expanduser("~/mars_camera_feed.py")
MAIN_CAM_TOPIC = "/mars/main_camera/left/image_raw/compressed"


class PublishInterview(Skill):
    """Turn a consented photo + what the guest said into a published, tagged post."""

    def __init__(self, logger):
        super().__init__(logger)

    @property
    def name(self):
        return "publish_interview"

    def guidelines(self):
        return (
            "Post to X (and the gallery if set up). Provide `working_on` (one line about what the "
            "guest is working on) and `handle` (their @, to tag them). It generates an image from "
            "`working_on` with Magnific, writes a caption, and posts + tags them. ONLY call this "
            "after the guest agreed out loud to be posted."
        )

    def execute(self, working_on: str = "", quote: str = "", handle: str = "",
                summary: str = "", image_path: str = None):
        try:
            from mars.config import EventContext, Settings
            from mars.content import compose_post
            from mars.interview import Transcript
            from mars.publish import build_publishers
        except Exception as e:
            self.logger.error(f"[publish_interview] mars lib not importable (copy mars/ -> ~/mars_lib): {e}")
            return f"publish lib not found: {e}", SkillResult.FAILURE

        said = working_on or quote or summary
        settings = Settings()
        frame = self._get_image(image_path, said, settings)
        post = compose_post(Transcript(turns=[("guest", said)]),
                            frame, EventContext(), settings, handle=handle)

        results = []
        for pub in build_publishers(Settings()):
            try:
                results.append(f"{pub.name}:{pub.publish(post)}")
            except Exception as e:  # a posting failure must not crash the skill
                self.logger.warning(f"[publish_interview] {pub.name} failed: {e}")

        if not results:
            return "No publish targets succeeded.", SkillResult.FAILURE
        msg = "Posted -> " + ", ".join(results)
        self.logger.info(f"\033[92m[publish_interview] {msg}\033[0m")
        return msg, SkillResult.SUCCESS

    def _get_image(self, image_path: str | None, said: str, settings) -> bytes:
        # Passed photo wins; else generate one from what Mars reports (Magnific); else text-only.
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as f:
                return f.read()
        if settings.magnific_api_key and said:
            from mars.content import generate_image
            prompt = (f"A bold, vibrant, social-media-ready illustration of: {said}. "
                      "Clean, modern, eye-catching, no text or words in the image.")
            return generate_image(prompt, settings)
        return b""

    def cancel(self):
        return "publish_interview cannot be canceled once posting has started"
