#!/usr/bin/env python3
"""Shared configuration for the factory's lab tools. Standard library only.

Every setting resolves in the same order: real environment first, then the
project-root `.env`, then a default. That order matters — it lets a single run be
overridden inline (`DO_TOKEN=... python do.py ...`) without editing anything.

PROJECT ROOT
    The skill is expected to live at `<project>/.claude/skills/content-factory/`,
    so the root is four levels above this file's parent. If you keep the skill
    somewhere else, set `CONTENT_FACTORY_ROOT` and every tool follows.

`.env` LIVES AT THE PROJECT ROOT AND IS GITIGNORED. Nothing in this kit ever writes
a secret to disk anywhere else, and nothing should: `content-lab/` is committed.
"""
import os
from pathlib import Path

_HERE = Path(__file__).resolve()


def project_root() -> Path:
    override = os.environ.get("CONTENT_FACTORY_ROOT", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    # lab/ -> content-factory/ -> skills/ -> .claude/ -> <project root>
    return _HERE.parents[4]


ROOT = project_root()
CONTENT_LAB = ROOT / "content-lab"


def _dotenv() -> dict:
    """Parse the project-root .env. Deliberately tiny: `KEY=value`, `#` comments,
    optional surrounding quotes. No interpolation, no export handling — anything
    fancier belongs in a real loader, and this only has to find a token."""
    path = ROOT / ".env"
    values = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return values


_CACHE = None


def env(key: str, default: str = "") -> str:
    """Environment, then .env, then default."""
    global _CACHE
    live = os.environ.get(key)
    if live:
        return live
    if _CACHE is None:
        _CACHE = _dotenv()
    return _CACHE.get(key) or default


def require(key: str, why: str) -> str:
    """Same, but exit with an actionable message instead of a traceback."""
    value = env(key)
    if not value:
        raise SystemExit(
            f"{key} is not set.\n"
            f"  Needed for: {why}\n"
            f"  Add it to {ROOT / '.env'} (gitignored) or export it for this run."
        )
    return value
