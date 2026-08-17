# pkill -f can match the remote wrapper shell that carries it — and kill the ssh session

**What happened (coolify-zero-downtime-deployment, 2026-08-11):** the experiment runner
started each probe with `pkill -f 'probe.py'; ...; setsid nohup python3 /root/probe.py ...`
over ssh. The remote wrapper is `bash -c "<the whole command>"`, and that command line
CONTAINS the literal string `/root/probe.py` (as the start argument). So pkill matched the
wrapper itself, killed it, ssh died with **exit 255 and zero output**, and none of the
commands after pkill ran. The bracket trick (`[p]robe.py`) does NOT save you when the
command later names the real path — the wrapper still contains `probe.py` verbatim.

Three compounding traps in one bug:
1. It looks exactly like ssh flakiness (255, no stdout, no stderr) — I burned a retry
   loop on "sshd MaxStartups throttling" first.
2. The stale-state trap: the previous probe's log still existed, so a `tail` pre-check
   showed healthy 200 lines and passed while the probe was actually DEAD.
3. `subprocess.run(timeout=...)` on Windows can hang forever after killing do.py because
   the orphaned ssh child keeps the captured pipes open.

**Rules:**
- Kill remote processes with an ANCHORED pattern that can't match a shell wrapper:
  `pkill -f '^python3 /root/probe'` (wrapper cmdlines start with `bash -c`).
- A liveness pre-check must assert the log is GROWING (two line-counts 3s apart), never
  just that it contains healthy-looking lines.
- Treat empty-output exit-255 as "my command killed its own session" BEFORE blaming sshd.
