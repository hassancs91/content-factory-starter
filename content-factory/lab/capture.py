#!/usr/bin/env python3
"""Playwright capture harness for content-factory assets.

Default spec (plan §7): 1440x900 viewport, DPR 2, light scheme, scrollbars hidden.
Renders live URLs (real captures) and local HTML files (clone-kit renders) the same way.

    python capture.py --url https://... --out shot.png
    python capture.py --file clone.html --out clone.png --selector .ck-browser
    python capture.py --url http://127.0.0.1:8150/my-page/ --out full.png --full --dark

Authenticated captures (an admin panel, a provider's billing dashboard): pass
--storage-state state.json, minted once by lab/auth.py. Keep it OUT of git.

    python capture.py --url https://app.example.com/usage \
        --out assets/raw/usage.png --storage-state content-lab/.auth/app.json \
        --record-json /usage

--record-json saves every JSON response whose URL contains the given substring to
<out>.xhr.json. On a dashboard this is worth more than the screenshot: it yields the
provider's own numbers as data instead of pixels, it exposes the internal endpoint the
UI calls (which is rarely the one a public API guess would find), and a refresh months
later can diff it. The sidecar is RAW: it can contain account ids and tokens, so read it
before promoting anything out of it into evidence/.
"""
import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    p = argparse.ArgumentParser(description=__doc__)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--url")
    src.add_argument("--file", help="local HTML file (clone-kit render)")
    p.add_argument("--out", required=True)
    p.add_argument("--width", type=int, default=1440)
    p.add_argument("--height", type=int, default=900)
    p.add_argument("--dpr", type=int, default=2)
    p.add_argument("--selector", help="capture just this element")
    p.add_argument("--full", action="store_true", help="full-page capture")
    p.add_argument("--dark", action="store_true", help="prefers-color-scheme: dark")
    p.add_argument("--wait", type=int, default=800, help="extra settle ms after load")
    p.add_argument("--storage-state", help="playwright storage state json for auth'd captures")
    p.add_argument("--record-json", metavar="SUBSTR",
                   help="save JSON responses whose URL contains SUBSTR to <out>.xhr.json; "
                        "pass '' to record every JSON response (endpoint discovery)")
    a = p.parse_args()

    target = a.url or Path(a.file).resolve().as_uri()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(channel="chrome")
        except Exception:
            browser = pw.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": a.width, "height": a.height},
            device_scale_factor=a.dpr,
            color_scheme="dark" if a.dark else "light",
            storage_state=a.storage_state,
            # CSP-strict apps (style-src 'self') block the scrollbar-hiding
            # style tag below; bypass applies to this capture context only.
            bypass_csp=True,
        )
        page = ctx.new_page()

        # Attach BEFORE goto, or the dashboard's own first fetch is already gone.
        xhr = []
        if a.record_json is not None:
            def on_response(resp):
                if a.record_json not in resp.url:
                    return
                if "json" not in (resp.headers or {}).get("content-type", ""):
                    return
                try:
                    body = resp.json()
                except Exception:
                    return  # streamed/aborted bodies are not readable after the fact
                xhr.append({"url": resp.url, "status": resp.status, "body": body})
            page.on("response", on_response)

        page.goto(target, wait_until="networkidle", timeout=60000)
        page.add_style_tag(content="::-webkit-scrollbar{display:none} *{caret-color:transparent}")
        page.wait_for_timeout(a.wait)
        if a.selector:
            el = page.locator(a.selector).first
            el.wait_for(state="visible", timeout=15000)
            el.screenshot(path=str(out))
        else:
            page.screenshot(path=str(out), full_page=a.full)
        browser.close()
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")

    if a.record_json is not None:
        side = out.with_suffix(out.suffix + ".xhr.json")
        side.write_text(json.dumps(xhr, indent=2), encoding="utf-8")
        print(f"wrote {side} ({len(xhr)} JSON responses matching '{a.record_json}')")
        for r in xhr:
            print(f"  {r['status']}  {r['url'][:120]}")
        if not xhr:
            print("  nothing matched -- widen SUBSTR, or the data may be server-rendered "
                  "(check the page HTML for an embedded payload instead)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
