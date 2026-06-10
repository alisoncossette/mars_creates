# akamai-hack

> **Mars, the roving interviewer.** The Innate **Mars** robot rolls up to people, asks if they're
> open to a quick interview, records on a *yes*, asks a few questions, and turns each conversation
> into a polished published post in real time — streamed/delivered on **Akamai**, visuals by **Magnific**.

## Concept

An autonomous robot field reporter. Mars roams a space (event, office, expo), finds a person,
gets **consent**, runs a short voice interview, and the moment it wraps it generates and publishes
a post from the conversation — image enhanced by Magnific, copy pulled from what was actually said,
delivered over Akamai. A content creator that *makes its own content by talking to people.*

## Interaction flow

1. **Roam → spot a person.**
2. **Ask consent** (voice): *"Hi, I'm Mars — would you be open to a quick interview?"*
3. **Listen.** Yes → start recording (both cameras + audio). No → thanks, move on. *(Records only on a verified yes.)*
4. **Interview.** LLM-driven Q&A — asks a few questions, listens, throws a follow-up or two.
5. **Confirm publish** (voice): *"Want me to post this?"* → only publishes on a second yes.
6. **Create.** Magnific enhances a strong frame; LLM writes the caption + pulls a quote.
7. **Post.** Publish; Akamai delivers it (and the live stream, if on).

## Architecture (data flow)

```
[ Mars · 2 cameras + mic/speaker ]
   roam -> detect person -> TTS consent prompt
        |  STT: yes/no  -- no -> move on
        v yes
   record (cameras + audio)  --live-->  Akamai media streaming (optional live view)
        |  LLM interview loop: TTS question -> STT answer -> follow-up
        v  wrap + TTS "post this?" -> STT yes
   [ pipeline service · Akamai Cloud (Linode) ]
        |-> Magnific API   -> enhance a frame into the post visual
        |-> LLM            -> caption + pull a quote from the transcript
        |-> post           -> X / web gallery (served via Akamai CDN)
        v
   [ published post ]  --delivered by-->  Akamai CDN
```

## Components

| Piece | Job | Candidate |
|---|---|---|
| Locomotion + perception | roam, find + approach a person | Innate Mars SDK |
| Voice out (TTS) | ask consent + questions | ElevenLabs / OpenAI TTS |
| Hearing (STT) | consent + answers | Deepgram / Whisper |
| Interview brain | drive Q&A, follow-ups, captions | Claude |
| Recording | both cams + audio | local capture |
| Streaming / delivery | live feed + post delivery | **Akamai** (Linode + media/CDN) |
| Content creation | enhance frame -> post visual | **Magnific** (Freepik API) |
| Publisher | post the content | X API / self-hosted gallery |

## Consent by design (don't skip this)

Recording and publishing a *person* needs real consent — **twice**:
- **Consent to record** — only start the cameras/mic on a clear *yes*.
- **Consent to publish** — confirm before the post goes live (or play it back first).

This isn't only ethics — it's the strongest beat in the demo: a robot that **won't record or post
someone without a verified yes.** (Verify before an irreversible action — recording, publishing.)

## Open questions (resolve first)

- [ ] **Mars audio I/O** — usable **mic + speaker** onboard, or tether a phone/laptop for voice?
- [ ] **Innate SDK** — camera frame grab + locomotion + person-detection API?
- [ ] **Akamai** — which resource the hack gives (Linode compute / media streaming / EdgeWorkers)?
- [ ] **Magnific / Freepik API** — key + operation (upscale vs. style/relight)?
- [ ] **Post target** — X API, or a self-hosted gallery over Akamai CDN?

## Stack

- Robot + pipeline: **Python** (likely) · service: FastAPI on Linode · _confirm_

## Notes

- Lives outside OneDrive on purpose (fast installs, no file-lock hell).
