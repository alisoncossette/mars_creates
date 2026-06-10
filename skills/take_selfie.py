#!/usr/bin/env python3
"""take_selfie — swing the arm to a selfie pose and grab the wrist (arm) camera.

Matches the real on-robot arm-skill convention (from innate-os/skills/set_arm_joints.py):
  from brain_client.skill_types import Interface, InterfaceType, Skill, SkillResult
  manipulation = Interface(InterfaceType.MANIPULATION)  # class attr
  self.manipulation.move_to_joint_positions([j1..j5, gripper], duration, blocking)  # RADIANS

Deploy: ~/skills/take_selfie.py (auto-discovered as local/take_selfie). Reuses your
~/mars_camera_feed.py to grab the arm camera (no in-process rclpy clash).

CALIBRATE SELFIE_POSE on the robot: teleop the arm to a good selfie angle
(robohacks26/manipulation/scripts/teleop_arm.py), read the joint radians, paste them below.
"""
from __future__ import annotations

import os
import subprocess

from brain_client.skill_types import Interface, InterfaceType, Skill, SkillResult

CAM_SCRIPT = os.path.expanduser("~/mars_camera_feed.py")
ARM_CAM_TOPIC = "/mars/arm/image_raw/compressed"
SELFIE_OUT = "/tmp/mars_selfie.jpg"

# [base, shoulder, elbow, wrist_pitch, wrist_rotate, gripper] in RADIANS.
# PLACEHOLDER — calibrate via teleop. Limits: j1 +-3.14, j2 -1.57..1.22, j3/j4/j5 +-1.57, gripper 0..0.85.
SELFIE_POSE = [0.0, -0.6, 1.2, -0.8, 0.0, 0.3]


class TakeSelfie(Skill):
    """Pose the arm like a selfie stick and snap the arm camera."""

    manipulation = Interface(InterfaceType.MANIPULATION)

    def __init__(self, logger):
        super().__init__(logger)

    @property
    def name(self) -> str:
        return "take_selfie"

    def guidelines(self) -> str:
        return (
            "Pose the arm like a selfie stick and take a photo with the arm's camera. Use right "
            "before publishing, once the guest agreed to a selfie. Saves the photo to "
            f"{SELFIE_OUT} — pass that as image_path to publish_interview."
        )

    def execute(self, duration: int = 3):
        try:
            ok = self.manipulation.move_to_joint_positions(SELFIE_POSE, duration=duration, blocking=True)
            if ok is False:
                self.logger.warning("[take_selfie] arm move failed; shooting from current pose")
            subprocess.run(
                ["python3", CAM_SCRIPT, "--once", "--topic", ARM_CAM_TOPIC, "--out", SELFIE_OUT],
                timeout=15, check=False,
            )
            if os.path.exists(SELFIE_OUT):
                return f"Selfie saved to {SELFIE_OUT}", SkillResult.SUCCESS
            return "Selfie capture failed (no frame from arm camera).", SkillResult.FAILURE
        except Exception as e:
            return f"Selfie failed: {e}", SkillResult.FAILURE

    def cancel(self) -> str:
        return "Selfie cannot be cancelled once the arm starts posing."
