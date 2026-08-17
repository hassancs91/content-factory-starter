#!/usr/bin/env python3
"""LEDGER.md is GENERATED, never hand-edited.

The old LEDGER was one shared markdown table that every session read-modify-wrote.
Two sessions editing it at once lose each other's rows, and its `active_session`
column was an honour-system claim that went stale silently (the Plausible pilot ran
a whole second session with that column reading "idle").

So: each piece owns `content-lab/<slug>/PIECE.md` — a file no other session may
touch, because the lock guards it — and this module *renders* the ledger from those
files plus the live locks. Nothing shared is ever mutated, only replaced, so
concurrent syncs converge on the same content instead of clobbering each other.

    python ledger.py sync     # regenerate content-lab/LEDGER.md
    python ledger.py show     # print it without writing

`lock.py` calls sync() automatically on claim/touch/release, so the ledger is
always current without anybody remembering a ritual.
"""
import os
import re
import sys
import tempfile
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):      # cp1252 consoles choke on the em-dashes
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import ROOT  # noqa: E402
CONTENT_LAB = ROOT / "content-lab"
LEDGER = CONTENT_LAB / "LEDGER.md"

FIELDS = ("slug", "title", "status", "stage", "updated", "opened", "hub",
          "lab_resources", "url", "shipped", "seeded", "budget_spent",
          "next_action", "session_note")

HEADER = """# Content Factory — LEDGER

<!-- GENERATED FILE — DO NOT HAND-EDIT. -->
Regenerate with `python .claude/skills/content-factory/lab/ledger.py sync`
(or just claim/touch/release a lock — `lock.py` syncs for you).

Every row is rendered from that piece's `content-lab/<slug>/PIECE.md` frontmatter.
To change a row, edit the PIECE.md you hold the lock for. Editing this file does
nothing: the next sync overwrites it.

The **Lock** column is read live from `content-lab/.locks/` — it cannot lie about
who is working, which is exactly how the old hand-maintained `active_session`
column failed.
"""


def _unquote(value: str) -> str:
    """Take one frontmatter scalar, dropping any trailing ` # comment`."""
    value = value.strip()
    if not value:
        return ""
    if value[0] in "\"'":
        q = value[0]
        out, i, n = [], 1, len(value)
        while i < n:
            c = value[i]
            if c == "\\" and i + 1 < n:
                out.append(value[i + 1])
                i += 2
                continue
            if c == q:
                break
            out.append(c)
            i += 1
        return "".join(out)
    if value.startswith("["):
        end = value.rfind("]")
        return value[: end + 1] if end != -1 else value
    return re.split(r"\s+#", value, maxsplit=1)[0].strip()


def read_frontmatter(piece_md: Path) -> dict:
    """Minimal single-line YAML-ish frontmatter reader. No PyYAML dependency."""
    data = {}
    try:
        text = piece_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return data
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return data
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if m:
            data[m.group(1)] = _unquote(m.group(2))
    return data


