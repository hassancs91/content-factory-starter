# Asset module (S5) — captures, clones, charts, social card

Every asset is planned in the evidence manifest at S3, before it is produced. Finals go to
`content-lab/<slug>/assets/`, working files to `assets/raw/` (gitignored). At S8 the finals
are copied wherever your writer profile says images live.

## Real captures (anything that proves a claim)

Harness: `lab/capture.py` — spec baked in at 1440×900, DPR 2, scrollbars hidden.

```bash
CAP=.claude/skills/content-factory/lab/capture.py

python $CAP --url https://your-lab-box.example.com/... --out assets/raw/app.png
python $CAP --url http://127.0.0.1:8150/your-page/ --out assets/raw/page.png --full
python $CAP --file clone.html --out assets/raw/clone.png --selector .ck-browser
```

**Authenticated screens.** `lab/auth.py` opens a real headed browser, waits for you to log
in by hand (OAuth, SSO and 2FA all work, because it is a real browser), and saves the
session for every later capture to reuse:

```bash
python .claude/skills/content-factory/lab/auth.py \
    --url https://app.example.com/login --out content-lab/.auth/app.json \
    --wait-for-url "**/dashboard**"
python $CAP --url https://app.example.com/usage --out assets/raw/usage.png \
    --storage-state content-lab/.auth/app.json
```

That state file holds live session cookies for a real account. **Treat it like a password:**
keep it under `content-lab/.auth/` (gitignored), never copy it into `evidence/` or
`assets/`, and re-mint rather than share it.

`--record-json <substring>` saves every JSON response whose URL contains that substring
next to the shot. On a dashboard this is often worth more than the screenshot: you get the
provider's own numbers as data rather than pixels, and a refresh run months later can diff
it. The sidecar is **raw** — it can contain account ids and tokens, so read it before
promoting anything out of it into `evidence/`.

- **Redaction rule: never blur.** Re-shoot with placeholder values (a dummy email, a test
  key). If the screen cannot be re-staged, clone it instead.
- Two capture traps that produce confidently wrong images, both in `memory/`: lazy-loaded
  images shoot as blank boxes under `--full` (Playwright does not scroll), and pages taller
  than roughly 16,000 px come back as a repeated tile rather than a tall image.

## Clones (`lab/clone-kit/`)

For illustration, for screens that would leak secrets, and for idealized walkthrough states
you cannot reach on demand. `chrome.css` provides `.ck-browser` (browser frame with URL
bar), `.ck-terminal`, `.ck-window`, and `.ck-annotate` / `.ck-badge` / `.ck-box` for
overlays. Copy an example HTML into the piece workspace, build the body, render it with
`capture.py`.

**Honesty rules, and they are not negotiable:**

- Pixel-honest: real fonts, real spacing, the actual UI text of the real version.
- Command output inside a `.ck-terminal` must be **real output pasted from `evidence/`**,
  never typed from memory.
- **A clone never fabricates evidence.** If the image proves a claim, it must be a capture
  of the real thing. A clone illustrates; it does not testify.

## Annotations (re-runnable, never hand-edited pixels)

Wrap the raw capture in `.ck-annotate` with positioned `.ck-badge` / `.ck-box` divs in a
small HTML file in the workspace, then capture that file. This is why annotations are never
painted on in an image editor: a refresh run re-shoots the base image and re-renders the
annotations on top, automatically. One accent colour, numbered badges.

## Charts

Data comes from the JSON in `evidence/`. **A chart is a claim** — V2 applies, and it gets a
row in `claims.md` like any sentence would. Render it from an HTML file in the workspace via
`capture.py`, or inline the SVG when it is small.

## Social card

Whatever generator you use, produce it at S5 and wire it into the page's metadata at S8. It
is the only image most people will ever see of the piece.

## Optimization (at S8)

WebP for page images, explicit `width`/`height` attributes on every `<img>` so the layout
does not shift, lazy loading below the fold **only** (the largest above-the-fold image must
load eagerly or you damage your own LCP), and alt text that describes the evidence rather
than the decoration.
