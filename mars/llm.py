"""One place for the Claude call. MOCK mode (no key) returns a canned line so everything runs."""
from __future__ import annotations

import logging

from .config import Settings

log = logging.getLogger("mars.llm")


def complete(settings: Settings, system: str, user: str, max_tokens: int = 300) -> str:
    if settings.mock_llm:
        log.info("[llm] mock complete")
        return "[mock-llm] " + user[:80]
    # Real Claude
    from anthropic import Anthropic
    client = Anthropic(api_key=settings.anthropic_api_key)
    msg = client.messages.create(
        model=settings.llm_model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()
