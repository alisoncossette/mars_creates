#!/usr/bin/env python3
"""take_selfie — capture an upright portrait directly from the OAK camera via OpenCV.

Bypasses the (uncalibrated) ROS camera pipeline entirely. /dev/video5 exposes the stereo raw
(640x240 = two eyes side by side, rotated 90°); we take the LEFT eye and rotate clockwise to
get an upright portrait. Saves to /tmp/mars_selfie.jpg for publish_interview.

Deploy: ~/skills/take_selfie.py (auto-discovered as local/take_selfie).
"""
from __future__ import annotations

from brain_client.skill_types import Skill, SkillResult

PORTRAIT_OUT = "/tmp/mars_selfie.jpg"
CAM_INDEX = 5         # /dev/video5 — OAK stereo raw, grabbable without calibration
WARMUP_FRAMES = 8     # let auto-exposure settle


def grab_portrait(out_path: str = PORTRAIT_OUT) -> bool:
    """Grab one upright portrait from the OAK camera. Returns True on success."""
    import cv2

    cap = cv2.VideoCapture(CAM_INDEX)
    try:
        for _ in range(WARMUP_FRAMES):
            cap.read()
        ok, frame = cap.read()
    finally:
        cap.release()
    if not ok or frame is None:
        return False
    left = frame[:, : frame.shape[1] // 2]                  # left eye of the stereo pair
    portrait = cv2.rotate(left, cv2.ROTATE_90_CLOCKWISE)    # upright
    cv2.imwrite(out_path, portrait)
    return True


class TakeSelfie(Skill):
    """Snap an upright portrait from the OAK camera (direct grab) and save it for publishing."""

    def __init__(self, logger):
        super().__init__(logger)

    @property
    def name(self):
        return "take_selfie"

    def guidelines(self):
        return (
            "Take a portrait of the person in front of Mars. Face them so they're centered first. "
            f"Saves the photo to {PORTRAIT_OUT} — call this right before publish_interview and pass "
            "that path as image_path. Use after the guest said yes."
        )

    def execute(self):
        try:
            ok = grab_portrait()
        except Exception as e:
            return f"Portrait capture failed: {e}", SkillResult.FAILURE
        if not ok:
            return f"Camera /dev/video{CAM_INDEX} gave no frame.", SkillResult.FAILURE
        self.logger.info(f"[take_selfie] saved portrait to {PORTRAIT_OUT}")
        return f"Portrait saved to {PORTRAIT_OUT}", SkillResult.SUCCESS

    def cancel(self):
        return "Portrait cannot be cancelled."
