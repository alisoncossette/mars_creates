"""The interview: consent gating + an adaptive, event/sponsor-aware Q&A driven by Claude."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from . import llm
from .config import EventContext, Settings
from .voice import Voice

log = logging.getLogger("mars.interview")

_AFFIRM = {"yes", "yeah", "yep", "sure", "ok", "okay", "go", "do it", "of course", "absolutely", "fine", "y"}
_DENY = {"no", "nope", "nah", "don't", "do not", "rather not", "pass", "stop", "n"}


def yes_no(voice: Voice, prompt: str, settings: Settings) -> bool:
    """Ask a yes/no and read the answer robustly. Defaults to NO when unclear (consent-safe)."""
    ans = voice.ask(prompt).lower().strip()
    if any(w in ans for w in _DENY):
        return False
    if any(ans == w or ans.startswith(w + " ") or (" " + w) in (" " + ans) for w in _AFFIRM):
        return True
    if settings.mock_llm:
        return ans.startswith("y")
    verdict = llm.complete(
        settings,
        system="Classify the reply as a yes or no to the question. Reply with exactly YES or NO.",
        user=f"Question: {prompt}\nReply: {ans}",
        max_tokens=3,
    ).upper()
    return "YES" in verdict


def consent_to_record(voice: Voice, settings: Settings, event: EventContext) -> bool:
    ev = event.name or "the event"
    return yes_no(
        voice,
        f"Hi! I'm Mars, roaming {ev} collecting quick interviews. "
        f"Would you be open to a 30-second chat I might post? It's totally optional.",
        settings,
    )


def consent_to_publish(voice: Voice, settings: Settings) -> bool:
    return yes_no(voice, "That was great — okay if I post this with a photo?", settings)


@dataclass
class Transcript:
    turns: list[tuple[str, str]] = field(default_factory=list)  # (speaker, text)

    def as_text(self) -> str:
        return "\n".join(f"{'Mars' if who == 'mars' else 'Guest'}: {t}" for who, t in self.turns)

    def guest_lines(self) -> list[str]:
        return [t for who, t in self.turns if who == "guest" and t]


class InterviewBrain:
    def __init__(self, settings: Settings, event: EventContext):
        self.s = settings
        self.event = event

    def _system(self) -> str:
        return (
            "You are Mars, a friendly roving robot interviewer making short, postable street-style "
            "interviews. Ask ONE short, warm, specific question at a time. Be curious and human, "
            "never an ad read. Adapt to their last answer.\n\n" + self.event.prompt_block()
            + "\n\nWhen you've gotten a fun, postable moment (usually after 3-4 exchanges), reply with "
            "exactly the token DONE instead of another question."
        )

    def run_interview(self, voice: Voice) -> Transcript:
        t = Transcript()
        opener = (
            f"Awesome — thanks! So, how are you finding {self.event.name or 'today'}?"
            if not self.s.mock_llm else
            f"Awesome — thanks! How are you finding {self.event.name or 'today'}?"
        )
        voice.say(opener); t.turns.append(("mars", opener))
        t.turns.append(("guest", voice.listen()))

        for _ in range(max(1, self.s.max_questions - 1)):
            q = self._next_question(t)
            if not q or q.strip().upper() == "DONE":
                break
            voice.say(q); t.turns.append(("mars", q))
            t.turns.append(("guest", voice.listen()))

        closing = "Love it. Thanks so much — enjoy the rest of it!"
        voice.say(closing); t.turns.append(("mars", closing))
        return t

    def _next_question(self, t: Transcript) -> str:
        if self.s.mock_llm:
            # Mock still demonstrates event/sponsor awareness:
            sponsor = self.event.sponsors[0] if self.event.sponsors else "the sponsors"
            canned = [
                f"Nice! Have you checked out anything from {sponsor} yet?",
                f"What's the highlight of {self.event.name or 'the event'} so far?",
                "If you could tell everyone watching one thing, what would it be?",
            ]
            asked = sum(1 for who, _ in t.turns if who == "mars") - 1
            return canned[asked] if asked < len(canned) else "DONE"
        return llm.complete(self.s, self._system(), t.as_text() + "\n\nMars:", max_tokens=60)
