"""Optional live streaming: push Mars's feed to Akamai media ingest (RTMP) while interviewing.

Off by default (MARS_LIVE=0) — record→publish is the reliable core. Flip MARS_LIVE=1 to also
broadcast live. Stubbed so it no-ops cleanly until the Akamai ingest URL/key are set.
"""
from __future__ import annotations

import logging

from .config import Settings

log = logging.getLogger("mars.media")


class LiveStream:
    def __init__(self, settings: Settings):
        self.s = settings
        self.enabled = settings.live and bool(settings.rtmp_ingest_url and settings.stream_key)
        self._proc = None

    def start(self) -> None:
        if not self.s.live:
            return
        if not self.enabled:
            log.info("[live] requested but no AKAMAI_RTMP_INGEST_URL/STREAM_KEY -> skipping")
            return
        # TODO(akamai-live): spawn ffmpeg pushing composited cam0|cam1 + audio to
        # f"{rtmp_ingest_url}/{stream_key}" as RTMP; Akamai packages to HLS for viewers.
        log.info("[live] START rtmp push -> %s", self.s.rtmp_ingest_url)

    def stop(self) -> None:
        if self._proc:
            log.info("[live] STOP")
            self._proc = None
