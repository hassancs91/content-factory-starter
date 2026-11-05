# Recon module (S2)

Goal: before anything is written, know exactly what already ranks, what it covers, what it
misses, and what an answer engine would cite — so the editorial plan at S3 is built on
gaps, not guesses.

Output: `content-lab/<slug>/recon/recon-report.md`, from
[templates/recon-report.md](../templates/recon-report.md).

## Tooling: deliberately unspecified

**This module tells you what to find out, not which API to call.** There is no `recon.py`
in this kit, and that is on purpose — keyword tooling is the most personal, most
frequently-changing part of anyone's stack, and a script hardcoded to one vendor would be
the first thing you had to rewrite.

Use whatever you actually have, in rough order of preference:

1. A keyword API you already pay for (Ahrefs, Semrush, DataForSEO, Keywords Everywhere,
   or similar) — called through an MCP server, a small script, or their web UI.
2. A SERP API (Serper, SearchAPI, ScrapingDog) for the results page itself.
3. Plain web search plus fetching the ranking pages, which your agent can already do.
4. Your own audience: comments, support tickets, community threads, sales calls. For a
   small or new niche this beats every keyword tool, because the volumes there round to
   zero while the demand is real.

**One worked example of plugging in your own** (an example, not a requirement): Keywords
Everywhere has an official MCP server. One command in a terminal adds it to Claude Code at
user scope, so the key is stored in your user config (`~/.claude.json`), never in the
project. Put your own API key in place of `YOUR_KEY`:

```bash
claude mcp add --scope user --transport http keywords-everywhere https://mcp.keywordseverywhere.com/mcp -H "Authorization: Bearer YOUR_KEY"
```

Then add one line under this heading, so recon knows to use it: "Search connector for this
kit: recon gets search volumes and related keywords from the `keywords-everywhere` MCP
server, and the results pages from web search." Its data calls spend credits from your
account (one real piece spent 250 at recon); checking the balance is free. Any other keyword
tool with an MCP server plugs in the same way, with its own command and name.

**Whatever you use, the numbers go into the report as data on disk, not as recalled
figures.** Save the raw payloads into `recon/`. A volume you cannot point at a file for is
a volume you made up.

If you settle on one provider, write a small `recon.py` of your own into `lab/` and note it
here. That is the intended path — the kit ships the contract and lets you own the plumbing.

## Procedure

1. **Seeds.** From the owner's idea plus what you loaded at S1, pick 2–3 seed keywords.
   Pull volumes, related terms, and "people also search for" data for each.
2. **Pick targets.** Primary plus secondaries, chosen on volume × intent fit. Cross-check
   any number that drives the plan against a second source — providers disagree, sometimes
   by multiples.
   - Check whether two phrasings return the *same* results page. If they do, one page can
     take the whole cluster and you should be reporting the cluster total, not the single
     term. If they do not, they are two pieces.
3. **SERP.** Fetch the top 10–15 for the primary and the strongest secondary. Save the
   normalized positions, URLs, and titles.
4. **Dissect.** Fetch the top 5–7 ranking pages properly and read them. For each: what it
   covers, what it misses, and **does it show first-hand evidence?** Usually not. That
   absence is your edge, and it is the single most useful column in the report.
5. **Answer engines.** What would an AI answer lift from a page on this topic — a
   definition, a table, a sequence of steps, a specific number? Which question-shaped
   subqueries deserve their own H2? Check for an AI overview on the query and note what it
   currently cites.
6. **Gap analysis.** Write the differentiator candidates. **If you cannot name a gap that a
   first-hand build or test can own, say the topic is weak BEFORE S3.** That is the whole
   point of doing recon first, and killing a piece here is a success, not a failure.
7. Fill in `recon/recon-report.md` and put a five-line summary in PIECE.md.

## Rules

- Raw payloads stay in `recon/` (committed; raw fetched HTML is gitignored — it is bulky
  and reproducible).
- **Never trust the model's memory for volumes or positions.** Only the data on disk.
- Degrade gracefully and say so. If a provider is down and you fell back to a second
  source, the report says which numbers came from where. A recon report that hides its
  sourcing is worse than one with gaps.
- The recon report is evidence too. Any claim in the finished piece about "what other
  guides miss" traces back to this file, and V2 will ask for it.

## The probe shortcut

When a cheap factual probe can test whether the piece has a real differentiator, **run it
before recon, not after** — see `memory/lesson_probe_differentiator_before_recon.md`. It
flips recon's job from "hunt for an angle" to "size the one we already proved", which is a
much easier question and a much lower-risk Checkpoint 1.

It does not apply to anything about audience demand or competition. That is recon's actual
job and no probe can answer it.
