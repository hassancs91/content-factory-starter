# Content Factory — Starter Kit

A [Claude Code](https://claude.com/claude-code) skill that turns a one-line idea into a
published, evidence-backed page.

Not a prompt. A pipeline: it researches what already ranks, rents a real server, deploys and
breaks the actual software, takes its own screenshots, writes in your voice, ties every
factual claim to an evidence file, and stops at two fixed points for you to approve.

This is the generic version of the system behind
**[learnwithhasan.com/guide/ai-content-factory/](https://learnwithhasan.com/guide/ai-content-factory/)** —
same contract, same tools, same hard-won lessons, with the site-specific parts stripped out
so you can point it at your own niche.

**Free, MIT-licensed, no email required.**

---

## Why this exists

Most "AI content" workflows are a prompt, a generate button, and a publish button. The model
writes from its memory of the internet, which means it writes the average of what everyone
else already said. That average is the slop.

This bets the other way. **The scarce thing is not text generation, it is first-hand
evidence.** So the system spends most of its time generating evidence and only then writes.

The result of one real run: a server rented for about 21 hours, 11 containers deployed, a
connection pooler deliberately broken and diagnosed, 49 mapped claims — and a total lab bill
of **$0.76**. That run is included in [`example/`](example/), unedited.

## What is in the box

```
content-factory/          ← the skill. Copy this whole folder into .claude/skills/
├── SKILL.md              the contract: stages, rules, and where it must stop for you
├── SETUP.md              read this once before the first run
├── modules/              lab · recon · assets · verify · knowledge base
├── profiles/             how a verified draft becomes a page on YOUR site
├── templates/            PIECE.md · claims map · evidence manifest · recon report
├── memory/               17 lessons from real runs — the part that compounds
└── lab/                  the tools (Python, mostly stdlib)
example/                  a real piece, start to finish, lightly scrubbed
docs/                     QUICKSTART.md · ADAPT.md
```

### The tools

| Tool | What it does | Needs |
|---|---|---|
| `lock.py` | Per-piece locks and ports so several pieces run in parallel without collisions | — |
| `ledger.py` | Renders `LEDGER.md` from every piece's frontmatter, so nothing is ever hand-maintained | — |
| `lint_draft.py` | Mechanical voice lint: the tells that survive a careful read | — |
| `capture.py` | Playwright screenshots to a fixed spec, including authenticated pages | Playwright |
| `auth.py` | Log in once by hand in a real browser, reuse the session for every later capture | Playwright |
| `do.py` | Create, drive, and destroy lab VMs — guarded so it cannot delete a sibling's box | DO token |
| `dns.py` | Real subdomains for lab boxes, so TLS and OAuth callbacks work | CF token |
| `clone-kit/` | Pixel-honest browser and terminal frames for illustration | — |

There is deliberately **no keyword tool**. Recon is specified as a contract in
`modules/recon.md` and you plug in whatever you already pay for — that part of everyone's
stack is different, and a hardcoded vendor would be the first thing you had to rip out.

## Install

```bash
git clone https://github.com/hassancs91/content-factory-starter.git
cp -r content-factory-starter/content-factory /path/to/your-project/.claude/skills/
cd /path/to/your-project && mkdir -p content-lab
```

Then open `.claude/skills/content-factory/SETUP.md` and do the two required steps (the
workspace and the writer profile). [docs/QUICKSTART.md](docs/QUICKSTART.md) walks a first
piece end to end.

Requires Python 3.9+. `pip install playwright requests` only when you reach for the tools
that need them.

## The five blocks

The pipeline is five roles. **They are roles, not tools** — every niche fills them
differently, which is what makes this portable.

| Block | The question it answers | Not a tech niche? |
|---|---|---|
| **Contract** | What are your stages, your rules, and where must it stop for you? | Same file. Everyone has a process; almost nobody writes it down |
| **Senses** | How do you know what your audience actually asks? | Keyword tools, your comments, forums, sales calls |
| **Hands** | What does the system capture as proof? | Screenshots of real flows, an exported report, a spreadsheet with its formulas |
| **Lab** | Where does your niche's truth get tested? | A real A/B test in your email tool, a stress-tested financial model, a sandbox account |
| **Brain** | What are your opinions, stories and numbers, written down? | A folder of markdown files. Ten is enough to start |

[docs/ADAPT.md](docs/ADAPT.md) works through what each block becomes outside software.

## The two rules that make it trustworthy

**A claim without a receipt does not ship.** Every factual claim in a draft maps to an
evidence file or a primary source you fetched. Built while writing, not audited afterwards.

**You read it. All of it, before it goes live.** The pipeline exists to make that read cheap
and worth doing — not to replace it.

> Automate the work. Never automate the responsibility.

## Where to start reading

1. [`example/`](example/) — a real run, including the eight-hour failure that became the
   published guide's headline advice
2. [`content-factory/SKILL.md`](content-factory/SKILL.md) — the contract itself
3. [`content-factory/memory/`](content-factory/memory/) — 17 lessons, each written the day
   something cost a re-run

## Honest expectations

- **Your first piece will be slower than writing it yourself.** The payoff starts around
  piece three, when the writer profile is real and the memory folder has your lessons in it.
- **The writer profile is work.** Everything up to verification is portable; publishing is
  yours, and a vague profile produces drafts nobody can ship without a manual pass.
- **This is not autonomous publishing.** Two human checkpoints are load-bearing, and the
  full read at the end is not optional. A system that publishes without you is a different
  system, with different risks, and it is not this one.
- **The lab is optional.** Plenty of good pieces need no server at all. What is not optional
  is that the evidence be *yours*.

## Credits

Built by [Hasan Aboul Hasan](https://learnwithhasan.com). If you want the story of how the
system was designed and what it costs to run, that is
[the guide](https://learnwithhasan.com/guide/ai-content-factory/).

MIT licensed — see [LICENSE](LICENSE). Use it, change it, ship it. No attribution required,
though a link back is always welcome.

<!-- lwh-footer -->

---

## 📘 The free book

This repo is one thing I built with AI. The book is the system underneath it.

**[Vibe Engineering Blocks](https://learnwithhasan.com/blocks/)** is my free 74-page book.
47 building blocks for shipping real apps with AI. One block per page, each with the exact
prompt to hand your AI.

Built by **[Hasan Aboul Hasan](https://learnwithhasan.com)**. I build real products with AI and
write down exactly how.
[Guides](https://learnwithhasan.com/guides/) &nbsp;·&nbsp;
[YouTube](https://www.youtube.com/@HasanAboulHasan) &nbsp;·&nbsp;
[Community](https://learnwithhasan.com/community/)
