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
    """Magnific Creative Upscaler (api.magnific.com): make the camera grab post-worthy.
    Async submit -> poll. Falls back to the original frame on ANY failure, so a post always
    goes out. Exact field/header names are best-guess from the docs — confirm with one real
    call once the key is in; the graceful fallback makes a wrong guess harmless (posts raw photo).
    """
    if not settings.magnific_api_key or not frame_jpeg:
        log.info("[content] magnific MOCK (no key / empty frame) -> passthrough %d bytes", len(frame_jpeg))
        return frame_jpeg
    try:
        import base64
        import time
        import httpx

        base = settings.magnific_base_url.rstrip("/")
        headers = {"x-magnific-api-key": settings.magnific_api_key}  # TODO confirm header name
        b64 = base64.b64encode(frame_jpeg).decode()

        submit = httpx.post(
            f"{base}/v1/ai/image-upscaler",
            headers=headers,
            json={"image": f"data:image/jpeg;base64,{b64}", "scale_factor": settings.magnific_scale},
            timeout=30,
        )
        submit.raise_for_status()
        body = submit.json()
        task_id = body.get("id") or body.get("task_id") or body.get("data", {}).get("id")

        for _ in range(40):  # ~80s max
            time.sleep(2)
            st = httpx.get(f"{base}/v1/ai/image-upscaler/{task_id}", headers=headers, timeout=30).json()
            status = (st.get("status") or st.get("state") or "").lower()
            if status in {"completed", "success", "succeeded", "done", "finished"}:
                url = st.get("result") or st.get("image_url") or st.get("output", {}).get("url") \
                    or (st.get("images") or [{}])[0].get("url")
                if url:
                    log.info("[content] magnific upscaled -> downloading result")
                    return httpx.get(url, timeout=60).content
                break
            if status in {"failed", "error", "cancelled"}:
                break
        log.warning("[content] magnific didn't finish; using original frame")
    except Exception as e:
        log.warning("[content] magnific failed (%s); using original frame", e)
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
