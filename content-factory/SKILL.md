---
name: content-factory
description: End-to-end content pipeline — idea in, published evidence-backed page out. Orchestrates search recon, real lab experiments (cloud VMs / local Docker), screenshot and asset production, drafting in a defined voice, verification loops, ship, and a write-back to your knowledge base. Triggers on "/content-factory ...", "new piece ...", "factory status", "resume <slug>", "refresh <slug>", "continue the <slug> piece", or any request to create a page that needs experiments, captures, or SERP recon.
version: 1.0.2
---

# Content Factory — Orchestrator

This skill runs a content pipeline where **the evidence is generated before the writing
starts**. The model is one component. The pipeline around it is what makes the output
worth publishing.

Read [SETUP.md](SETUP.md) once before the first run — the pipeline expects a handful of
files to exist and a few decisions to have been made.

| Module | File | What it covers |
|---|---|---|
| Lab (cloud VMs, local Docker) | [modules/lab.md](modules/lab.md) | Where experiments run and how they get torn down |
| Recon | [modules/recon.md](modules/recon.md) | What to learn about the topic before writing |
| Assets | [modules/assets.md](modules/assets.md) | Captures, clones, charts, social cards |
| Verification | [modules/verify.md](modules/verify.md) | Loops V0–V6, the release gate |
| Knowledge base | [modules/brain.md](modules/brain.md) | Reading your voice in, writing lessons back |
| Writer profile | [profiles/](profiles/) | How a draft becomes a page on YOUR site |

## The one rule that makes everything else work

**`content-lab/<slug>/PIECE.md` is the single source of truth for a piece.**

Update it after every meaningful step, not at session end. Any session must be able to
pick up any piece from PIECE.md alone: read `LEDGER.md` → read the piece's `PIECE.md` →
do what its `next_action` line says. Never rely on chat context surviving.

That rule is enforced rather than encouraged: `LEDGER.md` is *rendered from* the PIECE.md
files, so a piece whose frontmatter you let go stale disappears from the shared view. Only
one session may hold a piece, so PIECE.md has exactly one writer — which is why the ledger
can never be clobbered by a parallel session.

## Load this before any task

1. **[memory/MEMORY.md](memory/MEMORY.md)** — the skill's own memory index. Load it FIRST,
   before touching a piece, so past friction shapes what you do instead of being
   rediscovered at cost. Then open any `memory/<file>.md` whose description looks relevant.
2. Surface a one-line "Loaded N factory memories: …" so the owner knows what informed you.

A per-piece Decision log is scoped to THAT piece and dies with it. Anything that would
change how the NEXT piece runs belongs in `memory/` or in a `modules/*.md` rule — writing
it only into PIECE.md means nobody will ever read it again. **This is the part of the
system that compounds. Do not skip it.**

## Tasks

### Task: new-piece

**Trigger:** "/content-factory new <topic>", "new piece: <topic>", or the owner describes an idea
for a page that needs the pipeline.

0. `lock.py status`, then `lock.py claim <slug>` once the slug is agreed (step 1). Note
   the port it prints — that is your preview server for this piece.
1. Propose a slug (kebab-case, matches the final URL fragment). Confirm it.
2. Create `content-lab/<slug>/` with subdirs `recon/ scripts/ evidence/ evidence/raw/ assets/ assets/raw/ drafts/`.
3. Copy [templates/PIECE.md](templates/PIECE.md) → `content-lab/<slug>/PIECE.md`; fill the
   frontmatter; paste the owner's idea and thoughts into the Idea section **verbatim**.
   Their exact words carry intent that your summary of them will not.
4. Nothing to do for the LEDGER — it is generated. The row appears the moment PIECE.md
   exists and something syncs (`lock.py touch <slug>` will do it). Never hand-edit it.
5. Proceed to S1 unless told otherwise.

### Task: run-stages

Drive the piece through the lifecycle:

