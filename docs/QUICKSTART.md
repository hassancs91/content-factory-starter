# Quickstart — your first piece

Goal: one piece, end to end, today. Not a perfect pipeline — **one piece through the full
loop teaches you more than a month of designing the perfect pipeline.**

Pick something small and real. A topic you already know the answer to is ideal for run one:
you will spot a wrong claim instantly, which is exactly what you want while you are learning
to trust the machinery.

## 1. Install (5 minutes)

In Git Bash (Windows) or any bash:

```bash
git clone https://github.com/hassancs91/content-factory-starter.git
mkdir -p /path/to/your-project/.claude/skills
cp -r content-factory-starter/content-factory /path/to/your-project/.claude/skills/
cd /path/to/your-project
mkdir -p content-lab
printf '\n.env\ncontent-lab/.locks/\ncontent-lab/.ssh_known_hosts.d/\ncontent-lab/.auth/\ncontent-lab/*/evidence/raw/\ncontent-lab/*/assets/raw/\ncontent-lab/*/recon/serp/pages/\n' >> .gitignore
python .claude/skills/content-factory/lab/lock.py status
```

Or in PowerShell:

```powershell
git clone https://github.com/hassancs91/content-factory-starter.git
New-Item -ItemType Directory -Force C:\path\to\your-project\.claude\skills | Out-Null
Copy-Item -Recurse content-factory-starter\content-factory C:\path\to\your-project\.claude\skills\
Set-Location C:\path\to\your-project
New-Item -ItemType Directory -Force content-lab | Out-Null
Add-Content .gitignore "", ".env", "content-lab/.locks/", "content-lab/.ssh_known_hosts.d/", "content-lab/.auth/", "content-lab/*/evidence/raw/", "content-lab/*/assets/raw/", "content-lab/*/recon/serp/pages/"
python .claude\skills\content-factory\lab\lock.py status
```

The `.gitignore` line is the same one as in `SETUP.md` step 1, and it covers `.env`, where
your keys go. That last command should print your session id and "no locks held". If it
does, the spine works.

## 2. Fill in the writer profile (30 minutes, and worth every one)

```bash
cd .claude/skills/content-factory
cp profiles/writer-profile.example.md profiles/guide.md
```

Open it and answer the questions honestly. The single highest-value line is the one
pointing at **a finished page you are proud of** — one good example teaches structure faster
than any amount of prose about structure.

You can leave the render test as a TODO on run one. You cannot leave the output contract
vague, or S8 has nothing to aim at.

## 3. Start ten knowledge files (30 minutes, optional but this is the difference)

A folder, ten markdown files, `BRAIN_DIR` in your `.env`:

- `identity/voice.md` — how you write. Rhythm, banned phrases, what you never claim.
- `identity/beliefs.md` — three to five positions you will actually defend.
- `knowledge/stories/` — your five best stories, **with the real numbers**.

Skip this and the drafts come out competent and anonymous. It is the most common reason a
factory disappoints its owner on run one.

## 4. Run the piece

In Claude Code, from your project:

```
/content-factory new how to <the thing you know>
```

Then get out of the way until it stops. Here is what to expect:

| It does | You do |
|---|---|
| S1–S2: loads your voice, researches the topic, dissects what ranks | nothing |
| S3: proposes a thesis, an outline, experiments, and a cost estimate | **Checkpoint 1 — read the plan and the budget. Approve, change, or kill the topic** |
| S4–S7: runs the experiments, captures assets, drafts, verifies | nothing |
| S8: publishes to your site | **Checkpoint 2 — read every word** |
| S9: proposes what it learned back to your knowledge base | approve entry by entry |

**Checkpoint 1 is where your leverage is.** A bad plan approved cheaply costs you the whole
run; ten minutes of reading here saves hours downstream. Push back on the differentiator
specifically: if the plan cannot name something the piece will have that no ranking page
has, the topic is not ready, and saying so is a valid outcome.

## 5. Afterwards: write down what hurt

```bash
# .claude/skills/content-factory/memory/lesson_<what_bit_you>.md
```

One file, what happened, why, how to apply it next time. Add a line to `memory/MEMORY.md`.

The kit's `memory/` sits under `.claude/`, and Claude Code asks before it writes anything
there. So every lesson write-back is an approval: in an interactive session (the VS Code
panel or the terminal), say yes when it asks. In print mode (`claude -p`) the write is
refused outright, even with `--permission-mode acceptEdits`. A test run of this kit in a
new project hit exactly that and parked its four lessons in the piece's `PIECE.md` Decision
log instead; move lessons like those into `memory/` yourself.

This is the step everyone skips, and it is the one that makes run five better than run one.
The twenty lessons shipped in this kit are exactly that: seventeen accumulated across
25 pieces, and three from that test install of the kit on Windows.
**A factory that never writes lessons back is just a long prompt.**

## Troubleshooting

**"It wrote something generic."** Your knowledge base is thin or was not loaded. Check the
S1 log in `PIECE.md` — it lists exactly what went in. Nothing in, nothing out.

**"It made a claim I cannot verify."** Open `claims.md`. If the claim has no row, V2 was
skipped or rushed; re-run it. If the row points at a source that does not support the claim,
that is the machinery working — fix the claim, and write a lesson about how it got through.

**"Checkpoint 1 asked for more money than I expected."** Cost tracks how long a box stays
alive, not how many experiments run. Ask which line item is the wall-clock driver, and
whether an experiment with a long wait in it can be time-boxed instead
(`memory/lesson_timeboxed_experiments.md`).

**"Two sessions clashed."** They should not. Run `lock.py status` — every piece has one
owner and one port. If a lock reads DEAD, that session crashed and its `PIECE.md` may
overstate what actually finished; read it before continuing.

**"S8 does not know where to put the file."** The writer profile is not filled in. That is
the one file the factory genuinely cannot guess.
