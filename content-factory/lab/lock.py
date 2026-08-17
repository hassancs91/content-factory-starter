#!/usr/bin/env python3
"""Piece locking + port assignment for parallel factory sessions.

The LEDGER is a *generated view* (see ledger.py), never a guard. This is the
enforcement layer. Locks are created atomically with O_EXCL, so two sessions
racing to claim the same piece cannot both win.

    L=.claude/skills/content-factory/lab/lock.py

    python $L status                                  # who holds what, and is it alive
    python $L claim <slug> --stage S2 --note "recon"  # take the piece, prints your port
    python $L touch <slug> --stage S4                 # refresh heartbeat / update stage
    python $L release <slug>                          # give it back
    python $L ship-claim / ship-release               # the ONE global shared-file lock
    python $L check <slug>                            # exit 0 only if THIS session holds it

Ownership is real, not advisory-by-honour: every lock records the Claude Code
session id (`CLAUDE_CODE_SESSION_ID`) and the long-lived `claude.exe` pid
(`CLAUDE_PID`), both of which the harness exports into every shell. That buys
three things the previous version could not do:

  * **Re-entrancy** — re-claiming a piece you already hold is a no-op that
    succeeds, so "claim before every work burst" is free advice. Previously a
    session could block on its OWN lock and then learn to `--force` past it.
  * **Honest liveness** — a crashed session's lock is detectable immediately
    (its pid is gone) instead of squatting the piece for six hours. The old
    `pid` field recorded the pid of the lock.py process itself, which was dead
    milliseconds after being written, so it proved nothing.
  * **No false STALE** — a session working a piece for ten hours stays ALIVE, so
    nobody force-takes a lock out from under live work.

Locks live in `content-lab/.locks/` (gitignored: runtime state, not ledger).
Every claim/touch/release regenerates LEDGER.md, so the human view is never stale.
"""
import argparse
import json
import os
import socket
import subprocess
import sys
import time
import zlib
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):      # cp1252 consoles choke on the em-dashes
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import ROOT, CONTENT_LAB, env  # noqa: E402

LOCK_DIR = CONTENT_LAB / ".locks"
SHIP_LOCK = "SHIP"
STALE_HOURS = 6

# Port range for per-piece preview servers. Kept clear of 8000/8080 and friends so a
# piece never collides with whatever your project already runs. Override the base with
# CF_PREVIEW_PORT_BASE if 8140-8199 is busy on your machine.
PORT_BASE, PORT_SPAN = int(env("CF_PREVIEW_PORT_BASE", "8140")), 60


# ---------------------------------------------------------------- identity ---

def my_session() -> str:
    return os.environ.get("CLAUDE_CODE_SESSION_ID", "") or ""


def my_pid() -> int:
    try:
        return int(os.environ.get("CLAUDE_PID", "") or 0)
    except ValueError:
        return 0


def short(sid: str) -> str:
    return (sid or "?")[:8]


def pid_alive(pid: int):
    """True / False / None(unknown). PID reuse can make this optimistic, which is
    why it is only ever combined with the session id, never trusted alone."""
    if not pid:
        return None
    if os.name == "nt":
        import ctypes
        PROCESS_QUERY_LIMITED_INFORMATION, STILL_ACTIVE = 0x1000, 259
        k = ctypes.windll.kernel32
        handle = k.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return False
        code = ctypes.c_ulong()
        ok = k.GetExitCodeProcess(handle, ctypes.byref(code))
        k.CloseHandle(handle)
        return bool(ok) and code.value == STILL_ACTIVE
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


# ------------------------------------------------------------------- state ---

def _path(name: str) -> Path:
    return LOCK_DIR / f"{name}.lock"


def _read(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"corrupt": True, "claimed_at": p.stat().st_mtime, "v": 0}


def all_locks():
    if not LOCK_DIR.exists():
        return []
    return [(p.stem, _read(p)) for p in sorted(LOCK_DIR.glob("*.lock"))]


def age_hours(data: dict) -> float:
    return (time.time() - data.get("heartbeat", data.get("claimed_at", 0))) / 3600


def liveness(data: dict) -> str:
    """MINE | LIVE | DEAD | STALE | HELD. Also stamps `_age_hours` for renderers."""
    age = age_hours(data)
    data["_age_hours"] = age
    if data.get("session") and data["session"] == my_session():
        return "MINE"
    alive = pid_alive(data.get("claude_pid", 0))
    if alive is True:
        return "LIVE"
    if alive is False:
        # v2 lock whose owning Claude process is provably gone.
        return "DEAD"
    return "STALE" if age > STALE_HOURS else "HELD"


def taken_ports(exclude: str = "") -> set:
    out = set()
    for name, data in all_locks():
        if name in (exclude, SHIP_LOCK):
            continue
        if liveness(data) in ("DEAD",):
            continue
        if data.get("port"):
            out.add(int(data["port"]))
    return out


