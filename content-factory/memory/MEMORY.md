# Content Factory — Skill Memory Index

**Load this file before any factory task.** Then open any lesson whose one-liner looks
relevant to what you are about to do.

These are real lessons from real runs, each one written the day something cost a re-run, a
stage, or a wrong claim that nearly shipped. They are here because **the memory folder is
the part of this system that compounds.** Everything else is a pipeline; this is the part
that gets better.

Add your own the same way: one file per lesson, terse index line here, written the moment
it bites — not later, when you have already half-forgotten what actually happened.

Format: `- [Title](file.md) — one-line hook`

## Running experiments

- [Upload scripts, never pipe them](lesson_bash_s_stdin_trap.md) — `bash -s < script` dies silently at exit 0 the moment any line reads stdin (`docker exec -T`, `psql`, `ssh`); `cat > /root/x.sh` then run it, and treat an evidence file that ends early as this bug first.
- [Four traps in scripts piped over SSH](lesson_remote_script_traps.md) — `docker exec -i` eats the rest of the script; `curl|grep -q` SIGPIPEs on a MATCH under pipefail; tar exit 1 is a warning that IS the evidence; a golden image needs `apt-get update` before any install.
- [pipefail eats `| head`, and sentinels must encode exit status](lesson_evidence_scripts_pipefail_and_sentinels.md) — grep detached scripts for `| head` before launch; use `.done`/`.fail` sentinel pairs (`; touch done` fires on failure too); verify a daemon by its output file GROWING, never by pgrep.
- [Experiments that break their own transport](lesson_experiments_that_break_their_transport.md) — run detached with a sentinel (never pipe over the connection they sever), assert healthy BEFORE each break, run reverting experiments before the terminal-state script, verify the terminal state from outside the box.
- [Never edit a driver script while an instance is running](lesson_never_edit_running_driver.md) — bash reads scripts by byte offset mid-run, so an edit kills every live instance with phantom syntax errors minutes later.
- [pkill -f matches the remote wrapper shell](lesson_pkill_matches_the_remote_wrapper.md) — anchored patterns only (`^python3 /root/probe`); an empty exit-255 from ssh means you killed your own session; liveness checks must assert log growth.
- [Assert on what the user would see](lesson_assert_on_what_the_user_sees.md) — a websocket opening, a 200, "the container is running" all pass on a broken feature; assert on the rendered string, and print the options before selecting one.

## Planning and cost

- [Lab cost is wall-clock, not experiment count](lesson_lab_cost_is_wallclock_not_experiments.md) — 11 experiments cost $0.04 against a $1.20 estimate; estimate how long the box stays ALIVE. Also: `apt install iptables-persistent` silently removes ufw on Ubuntu 24.04.
- [Time-boxed experiments: state the window, don't fix it](lesson_timeboxed_experiments.md) — write manifests as "≥N hours, report the actual window" so a 24h gate can't block the pipeline; start clock-gated work as early as possible.
- [Probe for a differentiator before you spend recon](lesson_probe_differentiator_before_recon.md) — when a cheap factual probe can test whether the piece is more than the commodity take, run it before S2; it flips recon from "hunt for an angle" to "size the one we proved".
- [GPU lab: image, regions, and placement asserts](lesson_gpu_droplet_lab.md) — run a cheap boot probe before planning a GPU piece; a GPU benchmark must assert the model actually landed on the GPU (silent partial offload runs 3–4× slow while every request "succeeds"); price claims come from the vendor's own page, never an aggregator.

## Captures and assets

- [Lazy images render blank in full-page captures](lesson_lazy_images_blank_in_fullpage_captures.md) — Playwright's `full_page=True` never scrolls, so `loading="lazy"` images shoot as empty boxes; pre-scroll first, and curl the asset URL before suspecting paths.
- [Long pages: viewport stops, not --full](lesson_v6_capture_long_pages.md) — `--full` silently returns a repeated tile past Chromium's ~16k px surface limit; shoot viewport stops instead, and clear debug toolbars, cookie banners and popups out of the frame first.
- [Measure staleness before re-shooting](lesson_measure_before_you_reshoot.md) — 7 of 10 shipped screenshots were pixel-identical, so "refresh the screenshots" would have churned a live product for nothing; the one that looked stale was a capture bug (a first-run screen needs a first-run account).

## Parallel sessions and shipping

- [Delete the shared file, don't guard it](lesson_no_shared_mutable_files.md) — the LEDGER is GENERATED from PIECE.md frontmatter plus live locks, so no two sessions ever write one file; locks carry real session identity, which buys honest liveness and re-entrant claims.
- [`git commit -- <paths>` ignores the index](lesson_path_scoped_commit_ignores_the_index.md) — pathspecs make git commit take the WORKING TREE, silently discarding hunk-scoped staging; hunk-scope the index OR path-scope the commit, never both, and verify `git show HEAD:<file>` afterwards.

## Environment

- [Five Windows harness traps](lesson_windows_experiment_harness.md) — an em dash in a UTF-8-no-BOM `.ps1` breaks the parser 70 lines away; `2>&1` on a native exe is a terminating error; harness-reaped shells kill background servers; git-bash `sed -i` turns uploaded scripts CRLF.
