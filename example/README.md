# A real piece, start to finish

This is not a mock-up. It is the actual workspace of a guide that went through this exact
pipeline and got published: **[Self-Host Supabase](https://learnwithhasan.com/guide/self-host-supabase/)**.

Read the finished page first, then read these files. The point of the example is the
distance between the two — what had to happen before that page could honestly say the
things it says.

The only edits are a scrub: a destroyed server's IP, a private lab domain, and the name of
the keyword tool used. Every number, every failure, and the cost log are untouched.

## What is here

| File | Why it is worth reading |
|---|---|
| [PIECE.md](content-lab/self-host-supabase/PIECE.md) | **Start here.** The whole run in one file: the one-line idea, the plan, the checkpoint approvals, and the S4 lab log where you can watch the piece's real subject appear |
| [recon/recon-report.md](content-lab/self-host-supabase/recon/recon-report.md) | The gap analysis. Two of the nine ranking pages were actual guides, one from 2023, and neither had touched a server |
| [evidence-manifest.md](content-lab/self-host-supabase/evidence-manifest.md) | What was approved at Checkpoint 1: eight experiments, $0.70 estimated, a $1.50 cap |
| [claims.md](content-lab/self-host-supabase/claims.md) | 49 factual claims, each pointing at the file that proves it |
| [scripts/](content-lab/self-host-supabase/scripts/) | Two of the experiments, as they actually ran |
| [evidence/](content-lab/self-host-supabase/evidence/) | Their raw output — the files `claims.md` points at |

## The part worth studying

Read the **S4 lab run log** in `PIECE.md`, and specifically the E5 entry.

The plan said "test connection pooling". What happened was that the pooler silently died
after a routine secret rotation — no error, clients just hang forever — and one experiment
sat stuck for eight hours before anyone noticed. The system diagnosed the cause (the pooler
snapshots its credentials at first boot, so rotating them later breaks its login quietly),
wrote a fix, proved the fix, and that became the headline advice of the published guide:
**set every secret before the first boot.**

No competing page had it, because you only learn it by breaking it.

That is the whole argument for the lab. The failure was not a detour from the piece; the
failure *was* the piece. Notice also what it cost: the eight-hour hang kept the server alive
overnight, and the total bill for the run was **$0.76**.

Then read `claims.md` next to `evidence/e1_bringup.out` and check a number yourself. That
loop — claim, receipt, verify — is the machinery, and it is more convincing when you do it
than when it is described.

## Two things this example is missing

- **The draft and the shipped template.** Those are site-specific, and yours will look
  nothing like the original. That gap is exactly what `profiles/writer-profile.example.md`
  is for.
- **`evidence/raw/` and `assets/raw/`.** Pruned at S9, by design.
