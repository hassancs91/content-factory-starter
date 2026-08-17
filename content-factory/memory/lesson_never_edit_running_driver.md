# Never edit a driver script while an instance is running

**What happened (self-host-ollama, 2026-08-12):** two long-running local driver
processes (background Bash running `drive_box.sh` poll loops) died with phantom
`syntax error near unexpected token` failures minutes after I edited that same
file to add a RESUME mode. Bash reads script files incrementally by byte offset:
after the currently-parsed compound command ends, it seeks into the EDITED file
at a stale offset and parses garbage. The on-box chains survived (they run
uploaded copies, detached), but both drivers lost their poll/fetch/destroy tails.

**Why:** a shell script is not loaded into memory at launch. Any process
mid-execution of a file shares those bytes with your editor.

**How to apply:**
- Before editing any `scripts/*.sh` that a live process may be executing, check
  the background task list. If one is running: write a NEW file (copy to
  scratch, edit the copy) or wait.
- Keep a fetch-only recovery script (`fetch_box.sh`: poll sentinels → pull
  evidence → optional destroy) so a dead driver never strands on-box results.
- Sentinel pairs on-box (`all.done`/`all.fail` via ERR trap) are what make this
  recoverable — the experiment's truth lives on the box, not in the driver.
