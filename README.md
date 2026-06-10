# akamai-hack

> **The robot as an autonomous content creator.** The Innate **Mars** robot streams both cameras,
> turns its point-of-view into striking AI-enhanced content with **Magnific**, and **posts it live** —
> delivered on **Akamai**.

## Concept

Mars roams with two cameras. A pipeline pulls frames, runs them through Magnific to create
gallery-grade content, writes a caption from what the robot is actually seeing, and publishes —
all without a human in the loop. Content, created and posted *directly from the robot.*

## Architecture (data flow)

```
[ Mars robot · 2 cameras ]
        │  capture frames (both feeds)
        ▼
[ capture/stream layer ]  ──(live feed)──►  Akamai media streaming (optional live view)
        │  pick / composite best frame(s)
        ▼
[ pipeline service on Akamai Cloud (Linode) ]
        ├─► Magnific API  →  enhance / upscale / restyle into content
        ├─► caption (LLM)  →  text from the robot's view
        └─► post  →  X / web gallery (gallery served via Akamai CDN)
        ▼
[ published content ]  ──delivered by──►  Akamai CDN
```

## Where each sponsor slots in

- **Akamai** — host the pipeline service on **Akamai Cloud (Linode)**; deliver the generated
  content (and an optional live dual-cam feed) via Akamai's **media streaming / CDN**.
- **Magnific** (now via the Freepik API) — the *create* step: upscale / enhance / reimagine
  raw robot frames into polished content.

## Pipeline steps

1. **Capture** both camera feeds from Mars.
2. **Curate** — pick the frame(s) worth posting (a quality gate, not "post everything").
3. **Create** — Magnific enhances/transforms the chosen frame into content.
4. **Caption** — LLM writes copy from what the robot saw.
5. **Post** — publish to the target; Akamai delivers it.

## Open questions (resolve first)

- [ ] **Innate Mars SDK** — how are the *two* cameras exposed? (frame grab API / RTSP / ROS topic?)
- [ ] **Akamai** — which resource does the hack provide? (Linode compute credits / media streaming / EdgeWorkers?)
- [ ] **Magnific / Freepik API** — key access + which operation (upscale vs. style/relight)?
- [ ] **Post target** — X API, or a self-hosted web gallery served over Akamai CDN?

## Stack

- Robot + pipeline: **Python** (likely — robot SDKs lean that way) · _confirm_
- Service: FastAPI on Linode · _TODO_

## Notes

- Lives outside OneDrive on purpose (fast installs, no file-lock hell).
