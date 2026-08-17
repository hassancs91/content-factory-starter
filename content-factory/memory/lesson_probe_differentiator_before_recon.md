---
name: lesson_probe_differentiator_before_recon
description: If a cheap probe can test whether a piece has a real differentiator, run it BEFORE S2 recon — it changes what recon is for.
---

# Probe for a differentiator before you spend recon

S2 recon is framed as "find the gap". But when a piece is a sequel, or the topic is one you
already have infrastructure for, you can often **test the gap directly in minutes**, before
spending keyword-tool credits or fetching 15 SERP pages.

On `secure-coolify-vps` the open question was whether the piece was anything more than the
generic VPS-hardening checklist everyone has published. Two read-only scripts against a
droplet that was already alive answered it: ufw allowed 22/80/443/8000 while 6001 and 6002
were accepting connections from the public internet, on a stock Coolify install, because
Docker's DNAT rules bypass ufw's filter chain. Cost: about ten minutes and $0.

That flipped recon's job from "hunt for an angle" to "size the demand and competition for
the angle we already proved". Different searches, different report, much lower risk of a
Checkpoint 1 built on a guess.

**When it applies:** the piece is a sequel to a shipped one, or lab infra from a previous
piece is still alive, or the differentiator hypothesis is a factual claim about software
behaviour rather than a claim about what readers want.

**When it does not:** anything about audience demand, search volume, or what competitors
cover. Those are recon's actual job and a probe cannot answer them.

**Record it as provisional.** Discovery evidence gathered before S3 has not been through the
manifest, so mark it clearly and re-run it properly in S4. And flag what the probe did NOT
explain rather than smoothing it over: the same run found port 8080 listening on `0.0.0.0`
with a DNAT rule but closed from outside, which contradicts the tidy story. That is an S4
question now, not a sentence in the draft.

**Method note that cost a round:** probe reachability with a real TCP connect
(`/dev/tcp/$ip/$port`), never `curl`. curl reported port 22 as unreachable on a box we were
actively SSH'd into, because sshd does not answer HTTP.
