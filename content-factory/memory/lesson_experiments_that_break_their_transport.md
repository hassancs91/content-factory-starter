---
name: Experiments that break their own transport need a detached runner and an ordering rule
description: When a piece's experiments sever the SSH/network path you drive them over, pipe-the-script-over-SSH loses the evidence; run detached + poll + fetch, assert healthy BEFORE each break, and run every reverting experiment before the terminal-state script.
type: lesson
---

The Coolify SSH-lockout piece (2026-07-27) ran nine experiments whose whole purpose was to
break SSH on a droplet reachable only over SSH. Three separate failures came out of that
shape, and all three generalise to any piece that breaks its own transport (firewall rules,
network config, reverse proxies, the Coolify panel itself).

**1. Never run the experiment through the connection it breaks.**
The first pattern was `do.py run <slug> -- 'bash -s' < script > evidence.out`. E1's break
killed the pipe mid-run and the evidence file came back with 8 of 90 lines. The fix is
`scripts/_run_detached.sh`: upload the script, launch it with `setsid nohup ... &` writing to
a file ON the box plus a `.done` sentinel, poll for the sentinel, then fetch. Polling that
fails during the break window is fine, it just retries. This also makes the port-change and
lockout experiments possible at all.

**2. Assert healthy BEFORE the break, in the script.**
E1's first run applied its break against a box whose probe was already failing, for an
unrelated reason (a hardcoded key path that no longer existed). Without a healthy-before
assertion the output would have looked like a perfectly good result and the guide would have
shipped a false claim. Every break script now starts by proving the healthy path, and the
revert ends by proving it again.

**3. Reverting experiments must run BEFORE the terminal-state script.**
The dead-man revert deliberately runs `ufw --force disable`, because a bad firewall rule is
one of the ways you lose a box. Correct during breaks, wrong afterwards: E7b ran after the
terminal-state script E6 and silently switched the firewall back off, leaving sshd hardened
but the box open. It only surfaced because an independent external verification re-ran.
Either order the manifest so every reverting experiment precedes the terminal state, or ship
a re-apply script (`e6c_reapply_firewall.sh`) and re-verify.

**Corollary: verify the terminal state from OUTSIDE the box.** E6's own probes went to
localhost, which never crosses UFW. `e6b_verify_from_outside.sh` runs from the workstation
over the public internet and is what actually proved the claim.

**And the dead-man switch earns its keep.** A `systemd-run --on-active=5min` timer that
restores sshd_config, drop-ins, PAM and authorized_keys meant a real unplanned lockout cost
one DigitalOcean API `power_cycle` and 30 seconds, not a rebuilt droplet. Arm it before every
break, disarm explicitly, and have it log whether a listener came back.
