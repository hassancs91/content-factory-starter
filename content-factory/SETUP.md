# Setup — read once, before the first piece

The factory expects a few things to exist. Nothing here takes long, and you can start with
only the first two.

## 1. The workspace (required)

From the root of the project where your content lives:

```bash
mkdir -p content-lab
printf 'content-lab/.locks/\ncontent-lab/.ssh_known_hosts.d/\ncontent-lab/.auth/\ncontent-lab/*/evidence/raw/\ncontent-lab/*/assets/raw/\ncontent-lab/*/recon/serp/pages/\n' >> .gitignore
```

Everything else in `content-lab/` **is** committed on purpose: the scripts, the evidence
files, the claims map, and the recon report are the ledger. They are what makes a `refresh`
run possible six months later, and what lets you prove a number when someone asks.

The skill assumes it lives at `.claude/skills/content-factory/`, four levels below your
project root. If you put it somewhere else, set `CONTENT_FACTORY_ROOT` to the project root
and every script will follow.

## 2. The writer profile (required)

`profiles/` holds one file per kind of thing you publish. Copy the example and fill it in:

```bash
cp profiles/writer-profile.example.md profiles/guide.md
```

This is the file that turns a verified draft into a page on *your* site: where the file
goes, what the registry or CMS entry looks like, which schema you emit, how you run a
render test. **Until it is filled in, S8 has nothing to do.** It is the single most
site-specific file in the kit and the one place you should expect to write real detail.

## 3. The knowledge base (strongly recommended)

A directory of markdown files holding your voice, your positions, and your real stories
with real numbers. Point the skill at it:

```
BRAIN_DIR=/path/to/your-knowledge-base
```

Without it the drafts are competent and anonymous. With it they open with your argument.
[modules/brain.md](modules/brain.md) describes the minimum shape — an `INDEX.md`, an
`identity/` folder, a `knowledge/` folder. Ten files is enough to start.

## 4. Environment (only what you actually use)

All of these live in a gitignored `.env` at the project root. Every one is optional; the
tool that needs it says so when it is missing.

| Variable | Needed by | For |
|---|---|---|
| `DO_TOKEN` | `lab/do.py` | Creating and destroying cloud VMs for experiments |
| `CF_LAB_SSH_KEY` | `lab/do.py` | Path to the SSH key for lab boxes (default `~/.ssh/cf_lab`) |
| `CF_LAB_REGION` | `lab/do.py` | Default region (default `fra1`) |
| `CLOUDFLARE_LAB_DNS_TOKEN` | `lab/dns.py` | Real subdomains for lab boxes, so TLS works |
| `CF_LAB_DNS_ZONE` | `lab/dns.py` | The zone lab hostnames live under, e.g. `lab.example.com` |
| `BRAIN_DIR` | `modules/brain.md` | Your knowledge base |
| `CONTENT_FACTORY_ROOT` | all scripts | Project root override, if the skill is not at the default depth |

The lab is genuinely optional. A factory whose "lab" is a spreadsheet it builds and
stress-tests, or a sandbox account of the tool you teach, needs none of these — see
[../docs/ADAPT.md](../docs/ADAPT.md).

## 5. Python dependencies (only for the tools you use)

```bash
pip install playwright && playwright install chromium   # lab/capture.py, lab/auth.py
pip install requests                                    # lab/do.py, lab/dns.py
```

`lock.py`, `ledger.py`, and `lint_draft.py` are pure standard library. Python 3.9+.

## 6. Check it works

```bash
python .claude/skills/content-factory/lab/lock.py status
python .claude/skills/content-factory/lab/ledger.py sync
```

The first prints your session identity and an empty lock list. The second writes
`content-lab/LEDGER.md`. If both work, the spine is installed and you can run a piece.

## What to tune before piece two

Read `memory/MEMORY.md`. Then, after your first run, write down what hurt — in `memory/`,
not in your head. The lessons shipped in this kit are exactly that, accumulated over
25 pieces. **They are the compounding part of the system.** A factory that never writes
lessons back is just a long prompt.
