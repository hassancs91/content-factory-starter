---
name: lesson_no_shared_mutable_files
description: Parallel sessions are safe only when no two sessions write the same file — the fix for a shared file is to generate it, not to lock it.
---

# Parallel sessions: delete the shared file, don't guard it

The factory had a lock (`lab/lock.py`) and it worked — pieces could not be double-claimed.
It still was not safe to run two pieces at once, because the lock protected the *pieces* and
the pipeline had a shared mutable file the lock said nothing about: `content-lab/LEDGER.md`.
Every session read-modify-wrote that one markdown table (add a row at S0, set resources at
S4, flip SHIPPING at S8, move to Archive at S9). Two sessions doing that lose each other's
edits, and no lock over pieces can prevent it.

**The fix was to remove the shared write, not to add a second lock.** `LEDGER.md` is now
*generated* by `lab/ledger.py` from each piece's `PIECE.md` frontmatter plus the live locks,
written with an atomic replace. Every session writes only the PIECE.md it holds the lock
for. Concurrent syncs render identical bytes from identical inputs, so whoever lands last
lands the same content — convergence instead of contention. Verified with 8 simultaneous
processes and a 12-thread race.

This is the general rule for the pipeline: **when two sessions need to write the same file,
make that file derived.** A lock around a shared file only narrows the window; deriving it
closes it. Corollary — the ledger's "who is working this" column can no longer lie, because
it is read from the lock files rather than typed by a session. On the Plausible pilot a
second session worked the piece for hours while that column read `idle`.

## What else turned out to be shared

Auditing for "two sessions, one file" found three more, all now fixed in code rather than
in prose:

- **`do.py sweep --kill` destroyed every `cf-*` droplet**, including the box another
  session was mid-experiment on — and the S4 hard rule ("sweep must come back empty") reads
  as an instruction to do exactly that. Destroy and sweep now refuse any droplet a live
  session holds or that another piece names in `lab_resources`, and a guarded sweep reports
  what it skipped instead of claiming "clean".
- **One shared `known_hosts`**: ssh appends to it under `StrictHostKeyChecking=accept-new`,
  so two simultaneous connections can interleave and corrupt an entry — which then surfaces
  as a host-key failure that reads like an attack. Now per piece.
- **Dev-server ports collided** by birthday chance (crc32 over a 60-port span). A collision
  is silent and vicious: the second runserver dies and you verify the other piece's pages.
  Ports are now nudged off any port a live piece holds.

## Session identity: the harness already exports it

The old lock recorded `os.getpid()` — the pid of the `lock.py` process itself, dead
milliseconds later. So it proved nothing, and liveness fell back to a 6-hour heartbeat that
nobody remembered to refresh. That fails in both directions: a crashed session squats a
piece for six hours, and a session legitimately working for ten hours gets declared STALE
and force-taken.

Claude Code exports `CLAUDE_CODE_SESSION_ID` and `CLAUDE_PID` (the long-lived `claude.exe`)
into **every** shell, and unlike shell variables they survive across tool calls. Locks record
both. That buys real liveness (a dead owner is reclaimed on sight, no `--force`, no waiting)
and re-entrancy: re-claiming a piece you already hold is a no-op that exits 0. Re-entrancy
matters more than it sounds — without it a session blocks on its *own* lock after a
compaction, and the only way out it can see is `--force`, which teaches exactly the wrong
reflex.

## Method note

The bug that mattered most was found by the test, not by review: 12 concurrent syncs in one
process all built the temp file as `.LEDGER.<pid>.tmp`, so the second `os.replace` failed
with "file not found" — the first had already moved it. A pid is not a unique token when the
racers can share one. `tempfile.mkstemp` is. Windows also fails `os.replace` with
ERROR_ACCESS_DENIED whenever anything else holds the destination open, which happened on the
very first two-session run, so the retry loop is the common path rather than paranoia.