| Stage | Do | Gate |
|---|---|---|
| S1 Knowledge pull | Load the owner's voice, positions, and topic-relevant notes per [modules/brain.md](modules/brain.md). Log what you loaded in PIECE.md. | — |
| S2 Recon | Search-demand + competitor dissection + gap analysis per [modules/recon.md](modules/recon.md) → `recon/recon-report.md` ([template](templates/recon-report.md)). | — |
| S3 Plan | Thesis + differentiator + outline + [evidence manifest](templates/evidence-manifest.md) (experiments, infra, **cost estimate**) + asset manifest. | **CHECKPOINT 1: the owner approves plan + budget.** |
| S4 Lab run | Every experiment is a script in `scripts/`, output lands in `evidence/` (raw dumps in `evidence/raw/`). Failures are evidence too. Infra per [modules/lab.md](modules/lab.md). | — |
| S5 Assets | Captures, clones, charts, social card per [modules/assets.md](modules/assets.md). Finals in `assets/`, raw in `assets/raw/`. | — |
| S6 Draft | Write via the writer profile. Build `claims.md` **while writing** — every factual claim → an evidence file or a primary source. | — |
| S7 Verify | Loops V0–V6 per [modules/verify.md](modules/verify.md). Each loop: findings → fix → re-run until clean. Record in the PIECE.md verification table. | all green |
| S8 Ship | **Take `lock.py ship-claim` first, release it the moment the commit lands.** Publish per the writer profile's output contract, then run its render test. | **CHECKPOINT 2: the owner reads the rendered page.** |
| S9 Seed | Distill the *ledger* into candidate knowledge-base entries. Never auto-write. Prune `evidence/raw/` + `assets/raw/`. | the owner picks |

In **checkpoint mode** (the default): stop and wait ONLY at Checkpoint 1 and Checkpoint 2.
Everything between runs autonomously. In **interactive mode**: also confirm the outline and
the draft before moving on.

### Task: resume

**Trigger:** "resume <slug>", "continue the <slug> piece", "/content-factory resume <slug>".

0. `lock.py claim <slug>` FIRST. If it exits 1 the piece is live in another session: stop,
   say so, do not read-modify-write its files. Note the port it prints. (If it says
   `[reclaim]`, the previous session died — read its PIECE.md carefully before assuming
   the last step it recorded actually finished.)
1. Read `content-lab/LEDGER.md` for the cross-piece picture — which pieces are live, and
   whether yours shares lab infra with a sibling. It is a generated view; the lock you just
   took is the authority on who owns what.
2. Read `content-lab/<slug>/PIECE.md` fully.
3. Set `session_note` to what you are about to do; do what `next_action` says.
4. **Re-verify any recorded blocker before acting on it**, especially one whose only
   resolution is asking the owner. A previous session's "X does not exist, ask about it" is
   a claim, not a fact — it was written with whatever that session happened to search. Cost
   of checking: one query. Cost of not checking: a stalled pipeline and a question that
   never needed asking.

### Task: status

**Trigger:** "factory status", "/content-factory status".

1. `lab/lock.py status` FIRST — it regenerates the LEDGER as a side effect, so everything
   you read afterwards is current. Each lock reads MINE / LIVE / DEAD / STALE.
2. Read the regenerated `LEDGER.md` + each active piece's PIECE.md frontmatter. Report:
   slug, status, stage, next action, budget spent, lab resources, who holds it.
3. `lab/do.py sweep` — which VMs are still alive and billing, and which are GUARDED by
   another piece.

Report these as **findings, not details**: a **DEAD** lock (a session died mid-piece, so
its PIECE.md may overstate what actually finished), anything under the LEDGER's ⚠ headings
(shared infra, orphan locks, slug mismatches), and any VM alive that no piece claims.

### Task: refresh

**Trigger:** "refresh <slug>", "/content-factory refresh <slug>". Manual, monthly-ish.

1. Re-run the piece's `scripts/` against current infra (fresh VM if the manifest used one).
2. Diff new results against committed evidence; re-render clones.
3. Flag drifted claims and stale screenshots; propose edits; bump "Last verified" only
   after the owner approves.

## Parallel sessions

Several pieces can run at once in separate Claude Code sessions. **S1–S7 are fully
parallel. S8 is one-at-a-time, enforced by a lock.** You never have to reason about whether
another session is around: ask the tools.

```bash
L=.claude/skills/content-factory/lab/lock.py

python $L status                                   # who is live, what is free — ALWAYS first
python $L claim <slug> --stage S2 --note "recon"   # exits 1 if a LIVE session holds it
python $L touch <slug> --stage S4                  # heartbeat + stage update as you move
python $L release <slug>                           # when you stop, even mid-piece
```

**Claim is re-entrant.** Re-claiming a piece you already hold is a no-op that exits 0, so
claim again any time you are unsure — after a compaction, after a long gap, before a risky
write. It costs nothing and it is the cheapest way to be certain. If claim exits 1 it is
because a *provably live* session holds it: pick another piece or ask. Do not `--force`
past a LIVE lock.

The lock knows who you are: it records `CLAUDE_CODE_SESSION_ID` and the `claude` process
pid, both of which the harness exports into every shell. So a crashed session's lock is
reclaimed automatically (no `--force`, no six-hour wait), and a session that legitimately
works a piece for ten hours is never declared stale underneath itself.

### The two shared files you must NOT hand-edit

