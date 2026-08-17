# Evidence scripts: pipefail eats `| head`, and sentinels must encode exit status

On the self-host-gitlab E1 install script (2026-08-11), three consecutive silent
failures before a single package was installed:

1. `apt-cache madison gitlab-ce | head -60` under `set -euo pipefail`: `head` exits
   after 60 lines, the producer gets SIGPIPE (exit 141), pipefail kills the whole
   script. **Any `producer | head/-c` in a `set -o pipefail` script is a landmine.**
   Write the producer to a file first, or use `awk 'NR<=60'` / `openssl rand` style
   commands that terminate on their own.
2. The SAME trap struck twice in one script (`tr </dev/urandom | head -c 24` for a
   password). After fixing one `| head`, grep the script for the rest: `grep -n '| *head' script.sh`.
3. The detached-run sentinel was `bash script.sh > log; touch done` — `;` means the
   sentinel fires on FAILURE too, so the poller reported success on a dead install.
   Pattern that works: `if bash script.sh > log 2>&1; then touch .done; else touch .fail; fi`
   and poll for THREE states (done/fail/running). This composes with the existing
   lesson_experiments_that_break_their_own_transport (detached + sentinel): the
   sentinel must carry exit status, not just existence.

Bonus on fresh DO boxes: the first minutes after boot, `unattended-upgrades` holds the
dpkg lock and any apt evidence script fails. Benchmark boxes should
`systemctl stop && disable unattended-upgrades` FIRST (surprise apt activity mid-run
also pollutes measurements), then `fuser` wait on `/var/lib/dpkg/lock-frontend`.

Fourth trap, same piece, one hour later: the sampler-daemon start guard
`pgrep -f sampler.sh || (nohup bash sampler.sh &)` NEVER started the daemon — over
`do.py run` the whole command travels as one `bash -c` string, so `pgrep -f` matches
its own wrapper's cmdline, the guard "finds" the daemon, and the verify pgrep matches
itself again. 35 minutes of "measurements" had no measuring process. **Verify a daemon
by its OUTPUT FILE growing (`wc -l` twice, N seconds apart), never by pgrep; guard
restarts with a pid-file, not a name match** (or self-proof the pattern: `pgrep -f '[s]ampler.sh'`).

**Why:** evidence scripts run detached where stderr goes nowhere; a pipefail SIGPIPE
death is indistinguishable from success unless the sentinel says otherwise.
**How to apply:** before launching any detached evidence script: (a) grep it for
`| head`, (b) use the if/then done-fail sentinel pair, (c) on fresh boxes neutralize
unattended-upgrades before the first apt call.
