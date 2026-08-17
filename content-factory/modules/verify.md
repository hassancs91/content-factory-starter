# Verification module (S7) — loops V0–V6

Each loop: run → findings → fix → **re-run that loop** until clean. Record every round in
the PIECE.md verification table. All green = the release gate opens for S8.

Do them in order: V0 first (so you are testing what you think you are), then V1/V2 (facts),
then V3–V5 (form), then V6 (eyes).

**This is the stage that separates the factory from a prompt.** Everything before it makes
the draft good. This makes it trustworthy. Do not compress it because the draft reads well
— a draft reading well is exactly the condition under which a wrong claim survives.

## V0 — pre-flight (before ANY loop that renders a page)

A verification sheet built against a stale server is worse than no sheet: it is confident
and wrong. Both of these have burned real sessions.

0. **Use your own port.** `lock.py claim <slug>` prints it; `lock.py port <slug>` reprints
   it. Two sessions sharing a port is the nastiest version of the bug below — the second
   server dies silently and you verify the OTHER piece's page while believing it is yours.
   ```bash
   python .claude/skills/content-factory/lab/lock.py port <slug>
   ```
1. **Confirm the process on that port started AFTER your edits.** Most dev servers with
   auto-reload disabled never re-read templates, and a leftover server from an earlier
   session happily keeps serving pre-edit HTML while your new one fails to bind and exits
   without saying so.
   ```bash
   netstat -ano | grep <your-port>      # who owns it
   ```
   If its start time predates your edits, kill it and start your own. Re-run this check
   after **any** template edit made later in the session, including edits to a shared base
   template.
2. **Clear the right cache.** Sites usually have more than one. Clearing the wrong one
   changes nothing and looks exactly like clearing the right one.
3. **Prove one edit is live** before trusting anything else: fetch the page and grep for a
   string you just added. It costs one command and it collapses the entire class of "why is
   my fix not working" detours.

## V1 — Evidence

- Re-run or independently cross-check every key number in `evidence/`.
- Benchmarks and timings: n≥3 runs on a dedicated box; report median and spread in the
  piece, never a single run.
- **Adversarial pass.** For each result, actively try to refute it: would this replicate on
  a clean box? Does the number depend on cache warmth, region, or version? Write the
  refutation attempt *and its outcome* into `evidence/` — a failed refutation is part of the
  ledger and is the strongest thing you can cite.

## V2 — Claims

- `claims.md` maps EVERY factual claim — version, price, timing, capability, security
  statement — to an `evidence/` file or a primary-source URL that you **fetched**, not
  remembered.
- Zero orphan claims. Zero orphan evidence that contradicts the draft.
- Prices and versions re-checked against the live source **on the verification day**. That
  is what makes a "Last verified" line honest rather than decorative.

## V3 — Technical

```bash
python .claude/skills/content-factory/lab/lint_draft.py <draft-or-template>
```

Plus your writer profile's render test: the page returns 200, every planned schema type is
present, TOC anchors resolve to real `id`s, internal links resolve, and every image exists
on disk with width and height set.

## V4 — Voice

- Canonical voice: your knowledge base's voice file. The writer profile adds site deltas
  only; on conflict the knowledge base wins.
- **The anti-generic test, per paragraph: could a competitor publish this word for word?**
  If yes, fix it with a specific number, a real screenshot, a mistake you hit, or a
  trade-off you can defend — or cut it. This one test does more for the output than every
  other style rule combined.
- `lint_draft.py` catches the mechanical tells. This loop is the judgment part, and it does
  not delegate to the linter.

## V5 — Search and answer engines (against the recon report, not against taste)

- Every gap the plan promised to exploit is actually covered.
- Meta title ≤60 chars, description ≤155; the primary term in the title, the H1, and the
  first screen.
- The query is answered in the first screen. Question-shaped H2s where recon said so.
- Emitted schema matches the recon plan.
- Internal links: the inbound candidates and outbound links recon identified.

## V6 — Visual

```bash
CAP=.claude/skills/content-factory/lab/capture.py
python $CAP --url http://127.0.0.1:<port>/<path>/ --out assets/raw/v6-desktop.png --full
python $CAP --url http://127.0.0.1:<port>/<path>/ --out assets/raw/v6-mobile.png --width 390 --height 844 --dpr 3 --full
```

Inspect every frame for broken layouts, image sizing, code blocks overflowing their
container, and contrast. On a long page use viewport stops rather than `--full` — past
roughly 16,000 px Chromium's full-page capture silently returns a repeated tile, and you
will review an image that is not the page. Clean debug toolbars, cookie banners, and popups
out of the frame first, or the shots are useless as review artifacts.

These shots are what you present at Checkpoint 2.

## The step that is not a loop

Read the whole thing. Every word, every command, every number, before it goes live.

The pipeline exists to make that read *cheap and worth doing* — by the time the piece
reaches you, its claims already have receipts. It does not exist to replace the read.
**Automate the work. Never automate the responsibility.**
