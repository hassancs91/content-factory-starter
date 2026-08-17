#!/usr/bin/env python3
"""Mechanical voice/style lint for factory drafts (V3/V4 support).

Catches the rule violations that slip in mechanically; the judgment passes
(anti-generic, claim audit) stay with the model. Exit 1 if findings.

    python lint_draft.py <file.html|file.md> [more files...]

THE RULES BELOW ENCODE ONE PERSON'S VOICE. Edit them to encode yours — that is
the point of the file, not a caveat about it. Keep the ones you agree with, delete
the ones you do not, and add your own tells as you notice them in drafts. A linter
nobody agrees with gets ignored, and an ignored linter is worse than none.

What a mechanical linter is FOR: the tells that survive a careful read because they
look like normal writing. What it is NOT for: deciding whether a paragraph is any
good. That stays in V4, with a human or a model doing actual judgment.
"""
import re
import sys
from pathlib import Path

# (pattern, message). Patterns run case-insensitive on visible text.
RULES = [
    (r"—", "em-dash (—) — use comma, period, or colon"),
    (r"–", "en-dash (–) — use a hyphen or rewrite"),
    (r"\bin this (article|guide|post),? (we|you)('ll| will)\b", "filler intro ('in this article we will')"),
    (r"\bgame.?changer\b", "banned phrase: game-changer"),
    (r"\bleverage\b", "'leverage' as a verb — say 'use'"),
    (r"\bunleash\b", "hype verb: unleash"),
    (r"\bsupercharge\b", "hype verb: supercharge"),
    (r"\bdelve\b", "AI-tell verb: delve"),
    (r"\bseamless(ly)?\b", "hype word: seamless"),
    (r"\brevolutioniz\w+\b", "hype word: revolutionize"),
    (r"\bdon'?t miss out\b", "fear urgency"),
    (r"\byou('re| are) (falling|being left) behind\b", "fear urgency"),
    (r"\bit'?s (important|worth) (to note|noting) that\b", "throat-clearing filler"),
]

STRIP_BLOCKS = re.compile(
    r"<(script|style)[^>]*>.*?</\1>|<pre[^>]*>.*?</pre>|<code[^>]*>.*?</code>|```.*?```",
    re.I | re.S,
)

# ---- Structural checks on copyable code blocks ----
# The premise: a block with a copy button is a promise that its contents can be pasted
# into a terminal. Command output and config-file contents break that promise, and both
# have shipped in real guides more than once. Mark output blocks as output.
# Adapt the class names below (`prompt-block` / `out-block`) to whatever your site uses.
PRE_TAG = re.compile(r"<pre\b([^>]*)>(.*?)</pre>", re.I | re.S)
CLASS_ATTR = re.compile(r'class\s*=\s*["\']([^"\']*)["\']', re.I)

# Lines that are output, not something you type. If a copyable block is mostly these,
# the copy button is lying about what the block is for.
OUTPUT_SHAPED = re.compile(
    r"^\s*(?:\[(?:PASS|FAIL|OK|ERROR)\]|LISTEN\s|debug\d|\w+\[\d+\]:\s|"
    r"(?:Permission denied|Connection (?:refused|closed)|ssh: connect to|"
    r"No such file or directory|Authenticated using))",
    re.I,
)
# Config directives: `Word value` with no shell verb in sight.
CONFIG_SHAPED = re.compile(
    r"^\s*(?:PermitRootLogin|PasswordAuthentication|PubkeyAuthentication|Port\s+\d|"
    r"AuthenticationMethods|KbdInteractiveAuthentication|Match\s+User|ListenStream|"
    r"\[sshd\]|maxretry|bantime|findtime)\b",
    re.I,
)


def lint_structure(path: Path, raw: str) -> int:
    """R2/R3 checks over the raw HTML, before prose stripping."""
    findings = 0
    for m in PRE_TAG.finditer(raw):
        attrs, body = m.group(1), m.group(2)
        line_no = raw[: m.start()].count("\n") + 1
        classes = CLASS_ATTR.search(attrs)
        classes = classes.group(1).split() if classes else []
        text = re.sub(r"<[^>]+>", "", body).strip()
        if not text:
            continue
        body_lines = [ln for ln in text.splitlines() if ln.strip()]
        snippet = body_lines[0].strip()[:80] if body_lines else ""

        known = {"prompt-block", "out-block", "term__body"}
        if not (known & set(classes)):
            print(f"{path.name}:{line_no}: R3 — <pre> with no block class "
                  f"(use prompt-block / out-block)\n    {snippet}")
            findings += 1
            continue

        if "prompt-block" not in classes:
            continue

        # R3: a copyable block that is mostly output
        out_hits = sum(1 for ln in body_lines if OUTPUT_SHAPED.match(ln))
        if out_hits and out_hits >= len(body_lines) / 2:
            print(f"{path.name}:{line_no}: R3 — output-shaped content in a COPYABLE block "
                  f"(use out-block)\n    {snippet}")
            findings += 1

        # Standing rule: no inline comments inside copyable command blocks
        for ln in body_lines:
            if re.match(r"^\s*#", ln) and not CONFIG_SHAPED.match(ln):
                print(f"{path.name}:{line_no}: inline # comment inside a copyable block "
                      f"(explain in the prose line above)\n    {ln.strip()[:80]}")
                findings += 1
                break

        # R2: config directives need their file path with them
        if any(CONFIG_SHAPED.match(ln) for ln in body_lines):
            before = raw[max(0, m.start() - 400):m.start()]
            if "file-block__path" not in before:
                print(f"{path.name}:{line_no}: R2 — config block with no file path above it "
                      f"(wrap in .file-block)\n    {snippet}")
                findings += 1
    return findings


def lint(path: Path) -> int:
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = STRIP_BLOCKS.sub(lambda m: "\n" * m.group(0).count("\n"), raw)
    findings = 0
    lines = text.splitlines()
    for pat, msg in RULES:
        for i, line in enumerate(lines, 1):
            for m in re.finditer(pat, line, re.I):
                snippet = line.strip()[:90]
                print(f"{path.name}:{i}: {msg}\n    {snippet}")
                findings += 1
    if path.suffix.lower() in {".html", ".htm"}:
        findings += lint_structure(path, raw)
    return findings


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    total = sum(lint(Path(p)) for p in sys.argv[1:])
    if total:
        print(f"\n{total} finding(s)")
        sys.exit(1)
    print("lint: clean")


if __name__ == "__main__":
    main()
