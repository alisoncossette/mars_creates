# akamai-hack

> Self-improving embodied agent — a small floor robot that knows the limits of its body,
> writes itself a new agent when it hits a wall, and **won't take an irreversible action on an unverified guess.**

*(Working concept — swap freely if this repo is for a different build.)*

## The idea

The robot's day job is **picking up litter**. The real build is making it *smart about what it
picks up* and able to **build itself a new agent, live, when it hits something it can't handle.**

Differentiator: most robot demos make the robot *act*. This one knows when an action is
**irreversible** (throwing something away) and verifies before it commits — and when it hits its
limits, it generates the skill to do the right thing.

## Core loop

1. **Perceive** — camera spots an object on the floor.
2. **Verify before acting** — trash, or a dropped valuable? Cup/wrapper → bin it. Phone/wallet/badge → stop.
3. **Gap detection** — "beyond my body + my skills → I need a new agent: find the owner."
4. **Build it live** — Claude Code scaffolds a `find-owner` agent (read badge / look up attendee / route to lost-and-found).
5. **Verify the match** — right owner, real contact, not a hallucinated guess.
6. **Act + self-update** — return the item; the new agent joins the roster permanently.

**Live demo:** plant a phone in a pile of litter → robot picks the wrappers, catches that the phone
*isn't* trash, builds a find-owner agent on the spot, and returns it — on stage.

## Stack

- Robot: Innate **Mars** (small floor robot, single small arm)
- Agent generation: **Claude Code**
- _TODO: search / voice / verify layer / orchestration — fill in_

## Setup

```
# TODO
```

## Notes

- Lives outside OneDrive on purpose (fast installs, no file-lock hell).
