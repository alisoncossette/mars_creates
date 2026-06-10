"""Create the post: Magnific enhances a frame; Claude writes the caption + pulls a quote."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from . import llm
from .config import EventContext, Settings
from .interview import Transcript

log = logging.getLogger("mars.content")


@dataclass
class Post:
    image: bytes            # enhanced image bytes (or b"" in mock)
    caption: str
    quote: str
    alt_text: str
    event: str


def enhance(frame_jpeg: bytes, settings: Settings) -> bytes:
    """Magnific (via Freepik API): upscale / style / relight the chosen frame into a hero image."""
    if not settings.freepik_api_key:
        log.info("[content] magnific MOCK (no FREEPIK_API_KEY) -> passthrough %d bytes", len(frame_jpeg))
        return frame_jpeg
    # TODO(magnific): POST frame to Freepik/Magnific API with op=settings.magnific_op, poll, return result bytes.
    log.info("[content] magnific %s", settings.magnific_op)
    return frame_jpeg


def compose_post(transcript: Transcript, frame_jpeg: bytes, event: EventContext, settings: Settings) -> Post:
    image = enhance(frame_jpeg, settings)

    quote = _best_quote(transcript, settings)
    caption = _caption(transcript, quote, event, settings)
    sponsors = " ".join("#" + s.replace(" ", "") for s in event.sponsors)
    caption = f"{caption}\n\n{sponsors}".strip()

    return Post(
        image=image,
        caption=caption,
        quote=quote,
        alt_text=f"Robot street interview at {event.name or 'an event'}.",
        event=event.name or "",
    )


def _best_quote(t: Transcript, settings: Settings) -> str:
    lines = t.guest_lines()
    if not lines:
        return ""
    if settings.mock_llm:
        return max(lines, key=len)  # crude: the longest answer
    return llm.complete(
        settings,
        system="Pull the single most quotable, postable sentence the guest said. Return only that sentence.",
        user=t.as_text(),
        max_tokens=60,
    ) or max(lines, key=len)


def _caption(t: Transcript, quote: str, event: EventContext, settings: Settings) -> str:
    if settings.mock_llm:
        q = f'"{quote}" ' if quote else ""
        return f"{q}— a quick one from {event.name or 'the floor'}. 🤖🎤"
    return llm.complete(
        settings,
        system=(
            "Write a short, punchy social caption (1-2 sentences) for a robot's street interview. "
            "Warm, a little playful. You may give a natural shout-out to a sponsor if it fits.\n\n"
            + event.prompt_block()
        ),
        user=f"Interview:\n{t.as_text()}\n\nBest quote: {quote}",
        max_tokens=120,
    )
