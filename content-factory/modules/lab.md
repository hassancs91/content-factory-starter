# Lab module (S4) — infra catalog + rules

All experiment infrastructure for a piece. Secrets live in the project-root `.env`.

**The lab is the block people assume is expensive. It is the cheapest one.** A cloud VM
billed by the hour, created for one piece and destroyed when the stage ends, costs cents.
The reason to build it is not speed — it is that first-hand evidence stops being something
you can only afford occasionally.

## Infra catalog

| Infra | When | Access | Isolation |
|---|---|---|---|
| **Cloud VM** (default) | Anything needing a fresh box, a public IP, a real domain and TLS, or clean benchmark numbers | `lab/do.py` (DigitalOcean, `DO_TOKEN`) | Per-piece by construction: named `cf-<slug>`, destroyed after the run |
| **A shared panel / control plane** | UI captures and walkthroughs of a tool you self-host | your own instance, credentials in `.env` | Namespace every resource `cf-<slug>-*`; delete at teardown |
| **Local Docker** | Heavy experiments, no-public-IP needs, anything long-running | local machine | Compose project `cf-<slug>`; `docker compose -p cf-<slug> down -v` at teardown |
| **Not a server at all** | Most non-tech niches | whatever your niche tests truth with | See [../docs/ADAPT.md](../docs/ADAPT.md) |

`do.py` speaks the DigitalOcean API. To use another provider, swap that one file — every
other part of the pipeline only asks it for "a box named `cf-<slug>`, and destroy it later".

## do.py — VM lifecycle

```bash
DO=.claude/skills/content-factory/lab/do.py

python $DO ssh-key                      # one-time: create the lab key + register it
python $DO golden                       # build a golden snapshot cf-golden-YYYYMMDD (~10 min)
python $DO create <slug>                # boot cf-<slug> from newest golden
python $DO create <slug> --size s-4vcpu-8gb --image ubuntu-24-04-x64   # overrides
python $DO ip <slug>                    # print public IP
python $DO run <slug> -- <command>      # run a command on the box over SSH
python $DO ssh-cmd <slug>               # print the ssh command for manual use
python $DO snapshot <slug> <name>       # power off + snapshot
python $DO destroy <slug>               # destroy cf-<slug> (refuses if another piece claims it)
python $DO sweep                        # list ALL cf-* boxes, flagging GUARDED ones
python $DO sweep --kill                 # destroy the unguarded ones, report what was skipped
python $DO list                         # boxes + snapshots overview
```

**Destroying is guarded.** `destroy` and `sweep --kill` refuse any box that a live session
holds the lock for, or that another piece names in its PIECE.md `lab_resources`. That is
deliberate friction: teardown runs at the end of every S4, and without the guard the
"sweep must come back empty" rule reads as "delete the box the other session is using".
`--force` overrides — reach for it only when you have checked the other piece yourself.

Typical timings from a golden snapshot: boot → SSH-ready in well under a minute, golden
rebuild a few minutes, destroy ~10s.

## dns.py — real subdomains for lab-hosted apps

A lot of experiments are only honest with a real hostname: TLS issuance, OAuth callbacks,
webhooks, anything where the URL bar is part of the screenshot.

```bash
D=.claude/skills/content-factory/lab/dns.py
python $D set plausible $(python $DO ip plausible)
python $D rm plausible          # teardown
python $D sweep [--kill]        # everything under the lab zone
```

Set `CF_LAB_DNS_ZONE` (e.g. `lab.example.com`) and `CLOUDFLARE_LAB_DNS_TOKEN`. Records are
created unproxied with a short TTL, which is what lets the box issue its own certificates.

Teardown rule extends: end of S4 = `do.py sweep` clean AND `dns.py sweep` clean.

SSH: the lab key (default `~/.ssh/cf_lab`), user `root`, known-hosts isolated **per piece**
at `content-lab/.ssh_known_hosts.d/<slug>.known_hosts` — one shared file lets two sessions
append at the same instant and corrupt an entry, which then reads like a host-key attack.

Experiment scripts run ON the box but LIVE in the workspace. Upload, then execute — never
pipe (`memory/lesson_bash_s_stdin_trap.md` explains why a piped script silently dies at the
first command that reads stdin):

```bash
python $DO run <slug> -- 'cat > /root/e1.sh' < content-lab/<slug>/scripts/e1.sh
python $DO run <slug> -- 'bash /root/e1.sh' > content-lab/<slug>/evidence/e1.out 2>&1
```

## Rules

1. **Size cap.** Default to the smallest box that can run the experiment. Anything bigger
   must be justified in the evidence manifest the owner approved.
2. **Region.** Keep one default so snapshots stay usable — a snapshot only boots in its own
   region.
3. **Teardown is part of the stage.** End of S4 = `destroy` + `sweep` clean, and PIECE.md
   `lab_resources` back to `""`. A box alive overnight needs a documented reason in
   `lab_resources`. If you borrow another piece's box, name it in YOUR `lab_resources` too
   — that is what makes `do.py destroy` refuse to delete it out from under you.
4. **Golden freshness.** Rebuild the golden snapshot when a piece needs current packages,
   or about monthly. Delete the old one after the new one verifies.
5. **Cost math for manifests.** Estimate **how long the box stays alive**, not how many
   experiments run on it. That is the whole bill. Eleven experiments back to back on a warm
   box cost four cents; one experiment with a 24-hour wait in it costs fifty times more.
   See `memory/lesson_lab_cost_is_wallclock_not_experiments.md`.
6. **Benchmarks.** Own box, nothing else running, n≥3 runs, report median and spread. A
   single lucky run is not a measurement, and V1 will reject it.
7. **Shared infra stays shared.** Never install anything global on an instance other pieces
   use — resources only, namespaced `cf-<slug>-*`.
8. **Failures are evidence.** The experiment that broke something and the fix that
   unbroke it is usually the most valuable thing the piece will publish, because it is the
   part no competitor bothered to generate. Keep the failing output.

## Golden image contents (bootstrap-ubuntu.sh)

Ubuntu + docker-ce + the compose plugin + git/curl/jq/htop/unzip. Deliberately minimal:
piece-specific dependencies belong in the piece's own scripts, so the evidence records
exactly what was installed.

## Before you launch a detached experiment

Four traps that have each cost a full re-run. All four are cheap to check and expensive to
rediscover:

- `grep -n '| *head' script.sh` — under `set -o pipefail`, `head` closing the pipe kills the
  whole script with SIGPIPE.
- Sentinels must carry exit status: `if bash x.sh > log 2>&1; then touch .done; else touch .fail; fi`.
  A bare `; touch .done` fires on failure too, and your poller reports success on a dead run.
- Assert the healthy path BEFORE any experiment that breaks something, inside the script.
- Neutralize unattended upgrades on a fresh box before the first `apt` call.

Full versions in `memory/lesson_evidence_scripts_pipefail_and_sentinels.md` and
`memory/lesson_experiments_that_break_their_transport.md`.
