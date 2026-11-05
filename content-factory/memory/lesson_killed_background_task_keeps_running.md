---
name: lesson_killed_background_task_keeps_running
description: When the harness kills a background Bash task, only the wrapper dies; the script runs on, and its EXIT trap can write into the log of the run you started next.
---

# A killed background task leaves its script running

**What happened (self-host-uptime-kuma, 2026-10-21, Windows + Git Bash):** the boot probe
ran as a background Bash task while a 602 MB image pulled. The task reached the harness's
background time limit and came back `killed`. Only its wrapper died. The bash script kept
running, finished its steps, and its `trap cleanup EXIT` fired about three minutes later,
writing into the same log file that a fresh re-run had just truncated. The log came out
with NUL bytes and two runs' lines interleaved.

It looks like a corrupt log or a flaky container. It is two copies of one script sharing
one file. And because the trap removes the container by its fixed name, the old copy can
just as easily tear down the new run's container.

**Rule:**
- A `killed` task is not a stopped script. Before re-running it, look for the orphan:
  `docker ps` for its container, and in PowerShell
  `Get-CimInstance Win32_Process | Where-Object CommandLine -like '*<script name>*'` for the
  script. Git Bash's own `ps` shows no arguments, so it cannot find it.
- That query also matches every wrapper shell whose command line mentions the script (the
  harness's `bash -c "..."`, even the query itself). The orphan is the one that reads
  `bash.exe <path to the script>`. Stop it by its PID, never by a pattern.
- Give every run its own log path (a timestamp in the name), so two runs can never write
  one file.
- Do the slow one-off step (an image pull) on its own first, so the timed run is not the
  one the time limit kills.

Related: [[lesson_pkill_matches_the_remote_wrapper]] (the same wrapper-versus-script split,
on a remote box).
