#!/usr/bin/env python3
"""publish_interview — Innate integration skill.

Matches the real on-robot convention from ~/skills/send_picture_via_email.py:
  from brain_client.skills.types import Skill, SkillResult
  __init__(self, logger) | @property name | guidelines() | execute(...) -> (msg, SkillResult) | cancel()

The brain calls this AFTER a consented interview, passing the guest's best `quote`. It grabs a
camera frame (via your ~/mars_camera_feed.py --once, so no in-process rclpy conflicts), enhances
it with Magnific, writes a caption, and posts to the gallery + X.

DEPLOY (on the robot):
  • drop this file in ~/skills/  (auto-discovered as local/publish_interview)
  • copy the mars/ lib to ~/mars_lib/   (this file adds it to sys.path)
  • keys via env / .env: MAGNIFIC_API_KEY, ANTHROPIC_API_KEY, X_*, AKAMAI_GALLERY_*
    (anything missing -> that step degrades to mock, skill still succeeds)
"""
from __future__ import annotations

import os
import subprocess
import sys

from brain_client.skills.types import Skill, SkillResult

# Make the mars lib importable (copy mars/ -> ~/mars_lib/ on the robot).
sys.path.insert(0, os.path.expanduser("~/mars_lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CAM_SCRIPT = os.path.expanduser("~/mars_camera_feed.py")  # your working camera grabber


class PublishInterview(Skill):
    """Turn a just-finished, consented interview into a published social post."""

    def __init__(self, logger):
        self.logger = logger

    @property
    def name(self):
        return "publish_interview"

    def guidelines(self):
        return (
            "Create and post a social card from the interview you just finished. Provide "
            "`quote` (the single most postable thing the guest said) and a short `summary`. "
            "Optionally pass `image_path` to a photo already captured; otherwise a camera frame "
            "is grabbed automatically. ONLY call this after the guest agreed out loud to be "
            "posted. It enhances the photo with Magnific, writes a caption, and posts to the "
            "gallery and X."
        )

    def execute(self, quote: str = "", summary: str = "", image_path: str = None):
        try:
            from mars.config import EventContext, Settings
            from mars.content import compose_post
            from mars.interview import Transcript
            from mars.publish import build_publishers
        except Exception as e:
            self.logger.error(f"[publish_interview] mars lib not importable (copy mars/ -> ~/mars_lib): {e}")
            return f"publish lib not found: {e}", SkillResult.FAILURE

        frame = self._load_or_capture(image_path)
        settings = Settings()
        event = EventContext()
        post = compose_post(Transcript(turns=[("guest", quote or summary)]), frame, event, settings)

        results = []
        for pub in build_publishers(settings):
            try:
                results.append(f"{pub.name}:{pub.publish(post)}")
            except Exception as e:  # a posting failure must not crash the skill
                self.logger.warning(f"[publish_interview] {pub.name} failed: {e}")

        if not results:
            return "No publish targets succeeded.", SkillResult.FAILURE
        msg = "Posted -> " + ", ".join(results)
        self.logger.info(f"\033[92m[publish_interview] {msg}\033[0m")
        return msg, SkillResult.SUCCESS

    def _load_or_capture(self, image_path: str | None) -> bytes:
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as f:
                return f.read()
        return self._capture_frame()

    def _capture_frame(self) -> bytes:
        """Grab one JPEG by running your ~/mars_camera_feed.py --once in a subprocess.
        Isolated process => no clash with the brain's running rclpy executor."""
        out = "/tmp/mars_interview.jpg"
        try:
            subprocess.run(["python3", CAM_SCRIPT, "--once", "--out", out], timeout=15, check=False)
            if os.path.exists(out):
                with open(out, "rb") as f:
                    return f.read()
        except Exception as e:
            self.logger.warning(f"[publish_interview] camera capture failed: {e}")
        self.logger.warning("[publish_interview] no frame; posting without photo")
        return b""

    def cancel(self):
        return "publish_interview cannot be canceled once posting has started"
