# Writer profile: <name> — EXAMPLE, fill this in

Copy to `profiles/<name>.md` and replace every angle-bracket placeholder. One profile per
*kind* of thing you publish: a long guide, a short article, product docs, a newsletter
issue. They can differ a lot; the pipeline stays the same.

**This is the most site-specific file in the kit, and the only one the factory genuinely
cannot guess.** Everything up to S7 is portable. S8 is entirely yours. Expect to write real
detail here — a vague profile produces a draft nobody can publish without a manual pass,
which quietly defeats the whole pipeline.

---

## What to load at S6 (draft)

List every file the drafting agent must read before writing a word. Be specific — a path
that does not exist is a silent skip.

1. `<your voice reference, if you keep site deltas separate from the knowledge base>`
2. `<your component or design reference: what widgets exist and how they are marked up>`
3. `<a gold-standard published example — the single most useful item on this list>`
4. `<your SEO / metadata checklist>`
5. `<the registry, CMS schema, or frontmatter contract a new page must satisfy>`

Point 3 does most of the work. One finished page you are proud of teaches structure faster
than any amount of prose about structure.

## Shape

- **Length:** <target range, and what earns the upper end>
- **Structure:** <how a piece opens, what the first screen must do, how sections are built>
- **Components available:** <callouts, tables, terminal panes, comparison cards, FAQ blocks>
- **Never:** <patterns you reject — the listicle intro, the "in today's world" opener, the
  fake conclusion, whatever you actually hate>

## Voice deltas

The knowledge base's `identity/voice.md` is canonical. List here only what is specific to
*this* surface: mechanical rules (punctuation you ban, heading case), component grammar,
and how CTAs are phrased. If a delta contradicts the knowledge base, the knowledge base
wins and you should flag the conflict rather than silently resolving it.

## Output contract

The precise, checkable definition of "shipped". Every line should be something a script
could verify:

- **File:** `<exact path, e.g. templates/guides/<slug>.html or content/posts/<slug>.md>`
- **Registry / frontmatter:** `<the file to edit and every required field>`
- **Assets:** `<where images live, what format, what naming>`
- **Metadata:** `<title and description limits, canonical, social card wiring>`
- **Schema:** `<what structured data to emit, and when each type applies>`
- **Internal links:** `<the hub or index pages that must link to this piece, and back>`

## Render test

The command that proves the page actually works, run at V3 and again after S8 wiring:

```bash
<your command here>
```

It should assert: status 200, the expected schema types present, TOC anchors resolving to
real ids, every internal link resolving, every image present on disk with dimensions set.

**Write this as a script, not as a checklist.** A checklist gets skimmed on the fifth piece.
A script that exits non-zero does not.

## Publish steps (S8)

1. Take `lock.py ship-claim`.
2. `<copy assets into place>`
3. `<create or update the page file>`
4. `<add the registry / CMS entry>`
5. `<apply reverse links — propose them first, apply after approval>`
6. `<run the render test>`
7. `<commit, hunk-scoped if any shared file was already dirty>`
8. `lock.py ship-release` the moment the commit lands.
9. Fill `url` and `shipped` in the PIECE.md frontmatter.

## Factory-specific differences

If you already have a standalone writing workflow, note here how the factory changes it.
Typically:

- **Intake is replaced by S2 + S3.** The recon report and editorial plan replace whatever
  briefing questions you used to ask. The thesis / differentiator / will-NOT-do block is
  still locked before drafting — it is just grounded in the recon gap analysis now.
- **Screenshots and evidence come from S4 and S5.** The draft cites files in `evidence/`
  and `assets/`, never placeholders, and `claims.md` is built while writing rather than
  audited afterwards.
- **Self-review is folded into S7** as V4 (voice) and V2 (claims).
