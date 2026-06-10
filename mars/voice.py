"""Voice — TTS (speak) + STT (listen) on Mars's onboard mic + speaker.

MOCK mode (no keys): `say` prints the line, `listen` reads from the keyboard — so the whole
interview is a playable text simulation today. Drop in real providers at the TODOs.
"""
from __future__ import annotations

import logging

from .config import Settings
from .robot import MarsClient

log = logging.getLogger("mars.voice")


class Voice:
    def __init__(self, robot: MarsClient, settings: Settings):
        self.robot = robot
        self.s = settings
        self.mock_tts = not (settings.elevenlabs_api_key or settings.openai_api_key)
        self.mock_stt = not (settings.deepgram_api_key or settings.openai_api_key)

    # --- speak ---
    def say(self, text: str) -> None:
        if self.mock_tts:
            print(f"\n[MARS 🔊] {text}")
            return
        wav = self._synthesize(text)   # TODO(tts): ElevenLabs / OpenAI -> wav bytes
        self.robot.play_audio(wav)

    def _synthesize(self, text: str) -> bytes:
        # TODO(tts): call ElevenLabs (self.s.elevenlabs_api_key) or OpenAI; return wav bytes.
        log.info("[voice] synthesize %d chars", len(text))
        return b""

    # --- listen ---
    def listen(self, max_seconds: float = 25.0) -> str:
        if self.mock_stt:
            try:
                return input("[guest ⌨️ ] ").strip()
            except EOFError:
                return ""
        wav = self.robot.record_audio(max_seconds=max_seconds, silence_stop=True)
        return self._transcribe(wav)  # TODO(stt): Deepgram / Whisper -> text

    def _transcribe(self, wav: bytes) -> str:
        # TODO(stt): call Deepgram (self.s.deepgram_api_key) or whisper; return text.
        log.info("[voice] transcribe %d bytes", len(wav))
        return ""

    # --- convenience ---
    def ask(self, prompt: str) -> str:
        self.say(prompt)
        return self.listen()
