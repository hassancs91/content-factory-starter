---
name: Write time-boxed lab experiments as "≥N hours, report the actual window"
description: A fixed "leave it up 24h" in an evidence manifest becomes a pipeline blocker; scope the experiment to a minimum useful window and state the real elapsed time in the guide instead.
type: lesson
---

The Plausible piece's E5 (does a fresh public VPS attract bot traffic?) was written into
the manifest as "same droplet left up ~24h". At the 16-hour mark everything downstream was
finished and the piece sat blocked waiting for a clock, with a droplet billing the whole
time. Hasan's call: *"do we really need to wait? cant we wite based on the time passed?"*

He was right, and the reason generalises: **the window length was framing, not
methodology.** No claim in the guide depended on the number being 24. Closing at 16.4h
gave numbers that were, if anything, more striking (50 attacker IPs, 1,820 SSH attempts,
675 usernames, `.env` hunted at 138 distinct paths) and the prose simply states its own
window: "in the 16 hours I measured", "under 12 hours of logging".

**How to apply:** in the evidence manifest, write exposure/soak experiments as
**"≥N hours, report the actual window"** with N set to the smallest span that makes the
point. Take an intermediate read early to confirm the logging is actually working (the
Plausible run nearly lost its HTTP window to a broken YAML edit that made Traefik silently
skip the access log). Then close whenever the pipeline is otherwise ready, and cite the
real elapsed time everywhere the numbers appear.

**Corollary:** anything that gates on wall-clock should be started as early in the piece as
possible, and the manifest should say what work happens *while* it runs, so a session
never sits idle waiting.
