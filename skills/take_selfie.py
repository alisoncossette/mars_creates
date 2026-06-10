#!/usr/bin/env python3
"""take_selfie — capture a portrait of the guest from Mars's FRONT (main) camera.

Mars faces the person and snaps a portrait with the primary camera (no arm involved).
Uses the proper RobotState API (same mechanism record_position uses for its wrist image),
so no ROS-topic/QoS or serial access. Saves to /tmp/mars_selfie.jpg for publish_interview.

Deploy: ~/skills/take_selfie.py (auto-discovered as local/take_selfie).
"""
from __future__ import annotations

import base64

from brain_client.skill_types import RobotState, RobotStateType, Skill, SkillResult

PORTRAIT_OUT = "/tmp/mars_selfie.jpg"


class TakeSelfie(Skill):
    """Snap a portrait of the guest from the front (main) camera and save it for publishing."""

    image = RobotState(RobotStateType.LAST_MAIN_CAMERA_IMAGE_B64)

    def __init__(self, logger):
        super().__init__(logger)

    @property
    def name(self):
        return "take_selfie"

    def guidelines(self):
        return (
            "Take a portrait of the person using Mars's front (main) camera. Face them so they're "
            f"centered first. Saves the photo to {PORTRAIT_OUT} — call this right before "
            "publish_interview and pass that path as image_path. Use after the guest said yes."
        )

    def execute(self):
        if not self.image:
            return "No main camera image available yet.", SkillResult.FAILURE
        try:
            with open(PORTRAIT_OUT, "wb") as f:
                f.write(base64.b64decode(self.image))
        except Exception as e:
            return f"Portrait save failed: {e}", SkillResult.FAILURE
        self.logger.info(f"[take_selfie] saved portrait to {PORTRAIT_OUT}")
        return f"Portrait saved to {PORTRAIT_OUT}", SkillResult.SUCCESS

    def cancel(self):
        return "Portrait cannot be cancelled."
