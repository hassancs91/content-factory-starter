---
name: lesson_remote_script_traps
description: Four traps in experiment scripts piped over SSH — docker exec -i eats the rest of the script, curl|grep -q SIGPIPEs under pipefail, tar exit 1 is a warning not a failure, and the golden image needs apt-get update first.
type: lesson
---

# Four traps in scripts piped over SSH (docker-backups, 2026-08-11)

All four fired in ONE piece's S4, each costing a re-run. They generalize to every
`do.py run <slug> -- 'bash -s' < script` experiment.

**1. `docker exec -i` swallows the rest of your script.** The script arrives on
stdin; any command that reads stdin (`docker exec -i`, `ssh`, `mariadb` without a
redirect) consumes the remaining script text as its input. The script "succeeds"
but silently stops at that line — exit 0, half the evidence missing. Use `-i` ONLY
with an explicit `< file` redirect; define query helpers without it
(`docker exec c mariadb -e "..."`).

**2. `curl -s url | grep -q pattern` fails on a MATCH under `set -o pipefail`.**
grep -q exits on first match and closes the pipe; curl takes SIGPIPE → exit 23 →
the pipeline is "failed" precisely when the assertion should pass. Capture first:
`OUT=$(curl -s url || true); echo "$OUT" | grep -q pattern`.

**3. tar exit code 1 means "file changed as we read it" — a warning, and under
`set -e` it kills the script.** When taring live data IS the experiment, that
warning is the evidence. Tolerate and record it:
`TAR_EXIT=0; tar czf ... 2>warn.txt || TAR_EXIT=$?; echo "TAR_EXIT=$TAR_EXIT"`.

**4. The golden image ships stale apt lists and no bzip2.** Any
`apt-get install` in an experiment script needs `apt-get update -qq` first, or it
dies with "has no installation candidate". (restic's release binary is .bz2 —
bzip2 is not preinstalled.)

Corollary to #1 that already burned the Coolify piece differently: a background
writer loop `( while ...; do docker exec ...; done ) &` must have its stdio
redirected `>/dev/null 2>&1` AND a `trap 'touch /tmp/stopfile' EXIT` — otherwise
a dying script orphans the loop, and its open stdout keeps the whole SSH session
(and your harness command) hanging forever.