def pieces() -> list:
    if not CONTENT_LAB.exists():
        return []
    out = []
    for d in sorted(CONTENT_LAB.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        pm = d / "PIECE.md"
        if not pm.exists():
            out.append({"slug": d.name, "_no_piece_md": True})
            continue
        fm = read_frontmatter(pm)
        fm.setdefault("slug", d.name)
        if fm.get("slug") != d.name:
            fm["_slug_mismatch"] = fm.get("slug")
            fm["slug"] = d.name
        out.append(fm)
    return out


def cell(value, limit=None) -> str:
    """Make a value safe for a markdown table cell."""
    s = " ".join(str(value or "").split()).replace("|", "\\|")
    if limit and len(s) > limit:
        s = s[: limit - 1].rstrip() + "…"
    return s or "-"


def _lock_view():
    """Ask lock.py for the live lock picture. Kept as a soft dependency so this
    module still renders (minus the Lock column) if lock.py is unavailable."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import lock  # noqa: WPS433 - deliberate local import
    except Exception:
        return {}, []
    view = {}
    orphans = []
    for name, data in lock.all_locks():
        if name == lock.SHIP_LOCK:
            view["__ship__"] = (lock.liveness(data), data)
            continue
        view[name] = (lock.liveness(data), data)
    known = {p["slug"] for p in pieces()}
    for name in list(view):
        if name != "__ship__" and name not in known:
            orphans.append(name)
    return view, orphans


def _lock_cell(entry) -> str:
    if not entry:
        return "free"
    state, data = entry
    who = (data.get("label") or data.get("session") or "?")[:8]
    age = data.get("_age_hours", 0.0)
    if state == "DEAD":
        return f"DEAD ({who}) — owner process gone, reclaimable"
    if state == "STALE":
        return f"STALE ({who}, {age:.0f}h idle)"
    return f"{state} {who} · {data.get('stage', '?')} · {age:.1f}h"


def render() -> str:
    all_pieces = pieces()
    locks, orphan_locks = _lock_view()

    active = [p for p in all_pieces if (p.get("status") or "").strip() != "Seeded"]
    archived = [p for p in all_pieces if (p.get("status") or "").strip() == "Seeded"]

    out = [HEADER, "\n## Pieces\n"]
    out.append("| Slug | Title | Status | Stage | Lock | Lab resources | Updated |")
    out.append("|---|---|---|---|---|---|---|")
    if not active:
        out.append("| _(none)_ | | | | | | |")
    for p in active:
        if p.get("_no_piece_md"):
            out.append(f"| {cell(p['slug'])} | **NO PIECE.md** — orphan workspace dir "
                       "| ? | ? | " + _lock_cell(locks.get(p["slug"])) + " | ? | ? |")
            continue
        out.append(
            f"| {cell(p['slug'])} | {cell(p.get('title'), 60)} | {cell(p.get('status'))} "
            f"| {cell(p.get('stage'))} | {_lock_cell(locks.get(p['slug']))} "
            f"| {cell(p.get('lab_resources'), 110)} | {cell(p.get('updated'))} |"
        )

    ship = locks.get("__ship__")
    out.append("\n## Ship window (S8)\n")
    if ship:
        state, data = ship
        out.append(f"**HELD** by `{cell(data.get('label') or data.get('session'))}` "
                   f"({state}, {data.get('_age_hours', 0):.1f}h) — note: {cell(data.get('note'))}")
        out.append("\nNo other session may touch shared files — the page registry, "
                   "shared templates, static assets, the git index, or any shared "
                   "MEMORY.md index — until it is released.")
    else:
        out.append("free — take it with `lock.py ship-claim` before touching any shared repo file.")

    shared = _shared_infra(active)
    if shared:
        out.append("\n## ⚠ Shared lab infra (destroy with care)\n")
        for res, slugs in shared:
            out.append(f"- `{res}` is referenced by **{len(slugs)}** pieces: "
                       + ", ".join(f"`{s}`" for s in slugs))
        out.append("\n`do.py destroy` refuses these unless every referencing piece is free.")

    problems = [f"lock `{n}` has no piece workspace (left over from a deleted piece?)"
                for n in orphan_locks]
    problems += [f"`{p['slug']}` PIECE.md declares slug `{p['_slug_mismatch']}`"
                 for p in all_pieces if p.get("_slug_mismatch")]
    if problems:
        out.append("\n## ⚠ Inconsistencies\n")
        out += [f"- {x}" for x in problems]

    out.append("\n## Archive (seeded pieces)\n")
    out.append("| Slug | Shipped | Seeded | URL |")
    out.append("|---|---|---|---|")
    if not archived:
        out.append("| _(none)_ | | | |")
    for p in archived:
        out.append(f"| {cell(p['slug'])} | {cell(p.get('shipped'), 90)} "
                   f"| {cell(p.get('seeded'), 90)} | {cell(p.get('url'))} |")
    out.append("")
    return "\n".join(out)


def _shared_infra(active) -> list:
    """Droplet names / IPs named by more than one piece's lab_resources."""
    hits = {}
    pattern = re.compile(r"(cf-[a-z0-9-]+|\b\d{1,3}(?:\.\d{1,3}){3}\b)")
    for p in active:
        for token in set(pattern.findall(p.get("lab_resources") or "")):
            hits.setdefault(token, set()).add(p["slug"])
    return sorted(((k, sorted(v)) for k, v in hits.items() if len(v) > 1))


def sync(quiet=False) -> int:
    """Write LEDGER.md atomically. Concurrent syncs are safe: same inputs render the
    same bytes, and os.replace means no reader ever sees a half-written file.

    Windows needs the retry. `os.replace` fails with ERROR_ACCESS_DENIED (WinError 5)
    when anything else holds the destination open — the other session's sync, an
    editor, or the file indexer. Observed on the very first two-claim run, so it is
    the common case, not a corner one. Retrying is correct rather than merely lucky:
    every writer renders identical bytes from the same inputs, so whoever lands last
    lands the same content."""
    CONTENT_LAB.mkdir(parents=True, exist_ok=True)
    body = render()
    # mkstemp, not f".LEDGER.{pid}.tmp" — a pid is not unique enough. Two syncs
    # inside one process (threads, or a lock command that syncs twice) would pick
    # the same name, and the second os.replace fails with "file not found" because
    # the first already moved it. Caught by the 12-way concurrency test.
    fd, tmp_name = tempfile.mkstemp(dir=str(CONTENT_LAB), prefix=".LEDGER.", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    tmp = Path(tmp_name)
    last = None
    for attempt in range(6):
        try:
            os.replace(tmp, LEDGER)
            if not quiet:
                print(f"[ok] LEDGER.md regenerated from {len(pieces())} piece(s)")
            return 0
        except OSError as exc:
            last = exc
            time.sleep(0.05 * (attempt + 1))
    tmp.unlink(missing_ok=True)
    print(f"[warn] could not replace LEDGER.md after 6 tries ({last}). "
          "It is only a rendered view — re-run `ledger.py sync` once the holder lets go.")
    return 1


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "sync"
    if cmd == "show":
        print(render())
        return 0
    if cmd == "sync":
        return sync()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
