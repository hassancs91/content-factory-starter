# Evidence + Asset Manifest — <slug>

Approved at Checkpoint 1: YYYY-MM-DD · Approved budget: $X

This is what the owner is actually approving at Checkpoint 1: a set of experiments, a
duration, and a number. Write it so a "yes" means something specific.

## Experiments

Every experiment becomes a script in `scripts/` and lands its output in `evidence/`.
**Failures are evidence too — keep them.** The experiment that broke something and the fix
that unbroke it is usually the most valuable thing the piece will publish.

| ID | Question it answers | Infra | Script (planned path) | Est cost | Est time | Status |
|---|---|---|---|---|---|---|
| E1 | | cf-<slug> VM | scripts/e1_<name>.sh | $ | | planned |

Write each question as something that can come back **no**. "Measure the RAM of each
container" is a task; "does the full stack fit in 4 GB?" is an experiment, and its answer
is publishable either way.

Time-boxed experiments (soak tests, exposure windows, anything with a wait) are written as
**"≥N hours, report the actual window"**, with N the smallest span that makes the point.
A fixed "leave it 24h" turns into a pipeline blocker with a VM billing the whole time.

## Infra plan

- VMs: <count × size × estimated hours alive> — create via `do.py create <slug>`, destroy
  in the same stage
- Shared infra: <projects to create, namespaced cf-<slug>-*>
- Local: <Docker compose project cf-<slug>>
- API spend: <provider: estimated calls → $>

**Say which line item is the wall-clock driver.** Cost tracks how long a box stays alive,
not how many experiments run on it, so the owner is approving a *duration* — make it
visible rather than folding it into a total.

## Teardown checklist

- [ ] `do.py destroy <slug>` + `do.py sweep` clean (or GUARDED-only)
- [ ] `dns.py sweep` clean
- [ ] Shared-infra projects `cf-<slug>-*` deleted
- [ ] Local compose project down, volumes removed
- [ ] PIECE.md `lab_resources` cleared — that is what the LEDGER renders

## Assets

| ID | Type (capture/clone/chart/social) | Shows | Source (screen or clone file) | Status |
|---|---|---|---|---|
| A1 | capture | | | planned |
| A2 | social | share card | | planned |

For each capture, name the **claim it supports**. An asset that illustrates nothing is
decoration, and decoration can be added later; an asset that proves something has to be
shot while the lab is still alive. Once the box is destroyed, that screenshot can never be
taken again.
