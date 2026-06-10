"""MarsAgent — the orchestrator that ties every tool together.

Kickoff: learn the event (ask the operator if unknown).
Each round: roam -> find someone -> consent-to-record -> interview (event/sponsor-aware) ->
record both cams + audio -> consent-to-publish -> Magnific + caption -> post (gallery + X).
"""
from __future__ import annotations

import logging

from .config import EventContext, Settings
from .content import compose_post
from .interview import InterviewBrain, consent_to_publish, consent_to_record
from .media import LiveStream
from .publish import Publisher
from .robot import MarsClient
from .voice import Voice

log = logging.getLogger("mars.agent")


class MarsAgent:
    def __init__(
        self,
        settings: Settings,
        event: EventContext,
        robot: MarsClient,
        voice: Voice,
        brain: InterviewBrain,
        publishers: list[Publisher],
        live: LiveStream,
    ):
        self.s = settings
        self.event = event
        self.robot = robot
        self.voice = voice
        self.brain = brain
        self.publishers = publishers
        self.live = live

    def run(self, max_rounds: int | None = None) -> None:
        self.robot.connect()

        # --- kickoff briefing: capture the vibe + sponsors ---
        if not self.event.is_complete():
            log.info("[agent] event unknown — asking the operator…")
            self.event.brief(self.voice)
        log.info(
            "[agent] briefed | event=%r sponsors=%s vibe=%r",
            self.event.name, self.event.sponsors, self.event.vibe,
        )

        n = 0
        while max_rounds is None or n < max_rounds:
            try:
                self.one_round()
            except KeyboardInterrupt:
                log.info("[agent] stopping.")
                break
            n += 1

    def one_round(self) -> None:
        self.robot.wander()
        person = self.robot.find_person()
        if person is None:
            return
        self.robot.approach(person)

        # 1) consent to record
        if not consent_to_record(self.voice, self.s, self.event):
            self.voice.say("No worries — enjoy the event!")
            return

        # 2) record (both cams + audio) + optional live stream, while interviewing
        self.live.start()
        handle = self.robot.start_av_recording()
        transcript = self.brain.run_interview(self.voice)
        self.robot.stop_av_recording(handle)
        self.live.stop()

        # 3) consent to publish (verify before the irreversible action)
        if not consent_to_publish(self.voice, self.s):
            self.voice.say("Totally fine — I won't post it. Thanks!")
            return

        # 4) create (Magnific + caption + quote) and publish (gallery + X)
        hero = self.robot.capture_frame(cam=0)
        post = compose_post(transcript, hero, self.event, self.s)
        for pub in self.publishers:
            url = pub.publish(post)
            log.info("[agent] posted via %s -> %s", pub.name, url)
            print(f"  ✅ posted to {pub.name}: {url}")