def port_for(slug: str, avoid: set = frozenset()) -> int:
    """Stable port per slug, nudged off any port a live piece already holds.
    crc32, NOT hash() — hash() is salted per process. A collision here is not
    cosmetic: two pieces on one port means the second runserver dies and you
    verify the OTHER piece's pages (modules/verify.md V0)."""
    start = zlib.crc32(slug.encode()) % PORT_SPAN
    for i in range(PORT_SPAN):
        candidate = PORT_BASE + (start + i) % PORT_SPAN
        if candidate not in avoid:
            return candidate
    return PORT_BASE + start


def describe(name: str, data: dict) -> str:
    state = liveness(data)
    who = short(data.get("label") or data.get("session", ""))
    legacy = "" if data.get("v", 0) >= 2 else "  (legacy lock: liveness unknown)"
    return (f"  {state:<5} {name:<40} stage={data.get('stage', '?'):<6} "
            f"by={who:<9} port={data.get('port', '-'):<5} age={data['_age_hours']:5.1f}h  "
            f"{data.get('note', '')}{legacy}")


def _sync():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import ledger
        ledger.sync(quiet=True)
    except Exception as exc:                      # never let a render bug block a lock
        print(f"[warn] LEDGER regen failed ({exc}); run ledger.py sync by hand")


# ----------------------------------------------------------------- actions ---

def _payload(slug, stage, note, label, port):
    now = time.time()
    return {
        "v": 2, "slug": slug, "stage": stage, "note": note,
        "session": my_session(), "claude_pid": my_pid(),
        "label": label or short(my_session()), "host": socket.gethostname(),
        "claimed_at": now, "heartbeat": now,
        "claimed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "port": port,
    }


def _write_new(p: Path, payload: dict) -> bool:
    try:
        fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    return True


def claim(slug: str, stage: str, note: str, force: bool, label: str = "") -> int:
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    p = _path(slug)

    for attempt in (1, 2):
        if p.exists():
            held = _read(p)
            state = liveness(held)

            if state == "MINE":
                held.update(heartbeat=time.time(), stage=stage or held.get("stage"),
                            note=note or held.get("note"))
                p.write_text(json.dumps(held, indent=2), encoding="utf-8")
                print(f"[ok] '{slug}' is already yours (re-entrant claim, no-op).")
                print(f"[ok] your dev-server port is {held.get('port')}")
                _sync()
                return 0

            if state == "DEAD" and not force:
                print(f"[reclaim] '{slug}' was held by {short(held.get('session',''))}, "
                      f"whose Claude process (pid {held.get('claude_pid')}) is gone.")
                print("          Taking it. Read its PIECE.md before assuming its "
                      "last recorded step finished.")
                p.unlink(missing_ok=True)
            elif force:
                print(f"[force] taking '{slug}' from {short(held.get('session',''))} ({state}).")
                p.unlink(missing_ok=True)
            else:
                print(f"[BLOCKED] '{slug}' is already claimed.")
                print(describe(slug, held))
                if state == "STALE":
                    print(f"\n  That lock is STALE (>{STALE_HOURS}h, no heartbeat, "
                          "and it predates liveness tracking).")
                    print("  If you are sure nobody is working it: re-run with --force")
                else:
                    print("\n  That session is LIVE. Pick a different piece, or ask the owner.")
                    print("  Do NOT edit its files — not PIECE.md, not its workspace.")
                return 1

        port = port_for(slug, taken_ports(exclude=slug))
        if _write_new(p, _payload(slug, stage, note, label, port)):
            break
        if attempt == 2:
            print(f"[BLOCKED] '{slug}' was claimed by another session mid-race. Re-run status.")
            return 1

    if slug == SHIP_LOCK:
        print("[ok] SHIP lock taken — you are the only session allowed to touch")
        print("     shared files: the page registry, shared templates, static assets,")
        print("     the git index, and any shared MEMORY.md index.")
        print("     RELEASE IT AS SOON AS THE COMMIT LANDS: lock.py ship-release")
        _index_warning()
        _sync()
        return 0

    print(f"[ok] claimed '{slug}' (stage {stage}) as {short(my_session())}")
    print(f"[ok] your preview-server port is {port} "
          f"-> serve this piece on 127.0.0.1:{port}, and nothing else on it")
    print(f"     Release it when you stop: lock.py release {slug}")
    _sync()
    return 0


def _index_warning():
    """A non-empty git index belongs to somebody. `git commit` with no paths would
    swallow it into your commit and nobody would notice until it shipped."""
    try:
        r = subprocess.run(["git", "diff", "--cached", "--name-only"],
                           cwd=ROOT, capture_output=True, text=True, timeout=20)
    except Exception:
        return
    staged = [x for x in r.stdout.splitlines() if x.strip()]
    if staged:
        print(f"\n  [!] The git index is NOT empty — {len(staged)} file(s) already staged:")
        for f in staged[:10]:
            print(f"      {f}")
        if len(staged) > 10:
            print(f"      ... and {len(staged) - 10} more")
        print("  Those are probably another session's. Do NOT `git commit` without")
        print("  naming paths, or they ride along in your commit. Consider `git reset`")
        print("  ONLY if you are certain they are yours.")


