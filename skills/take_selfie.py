#!/usr/bin/env python3
"""take_selfie — grab a selfie from the arm's wrist camera at its CURRENT pose.

The operator poses the arm once at the best selfie angle (torque holds it), so this skill does
NOT move the arm — it just captures the wrist (arm) camera and saves it for publish_interview.
Uses the proper RobotState API (same wrist image record_position uses), so no ROS/serial access.

Deploy: ~/skills/take_selfie.py (auto-discovered as local/take_selfie).
"""
from __future__ import annotations

import base64

from brain_client.skill_types import RobotState, RobotStateType, Skill, SkillResult

SELFIE_OUT = "/tmp/mars_selfie.jpg"


class TakeSelfie(Skill):
    """Snap a selfie from the arm's wrist camera (current pose) and save it for publishing."""

    image = RobotState(RobotStateType.LAST_WRIST_CAMERA_IMAGE_B64)

    def __init__(self, logger):
        super().__init__(logger)

    @property
    def name(self):
        return "take_selfie"

    def guidelines(self):
        return (
            "Take a selfie with the arm's wrist camera from its current pose (the arm is already "
            f"posed for selfies). Saves the photo to {SELFIE_OUT} — call this right before "
            "publish_interview and pass that path as image_path. Use after the guest said yes."
        )

    def execute(self):
        if not self.image:
            return "No wrist camera image available yet.", SkillResult.FAILURE
        try:
            with open(SELFIE_OUT, "wb") as f:
                f.write(base64.b64decode(self.image))
        except Exception as e:
            return f"Selfie save failed: {e}", SkillResult.FAILURE
        self.logger.info(f"[take_selfie] saved {SELFIE_OUT}")
        return f"Selfie saved to {SELFIE_OUT}", SkillResult.SUCCESS

    def cancel(self):
        return "Selfie cannot be cancelled."
