# akamai-hack

> **Mars, the roving interviewer.** An Innate MARS agent that rolls up to people, gets consent,
> runs a short voice interview, and turns each chat into a published post — visuals by **Magnific**,
> delivered on **Akamai**. Built the Innate-native way: an Agent + a custom integration skill.

## How it maps to Innate (the real architecture)

Innate is **declarative** — the cloud brain runs the conversation, voice (mic + Cartesia/ElevenLabs
TTS), and the loop. You write a **prompt + a skill list**, not a control loop.

```
agents/interviewer.py        -> drop in robot ~/agents/   (the Agent: prompt + skills + ["micro"])
skills/publish_interview.py  -> drop in robot ~/skills/   (local/publish_interview integration skill)
mars/                        -> reusable lib the skill calls (Magnific, gallery+X, EventContext)
run_mars.py                  -> local OFF-robot harness to test the publish pipeline (no robot/keys)
```

- **Agent** (`MarsInterviewer`): `get_inputs() -> ["micro"]`, `uses_gaze() -> True`, skills =
  `innate-os/navigate_to_position`, `innate-os/wave`, `innate-os/head_emotion`,
  `local/capture_image`, `local/publish_interview`. The **prompt** is the whole behavior:
  roam → consent → interview (event/sponsor-aware) → consent-to-publish → post.
  (Pattern matches your `ruby_assistant_from_mars.py`.)
- **Skill** (`PublishInterview`): an integration skill like `innate-os/send_email`. Its
  `execute(quote, summary)` captures a frame, runs Magnific, writes the caption, posts to
  gallery + X. Body = `mars/` (already tested via `run_mars.py`).

## Consent by design (the demo's strongest beat)

Two hard rules baked into the prompt: **consent to chat**, then **consent to publish** — no
recording-for-posting or publishing without a clear spoken yes. A robot that *won't act on a
person without verified consent.*

## What the brain handles vs. what we built

| Handled by Innate OS | Built here |
|---|---|
| Conversation, voice (STT/TTS), the loop | The interviewer **prompt** + skill list |
| Navigation, gaze, cameras, WebRTC stream | The **publish** integration skill |
| Skill orchestration (LLM picks skills) | Magnific + caption + gallery/X (`mars/`) |

## Streaming (your concern, settled)

Core path is **record→publish**: capture a frame → Magnific → gallery served via **Akamai CDN**
(+ X). It always works. The robot already has **`innate_webrtc_streamer`** for a live camera feed
— tap that for a live view later (MARS_LIVE=1) if Akamai wants live; not on the critical path.

## Run it now (off-robot, zero keys)

```bash
python run_mars.py --rounds 1      # plays the whole flow; type the guest's answers
```

Then drop keys in `.env` (Anthropic, ElevenLabs/Deepgram, Freepik/Magnific, Akamai gallery, X).

## Deploy to the robot

1. Make `mars` importable in the innate env (`pip install -e .`, or copy `mars/` next to the skill).
2. Copy `agents/interviewer.py` → robot `~/agents/`, `skills/publish_interview.py` → `~/skills/`.
3. Wire the two TODOs in the skill: the camera frame grab (`maurice_cam`) and confirm the `Skill`
   base/metadata against an existing innate-os integration skill (`send_email`).
4. Set `MARS_EVENT_*` (or let Mars ask the operator at kickoff). Start the agent.

## Open questions (small now)

- [ ] Exact `Skill` base class + metadata fields (confirm vs. innate-os `send_email`).
- [ ] Camera frame-grab API inside a skill (maurice_cam topic / `local/capture_image` helper).
- [ ] Akamai gallery: Linode origin URL + upload endpoint. Magnific (Freepik) key. X harness (Tweepy vs Composio).

## Notes
- Repo lives outside OneDrive on purpose (fast installs, no file-lock hell).
