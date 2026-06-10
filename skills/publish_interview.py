"""publish_interview — an Innate integration skill (same category as innate-os/send_email).

Deploy: drop in the robot's ~/skills/ (auto-discovered as `local/publish_interview`).
The brain calls this after a consented interview, passing the guest's best `quote`.

NOTE: confirm the exact `Skill` base + metadata against an existing innate-os integration
skill (send_email is the closest analog). The execute() body is the real, tested work —
it reuses mars/ which run_mars.py exercises end-to-end off-robot.
"""
from __future__ import annotations

import logging

from brain_client.skill_types import Skill  # robot-only import (not needed for local run_mars.py)

from mars.config import EventContext, Settings
from mars.content import compose_post
from mars.interview import Transcript
from mars.publish import build_publishers

log = logging.getLogger("skill.publish_interview")


class PublishInterview(Skill):
    name = "publish_interview"
    description = (
        "Create and post a social card from the just-finished interview. "
        "Args: quote (the single most postable thing the guest said), summary (short recap). "
        "Captures a photo, enhances it with Magnific, writes a caption, posts to gallery + X."
    )

    def execute(self, quote: str = "", summary: str = "", **kwargs) -> str:
        settings = Settings()
        event = EventContext()

        frame = self._capture_frame()
        transcript = Transcript(turns=[("guest", quote or summary)])
        post = compose_post(transcript, frame, event, settings)

        results = []
        for pub in build_publishers(settings):
            try:
                results.append(f"{pub.name}:{pub.publish(post)}")
            except Exception as e:  # never let a posting failure crash the skill
                log.warning("[publish_interview] %s failed: %s", pub.name, e)
        return "Posted -> " + (", ".join(results) if results else "nowhere (no targets configured)")

    def _capture_frame(self) -> bytes:
        # TODO(innate): grab the current JPEG from maurice_cam (subscribe to the camera image
        # topic, or reuse whatever local/capture_image uses). b"" -> Magnific passthrough (mock).
        return b""
