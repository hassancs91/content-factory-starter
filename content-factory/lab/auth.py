#!/usr/bin/env python3
"""Mint a Playwright storage_state by logging in once, by hand, in a real browser.

capture.py already reuses an authenticated session via --storage-state. This is the
missing half: the thing that creates one. It opens a headed browser, waits for YOU to
finish logging in (OAuth, SSO and 2FA all work, because it is a real browser), then
writes the session to disk for every later capture to reuse.

    python .claude/skills/content-factory/lab/auth.py \
        --url https://app.example.com/login --out content-lab/.auth/app.json \
        --wait-for-url "**/dashboard**"

Then, from that point on, no login is needed again until the session expires:

    python .claude/skills/content-factory/lab/capture.py \
        --url https://app.example.com/usage --out assets/raw/usage.png \
        --storage-state content-lab/.auth/app.json

The wait is deliberately browser-side and never stdin. This runs under an agent
harness whose stdin is the null device, so "press Enter when you are done" would
return instantly and cheerfully save a logged-OUT session.

The output file holds LIVE session cookies for a real, funded account. Treat it like a
password: keep it under content-lab/.auth/ (gitignored), never copy it into evidence/
or assets/, and re-mint rather than share it.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


def git_ignored(path: Path) -> bool:
    """True if git would ignore this path. The guard below is only worth having if it
    asks git itself rather than pattern-matching a directory name that may not be in
    .gitignore on someone else's checkout."""
    try:
        r = subprocess.run(["git", "check-ignore", "-q", str(path)],
                           capture_output=True, timeout=10)
        return r.returncode == 0
    except Exception:
        return False


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--url", required=True, help="page to open; the login wall is fine")
    p.add_argument("--out", required=True, help="storage_state json (keep out of git)")
    p.add_argument("--wait-for-url", metavar="GLOB",
                   help="save once the browser reaches this URL glob, e.g. '**/dashboard**'")
    p.add_argument("--wait-for-selector", metavar="SEL",
                   help="save once this selector appears (use for SPAs that never change URL)")
    p.add_argument("--wait-seconds", type=int, default=240,
                   help="how long to wait for the login; also the plain timer when neither "
                        "--wait-for-url nor --wait-for-selector is given (default 240)")
    p.add_argument("--width", type=int, default=1440)
    p.add_argument("--height", type=int, default=900)
    p.add_argument("--force", action="store_true",
                   help="write even if the target path is not gitignored")
    a = p.parse_args()

    out = Path(a.out).resolve()
    if not git_ignored(out) and not a.force:
        print(f"REFUSING to write a live session to {out}\n"
              f"  git does not ignore that path, so the cookies could be committed.\n"
              f"  Put it under content-lab/.auth/ (already ignored), or pass --force.",
              file=sys.stderr)
        return 2

    out.parent.mkdir(parents=True, exist_ok=True)
    host = urlsplit(a.url).netloc

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(channel="chrome", headless=False)
        except Exception:
            browser = pw.chromium.launch(headless=False)
        ctx = browser.new_context(viewport={"width": a.width, "height": a.height})
        page = ctx.new_page()
        page.goto(a.url, wait_until="domcontentloaded", timeout=60000)

        print(f"A browser window is open at {a.url}")
        print(f"Log in there. I am waiting up to {a.wait_seconds}s and will save the")
        print("session automatically once you are through. Do not close the window.")
        sys.stdout.flush()

        ms = a.wait_seconds * 1000
        timed_out = False
        try:
            if a.wait_for_url:
                page.wait_for_url(a.wait_for_url, timeout=ms)
            elif a.wait_for_selector:
                page.wait_for_selector(a.wait_for_selector, timeout=ms)
            else:
                page.wait_for_timeout(ms)
        except Exception as e:
            timed_out = True
            print(f"\nWait condition never matched: {type(e).__name__}", file=sys.stderr)
            print("Saving whatever session exists anyway -- verify it below before trusting it.",
                  file=sys.stderr)

        # Let post-login redirects and token exchanges settle before snapshotting.
        page.wait_for_timeout(2500)
        ctx.storage_state(path=str(out))
        final_url = page.url
        browser.close()

    state = json.loads(out.read_text(encoding="utf-8"))
    cookies = state.get("cookies", [])
    domains = sorted({c.get("domain", "") for c in cookies})
    for_host = [c for c in cookies if host.endswith(c.get("domain", "\0").lstrip("."))]

    print(f"\nwrote {out}")
    print(f"  landed on : {final_url}")
    print(f"  cookies   : {len(cookies)} across {len(domains)} domains")
    print(f"  for {host}: {len(for_host)}")
    print(f"  origins   : {len(state.get('origins', []))} with localStorage")

    # Cookie COUNT proves nothing: a login page happily sets CSRF, analytics and
    # session-pending cookies for its own host. The landing URL is the real signal,
    # and a timed-out wait means the login never finished. Failing loudly here is the
    # whole point -- a state file that looks valid but is logged out would make every
    # downstream capture silently screenshot a login screen.
    low = final_url.lower()
    looks_logged_out = any(s in low for s in
                           ("/login", "/signin", "/sign-in", "/sign_in", "/auth/"))
    if not for_host:
        print("  VERDICT: no cookies for the target host -- logged out.", file=sys.stderr)
        return 1
    if looks_logged_out or timed_out:
        why = "landed on a login URL" if looks_logged_out else "the wait condition timed out"
        print(f"\n  VERDICT: NOT AUTHENTICATED ({why}).\n"
              f"  {out} exists but is a logged-out session. Do not use it.\n"
              f"  Re-run and complete the login in the browser window; raise "
              f"--wait-seconds if you need longer.", file=sys.stderr)
        return 1
    print("  VERDICT: authenticated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
