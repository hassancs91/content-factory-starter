---
slug: REPLACE-slug
title: "REPLACE working title"
status: Planned            # Planned | Recon | Drafting | In Review | Shipped | Seeded
stage: S0                  # current stage S0–S9
mode: checkpoint           # interactive | checkpoint
profile: ""                # which profiles/<name>.md this piece ships through
target_keywords: []
budget_est: "$0"
budget_spent: "$0"
opened: YYYY-MM-DD
updated: YYYY-MM-DD
lab_resources: ""          # everything ALIVE for this piece (VMs, DNS records, projects).
                           # Name any box you BORROW from another piece too — do.py reads
                           # this to refuse a destroy that would delete a sibling's
                           # evidence. MUST be "" when the piece is idle.
url: ""                    # S8: the live URL
shipped: ""                # S8: date + commit shas
seeded: ""                 # S9: date + knowledge-base commit
session_note: ""           # one line: what the active session is doing right now
next_action: "S0: capture the idea, create the workspace"
---

<!-- This frontmatter IS the LEDGER. content-lab/LEDGER.md is generated from these fields
     across all pieces, so keep status/stage/updated/lab_resources honest, and never
     hand-edit the LEDGER itself. -->


# REPLACE title — piece file

> Resume protocol: read this file top to bottom, then do `next_action`. Update the
> frontmatter and the relevant log section after every meaningful step — not at session
> end. A session that dies mid-stage leaves nothing behind except this file.

## Idea (the owner's words, verbatim)

_(paste at S0 — their exact words, not your summary of them)_

## Stage checklist

### S0 Intake
- [ ] `lock.py claim <slug>` taken; port noted
- [ ] Slug confirmed
- [ ] Workspace dirs created (recon/ scripts/ evidence/ evidence/raw/ assets/ assets/raw/ drafts/)

### S1 Knowledge pull
- [ ] Knowledge-base index read; `identity/` loaded
- [ ] Topic-relevant entries loaded (list below under Knowledge context)

### S2 Recon
- [ ] Search demand pulled + cross-checked
- [ ] Top-15 SERP fetched and dissected
- [ ] Answer-engine analysis
- [ ] Gap analysis + differentiator candidates
- [ ] `recon/recon-report.md` written

### S3 Editorial plan  →  CHECKPOINT 1
- [ ] Thesis + differentiator + will-NOT-do scope guard
- [ ] Outline (H2s + components)
- [ ] Evidence manifest (experiments, infra, scripts planned, cost estimate)
- [ ] Asset manifest (every capture/clone/chart/social card planned)
- [ ] **Checkpoint 1 approved** (record below, with the approved budget)

### S4 Lab run
- [ ] Infra provisioned per manifest; `lab_resources` frontmatter updated
- [ ] All experiments executed as scripts in `scripts/`
- [ ] Evidence captured to `evidence/` (raw → `evidence/raw/`)
- [ ] Teardown done — `do.py sweep` clean or GUARDED-only; `lab_resources` back to ""

### S5 Assets
- [ ] Real captures per spec
- [ ] Clones built and rendered
- [ ] Charts + social card
- [ ] Finals in `assets/`, sources preserved

### S6 Draft
- [ ] Full draft in `drafts/`, citing evidence
- [ ] `claims.md` complete — zero orphan claims

### S7 Verification (loop each until clean)
- [ ] V0 Pre-flight (right port, fresh server, right cache, one edit proven live)
- [ ] V1 Evidence cross-check + adversarial pass
- [ ] V2 Claims map verified
- [ ] V3 Technical (lint, render, schema, links)
- [ ] V4 Voice (canonical voice + anti-generic)
- [ ] V5 Search/answer-engine vs the recon report
- [ ] V6 Visual (desktop + mobile)

### S8 Ship  →  CHECKPOINT 2
- [ ] `lock.py ship-claim` taken
- [ ] Page + registry + assets shipped; reverse links proposed/applied
- [ ] Render test green
- [ ] Commit hunk-scoped if any shared file was dirty; `ship-release` the moment it lands
- [ ] `url` + `shipped` frontmatter filled
- [ ] **Checkpoint 2: the owner read the rendered page** (record below)

### S9 Knowledge seed
- [ ] Ledger distilled → candidate entries presented
- [ ] Approved entries written + indexed
- [ ] `evidence/raw/` + `assets/raw/` pruned (after asking); `seeded` filled; `status: Seeded`
- [ ] `lock.py release <slug>`

## Knowledge context loaded (S1)

_(entry names + why each is relevant)_

## Recon summary (S2)

_(5 lines max; the full report is in `recon/recon-report.md`)_

## Editorial plan (S3)

**Thesis:**

**Differentiator:** _(what this piece will have that no ranking page has)_

**Will NOT do:** _(the scope guard — what this piece deliberately leaves out)_

**Outline:**

**Evidence manifest:** see `evidence-manifest.md` in this folder
**Asset manifest:** see `evidence-manifest.md` §Assets

## Checkpoint 1 record

_(date, what changed, the approved budget)_

## Lab run log (S4)

_(per experiment: script, infra, started/finished, where the evidence landed, surprises.
The surprises are the valuable column — they are usually what the piece ends up being about.)_

## Asset log (S5)

## Draft log (S6)

## Verification log (S7)

| Loop | Round | Findings | Fixed | Status |
|---|---|---|---|---|

## Ship record (S8)

## Checkpoint 2 record

## Seed record (S9)

_(what entered the knowledge base, what was rejected and why)_

## Decision log

_(dated one-liners: anything decided mid-flight that a future session must know.
Anything that should change how the NEXT piece runs does NOT belong here — it belongs in
the skill's memory/ folder, because nothing reads this file except this piece.)_

## Cost log

| Date | Item | Est | Actual |
|---|---|---|---|
