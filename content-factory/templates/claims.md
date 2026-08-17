# Claims map — <slug>

Every factual claim in the draft, mapped to the thing that proves it.

**The rule: a claim without a receipt does not ship.** Build this file *while* drafting, row
by row, not as an audit afterwards. Written after the fact it becomes an exercise in
justifying sentences you already like; written during, it changes what you are willing to
write.

A "factual claim" is anything a reader could be wrong about because of you: a version
number, a price, a timing, a capability, a limit, a security statement, a count, a
comparison. Opinions clearly framed as opinions do not need a row. Opinions phrased as facts
do.

Receipts come in exactly two kinds:

- `evidence/<file>` — something this piece's lab run produced. Always preferred.
- A **primary source URL** that you fetched during verification. The vendor's own docs,
  changelog, pricing page, or repository. Not a search snippet, not a blog post about the
  docs, and not the model's memory of the docs.

If a claim has neither, you have three honest options: run an experiment that produces one,
weaken the claim to what you can actually support, or cut it.

---

## <Section of the piece>

- <the claim, in the same words the draft uses> → `evidence/<file>` (<what in that file shows it>)
- <the claim> → <primary source URL> (fetched YYYY-MM-DD)

## <Next section>

- ...

---

## Verification notes

**Re-checked on:** YYYY-MM-DD — the date the "Last verified" line on the page refers to.
Prices and versions must be re-checked against the live source *on that day*, or the line
is decorative.

**Deliberately not claimed:** anything you investigated, could not support, and cut. Worth
recording — it stops the next piece, or the next refresh, from cheerfully re-adding it.

**Claims that will go stale fastest:** list them, so a refresh run knows where to look
first.