1. **`content-lab/LEDGER.md` is generated.** Every row is rendered from that piece's
   `PIECE.md` frontmatter plus the live locks. Editing it does nothing — the next sync
   overwrites you. To change what the ledger says, edit the `PIECE.md` you hold the lock
   for; `claim`/`touch`/`release` re-render it for you. This is what makes parallel work
   safe: **no session ever writes a file another session also writes.** Force a re-render
   with `python .claude/skills/content-factory/lab/ledger.py sync`.
2. **The git index.** See rule 5 below.

Keep these `PIECE.md` frontmatter fields honest — they are the ledger's only inputs:
`status`, `stage`, `updated`, `lab_resources` (everything alive for this piece, `""` when
idle), and at S9 `url`, `shipped`, `seeded`.

### Rules

1. **Claim before you touch a piece**, in `new-piece` and `resume` alike; `release` when
   you stop. Never write into a workspace you do not hold — not its `PIECE.md`, not its
   evidence. `lock.py check <slug>` exits 0 only if the lock is yours; use it as a guard
   when a piece has been idle in your context for a while.
2. **Use YOUR port.** `claim` prints one (8140–8199), nudged off any port a live piece
   already holds, so two pieces can never land on the same one. Two servers on one port
   means the second dies silently and you verify against the OTHER piece's pages. See
   [modules/verify.md](modules/verify.md) V0.
3. Before S8, work touches ONLY `content-lab/<slug>/` — zero shared files.
4. **S8 is serialized by a real lock:**
   ```bash
   python $L ship-claim      # blocks if another piece is mid-ship
   #   ... the shared registry, shared templates, static assets, the commit ...
   python $L ship-release    # the moment the commit lands
   ```
   `ship-claim` also warns if the git index is already dirty — that is another session's
   staged work, and a bare `git commit` would swallow it.
5. **Git is global — treat it as a shared resource.** `git commit` with no paths commits
   the WHOLE index, so another session's staged files land in your commit and nobody
   notices. Never bare `git commit` when the index may hold foreign work; always name
   paths. Never `git add -A`. Hold the SHIP lock while staging and committing, even for a
   small fix. The same lock covers any shared `MEMORY.md` index you append a line to.
   (But see `memory/lesson_path_scoped_commit_ignores_the_index.md` — hunk-scoping the
   index and path-scoping the commit at the same time silently does the wrong thing.)
6. **Lab isolation.** VMs are per-piece (`cf-<slug>`); shared infra is namespaced
   `cf-<slug>`. `do.py destroy` and `sweep --kill` refuse to touch a VM that another live
   session holds, or that another piece names in its `lab_resources` — so record borrowed
   boxes there, in both pieces. A guarded sweep says what it skipped instead of reporting
   "clean".
7. Benchmarks needing clean numbers always get their own VM.
8. **If a file changes underneath you** (an edit tool says it moved on disk, or content you
   did not write appears), STOP, re-verify your own edits survived, and say so. A lock
   makes that unlikely, not impossible — a session that skipped the protocol still exists.

## Hard rules

- Never skip a checkpoint in checkpoint mode. Never publish live without Checkpoint 2.
- Every experiment is a committed script — no unscripted evidence.
- No orphan claims: if it is not in `claims.md` → evidence file or primary source, it does
  not ship.
- Costs: estimate in the manifest before running; log actuals in the PIECE.md Cost log; if
  a run will exceed the approved estimate by >50%, stop and ask.
- Knowledge base: read anytime; write ONLY at S9 with explicit approval, entry by entry.
- Voice: the knowledge base's voice file is canonical; the writer profile adds site deltas
  only.
- Lab teardown is part of the stage, not optional cleanup. `do.py sweep` must come back
  empty at the end of S4 — except for VMs it reports as GUARDED (another piece is using
  them) or that your own `lab_resources` documents as deliberately alive. Never
  `sweep --kill --force` to make the output look clean: that is how you delete the box
  another session is mid-experiment on.
- Secrets live in the repo-root `.env` (gitignored) — never in `content-lab/`, never in
  PIECE.md, never in an evidence file you commit.
- **Ship commits are hunk-scoped, not just path-scoped**, whenever a file you touched was
  ALREADY dirty. Run `git diff <file>` on every shared file first and stage only your
  hunks. After committing, verify the COMMITTED tree is self-consistent
  (`git show HEAD:<file>`), not just the working tree you tested.
- Skill feedback goes to `memory/` in this skill. Project-wide facts go wherever your setup
  keeps them.

## When NOT to use this skill

- Polishing an existing page with no new evidence → a normal edit.
- A quick copy change, template fix, or config tweak → a normal edit.
- Anything with its own dedicated skill → that skill.

The factory is expensive by design: it exists for pieces where **first-hand evidence is the
whole point**. Using it for a page that does not need evidence just adds ceremony.
