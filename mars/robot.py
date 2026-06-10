"""MarsClient — the abstraction over the Innate Mars robot.

This is the ONLY file that touches robot hardware. Every method is stubbed to run in MOCK
mode (logs + returns placeholders) so the whole agent runs end-to-end today. Wire the real
Innate SDK in at each `# TODO(innate-sdk)` and nothing else changes.

Hardware Mars exposes (confirmed): 2 cameras, onboard mic + speaker, locomotion.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass

log = logging.getLogger("mars.robot")


@dataclass
class Person:
    """A detected person Mars can approach."""
    id: str
    bearing_deg: float = 0.0     # where they are relative to Mars
    distance_m: float = 1.5


class MarsClient:
    def __init__(self, mock: bool = True):
        self.mock = mock
        self._connected = False

    def connect(self) -> None:
        # TODO(innate-sdk): initialize the Innate Mars connection / SDK session here.
        log.info("[robot] connect (mock=%s)", self.mock)
        self._connected = True

    # --- locomotion + perception ---
    def wander(self, seconds: float = 3.0) -> None:
        """Roam the space looking for someone to interview."""
        # TODO(innate-sdk): drive a short exploratory path.
        log.info("[robot] wandering for %.1fs", seconds)
        if self.mock:
            time.sleep(0.2)

    def find_person(self) -> Person | None:
        """Person detection from the cameras. Returns the nearest approachable person."""
        # TODO(innate-sdk): run person detection on a camera frame; return their bearing/distance.
        if self.mock:
            log.info("[robot] find_person -> mock person")
            return Person(id="mock-person", bearing_deg=0.0, distance_m=1.5)
        return None

    def approach(self, person: Person) -> None:
        """Move toward the person and stop at a polite interviewing distance."""
        # TODO(innate-sdk): turn to bearing, drive to ~1m, face them.
        log.info("[robot] approaching %s", person.id)

    # --- vision ---
    def capture_frame(self, cam: int = 0) -> bytes:
        """A single JPEG frame from camera 0 (front/face) or 1 (wide/context)."""
        # TODO(innate-sdk): grab a frame from the requested camera.
        log.info("[robot] capture_frame cam=%d", cam)
        return b""  # mock: empty bytes; real impl returns JPEG bytes

    # --- audio (onboard mic + speaker) ---
    def play_audio(self, wav: bytes) -> None:
        """Play synthesized speech out the onboard speaker."""
        # TODO(innate-sdk): pipe wav bytes to the speaker.
        log.info("[robot] speaker <- %d bytes", len(wav))

    def record_audio(self, max_seconds: float = 20.0, silence_stop: bool = True) -> bytes:
        """Capture a spoken answer from the onboard mic (stop on silence)."""
        # TODO(innate-sdk): record from mic until silence or max_seconds.
        log.info("[robot] mic recording (max=%.0fs)", max_seconds)
        return b""  # mock: empty bytes; real impl returns wav bytes

    # --- AV recording of the interview (both cams + audio) ---
    def start_av_recording(self) -> str:
        """Begin recording the interview: camera 0 + camera 1 + audio. Returns a handle/path."""
        # TODO(innate-sdk): start synchronized AV capture from both cameras + mic.
        path = f"recordings/interview-{int(time.time())}.mp4"
        log.info("[robot] START av recording -> %s", path)
        return path

    def stop_av_recording(self, handle: str) -> str:
        """Stop recording; return the path to the finished file."""
        # TODO(innate-sdk): finalize + mux the recording.
        log.info("[robot] STOP av recording -> %s", handle)
        return handle
