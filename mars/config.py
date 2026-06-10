"""Settings + EventContext.

EventContext is the "vibe + sponsors" layer: at kickoff Mars learns the event so the
interview brain can weave the event name, theme, and sponsors into its questions. If the
fields are blank, Mars *asks the operator out loud* at startup (see EventContext.brief()).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

try:  # optional — mock mode runs with stdlib only
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, "1" if default else "0").strip().lower() in {"1", "true", "on", "yes"}


@dataclass
class Settings:
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    llm_model: str = os.getenv("MARS_LLM_MODEL", "claude-opus-4-8")

    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    deepgram_api_key: str = os.getenv("DEEPGRAM_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    magnific_api_key: str = os.getenv("MAGNIFIC_API_KEY", "")
    magnific_base_url: str = os.getenv("MAGNIFIC_BASE_URL", "https://api.magnific.com")
    magnific_scale: int = int(os.getenv("MARS_MAGNIFIC_SCALE", "2"))

    # Akamai Cloud = Linode Object Storage (S3-compatible), fronted by Akamai CDN
    s3_endpoint: str = os.getenv("LINODE_S3_ENDPOINT", "")        # e.g. https://us-east-1.linodeobjects.com
    s3_region: str = os.getenv("LINODE_S3_REGION", "us-east-1")
    s3_bucket: str = os.getenv("LINODE_S3_BUCKET", "")
    s3_key: str = os.getenv("LINODE_S3_ACCESS_KEY", "")
    s3_secret: str = os.getenv("LINODE_S3_SECRET_KEY", "")
    cdn_base_url: str = os.getenv("AKAMAI_CDN_BASE_URL", "")      # optional custom Akamai domain
    rtmp_ingest_url: str = os.getenv("AKAMAI_RTMP_INGEST_URL", "")
    stream_key: str = os.getenv("AKAMAI_STREAM_KEY", "")

    @property
    def s3_configured(self) -> bool:
        return all([self.s3_endpoint, self.s3_bucket, self.s3_key, self.s3_secret])

    publish_gallery: bool = _bool("MARS_PUBLISH_GALLERY", True)
    publish_x: bool = _bool("MARS_PUBLISH_X", True)
    x_keys: dict = field(default_factory=lambda: {
        "api_key": os.getenv("X_API_KEY", ""),
        "api_secret": os.getenv("X_API_SECRET", ""),
        "access_token": os.getenv("X_ACCESS_TOKEN", ""),
        "access_secret": os.getenv("X_ACCESS_SECRET", ""),
    })

    live: bool = _bool("MARS_LIVE", False)
    max_questions: int = int(os.getenv("MARS_MAX_QUESTIONS", "4"))

    @property
    def mock_llm(self) -> bool:
        return not self.anthropic_api_key


@dataclass
class EventContext:
    """What event Mars is roaming. Drives sponsor/vibe-aware interview questions."""
    name: str = os.getenv("MARS_EVENT_NAME", "")
    location: str = os.getenv("MARS_EVENT_LOCATION", "")
    vibe: str = os.getenv("MARS_EVENT_VIBE", "")
    sponsors: list[str] = field(default_factory=lambda: [
        s.strip() for s in os.getenv("MARS_EVENT_SPONSORS", "").split(",") if s.strip()
    ])

    def is_complete(self) -> bool:
        return bool(self.name and self.sponsors)

    def brief(self, voice) -> None:
        """Fill any missing fields by ASKING the operator out loud at kickoff."""
        if not self.name:
            self.name = voice.ask("Before we start — what event are we at today?") or "this event"
        if not self.sponsors:
            raw = voice.ask("And who are the sponsors I should mention?")
            self.sponsors = [s.strip() for s in (raw or "").replace(" and ", ",").split(",") if s.strip()]
        if not self.vibe:
            self.vibe = voice.ask("How would you describe the vibe here in a few words?") or ""

    def prompt_block(self) -> str:
        """Injected into the interview system prompt so questions reference the event + sponsors."""
        sponsors = ", ".join(self.sponsors) if self.sponsors else "(none known yet)"
        return (
            f"EVENT CONTEXT — weave this in naturally whenever it fits:\n"
            f"  Event: {self.name or 'unknown'}\n"
            f"  Location: {self.location or 'unknown'}\n"
            f"  Vibe/theme: {self.vibe or 'unknown'}\n"
            f"  Sponsors to give a shout-out to when relevant: {sponsors}\n"
            f"Ask at least one question that ties to the event or a sponsor "
            f"(e.g. how they're finding {self.name or 'the event'}, or whether they've "
            f"tried something from a sponsor). Keep it light and human, never an ad read."
        )