def touch(slug: str, stage: str = "", note: str = "") -> int:
    p = _path(slug)
    if not p.exists():
        print(f"[warn] no lock for '{slug}' — claim it first")
        return 1
    data = _read(p)
    state = liveness(data)
    if state not in ("MINE",) and data.get("v", 0) >= 2:
        print(f"[warn] '{slug}' is held by {short(data.get('session',''))} ({state}), not you.")
        return 1
    data["heartbeat"] = time.time()
    if stage:
        data["stage"] = stage
    if note:
        data["note"] = note
    data.pop("_age_hours", None)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[ok] heartbeat refreshed for '{slug}'"
          + (f" (stage {data['stage']})" if stage else ""))
    _sync()
    return 0


def release(slug: str, force: bool = False) -> int:
    p = _path(slug)
    if not p.exists():
        print(f"[ok] '{slug}' was not locked")
        _sync()
        return 0
    data = _read(p)
    state = liveness(data)
    if state in ("LIVE", "HELD") and data.get("v", 0) >= 2 and not force:
        print(f"[BLOCKED] '{slug}' belongs to session {short(data.get('session',''))} "
              f"({state}), not you. Releasing another live session's lock would let a "
              "third session start writing its files. Use --force only if the owner "
              "says so.")
        return 1
    p.unlink()
    print(f"[ok] released '{slug}'")
    _sync()
    return 0


def check(slug: str) -> int:
    """Exit 0 only if THIS session holds the lock. For use as a guard before writes."""
    p = _path(slug)
    if not p.exists():
        print(f"[no] '{slug}' is not claimed by anyone — claim it before writing to it")
        return 1
    data = _read(p)
    if liveness(data) == "MINE":
        print(f"[yes] you hold '{slug}' (port {data.get('port')})")
        return 0
    print(f"[no] '{slug}' is held by {short(data.get('session', ''))} "
          f"({liveness(data)}) — not you. Do not write to its workspace.")
    return 1


def status() -> int:
    locks = all_locks()
    print(f"you are session {short(my_session()) or '(no CLAUDE_CODE_SESSION_ID)'} "
          f"(claude pid {my_pid() or '?'})")
    if not locks:
        print("no locks held — every piece is free")
    else:
        print("locks:")
        for name, data in locks:
            print(describe(name, data))
        dead = [n for n, d in locks if liveness(d) == "DEAD"]
        if dead:
            print(f"\n  {len(dead)} DEAD lock(s) ({', '.join(dead)}) — their Claude process is")
            print("  gone. `claim` takes them automatically; no --force needed.")
        print(f"\n(MINE=this session · LIVE=another live session · DEAD=owner process gone ·")
        print(f" STALE=legacy lock, >{STALE_HOURS}h idle · HELD=legacy lock, recent)")
    _sync()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("claim")
    c.add_argument("slug")
    c.add_argument("--stage", default="S1")
    c.add_argument("--note", default="")
    c.add_argument("--as", dest="label", default="", help="human label for this session")
    c.add_argument("--force", action="store_true")

    t = sub.add_parser("touch")
    t.add_argument("slug")
    t.add_argument("--stage", default="")
    t.add_argument("--note", default="")

    r = sub.add_parser("release")
    r.add_argument("slug")
    r.add_argument("--force", action="store_true")

    for name in ("port", "check"):
        s = sub.add_parser(name)
        s.add_argument("slug")

    sub.add_parser("status")
    sub.add_parser("sync")
    sub.add_parser("whoami")
    sc = sub.add_parser("ship-claim")
    sc.add_argument("--force", action="store_true")
    sc.add_argument("--note", default="shared-file window (registry/templates/static/git)")
    sr = sub.add_parser("ship-release")
    sr.add_argument("--force", action="store_true")

    a = ap.parse_args()
    if a.cmd == "claim":        return claim(a.slug, a.stage, a.note, a.force, a.label)
    if a.cmd == "touch":        return touch(a.slug, a.stage, a.note)
    if a.cmd == "release":      return release(a.slug, a.force)
    if a.cmd == "check":        return check(a.slug)
    if a.cmd == "status":       return status()
    if a.cmd == "sync":         _sync(); return 0
    if a.cmd == "ship-claim":   return claim(SHIP_LOCK, "S8", a.note, a.force)
    if a.cmd == "ship-release": return release(SHIP_LOCK, a.force)
    if a.cmd == "whoami":
        print(f"session={my_session()} pid={my_pid()} host={socket.gethostname()}")
        return 0
    if a.cmd == "port":
        p = _path(a.slug)
        print(_read(p).get("port") if p.exists() else port_for(a.slug, taken_ports()))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
