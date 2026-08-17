# Knowledge base module — pull (S1) + seed (S9)

Your knowledge base is the **single source of truth for voice and identity**: who the owner
is, how they write, what they believe, and the real stories with the real numbers. Point the
skill at it with `BRAIN_DIR` in `.env`.

Read from it anytime. **Write to it ONLY at S9, entry by entry, with explicit approval.**

Without this block the factory produces competent, anonymous pages. With it, the draft opens
with the owner's actual argument instead of a neutral summary of the topic. It is the
difference between "here is what the internet thinks about X" and "here is what I think
about X, and here is what I measured."

## Minimum viable shape

Ten markdown files is enough to start. A directory that works:

```
your-knowledge-base/
├── INDEX.md              # one line per entry — cheap to load, points at everything else
├── identity/
│   ├── core.md           # who you are, what you do, who you serve
│   ├── voice.md          # how you write: rhythm, banned phrases, what you never claim
│   └── beliefs.md        # the positions you actually hold and will defend
└── knowledge/
    ├── lessons/          # something that bit you, or a method that worked
    ├── facts/            # dated, verifiable state of a tool ("X needs Y, checked 2026-07")
    ├── stories/          # a narratable moment, with numbers
    └── takes/            # a position the evidence supports
```

The four kinds matter more than the folder layout. They are the four things a draft can
actually use, and separating them stops "I believe X" from silently becoming "X is true".

## Pull (S1)

1. Read `INDEX.md` — one line per entry, cheap.
2. Always load the whole of `identity/`.
3. Load every `knowledge/` entry whose index line matches the topic.
4. **Respect visibility markers.** Anything marked private or internal is context for you
   and never appears in a published page. If your entries have no such marker, add one
   before the knowledge base holds anything you would not publish.
5. Log what you loaded, and why, in PIECE.md under Knowledge context.

The differentiator you propose at S3 should lean on the takes and stories you loaded. That
is what makes the piece the owner's and not a competitor's.

## Seed (S9) — a dedicated session, AFTER ship and Checkpoint 2

**Distill the ledger, not the published page.** The page is the polished output; the ledger
(scripts, evidence, failures, surprises) holds what future pieces can reuse. The thing that
took eight hours to discover and got one sentence in the guide is exactly the entry worth
writing.

1. Re-read `evidence/`, the Lab run log, and the Decision log in PIECE.md.
2. Draft candidates as lesson / fact / story / take.
3. Present ALL candidates in one table: kind, one-liner, why it is reusable. **Two to four
   per piece, maximum.** Propose more and let the owner cut.
4. For each approved entry, write the file, add its `INDEX.md` row, and link related
   entries.
5. Deferred candidates ("maybe") go to a `PENDING.md`. Never silently dropped.
6. Prune the workspace: delete `evidence/raw/` and `assets/raw/`, keep the scripts, result
   JSON, claims map, and recon report — the refresh runs need them. **Ask before deleting.**
   By S9 the lab is long destroyed, so those raw captures are the only copies that will
   ever exist. Report the size and let the owner decide.
7. PIECE.md frontmatter: `status: Seeded` plus `shipped`, `seeded`, `url`. That alone moves
   the row into the LEDGER's Archive table — the LEDGER is generated, never hand-edited.
   Then `lock.py release <slug>`.

## Write rules that are worth adopting verbatim

These came out of real seed sessions and each one prevents a specific kind of rot:

- **Never rewrite an existing entry's body.** To connect a new entry to an old one, link
  from the NEW one. Only status fields (`superseded_by`, `status: outdated`) may be edited
  on old entries. A knowledge base you rewrite is a knowledge base you cannot trust as a
  record of what you knew when.
- **A story or a take requires a verbatim quote** from the owner, copied character for
  character, so the entry cannot drift into your paraphrase of their opinion. Verify the
  quote with a script; do not eyeball it.
- **Provenance follows the evidence, not the piece.** If a claim's proof lives in a
  different piece, that piece is the source.
- **Validate before committing**: frontmatter schema, topics drawn only from your taxonomy,
  no dead links.
- **Nothing writes itself in.** Every entry is approved individually. This is the gate that
  keeps a hallucinated "fact" from becoming permanent context for every future piece — the
  one failure mode in this whole system that compounds in the wrong direction.

## The flywheel

The first thing a piece does is read the knowledge base. The last thing it does is feed it.
Every run makes the base richer, and a richer base makes the next run better. That loop is
the reason to bother with S9 at all — skip it and you have an expensive pipeline that
learns nothing.
