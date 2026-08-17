---
name: V6 visual pass on long guides uses viewport stops, not --full
description: capture.py --full silently produces a repeated-tile image on pages taller than Chromium's ~16k px surface limit; capture viewport stops at scroll fractions instead, after clearing debug toolbar, cookie banner and popups.
type: lesson
---

`lab/capture.py --full` on a finished guide page produced an image where the whole article
appeared three times stacked. That is **not a page bug** — the HTML renders once (verified
by counting unique markers in the served HTML). It is Chromium's full-page screenshot
surface limit, roughly 16,000 px; the Plausible guide is ~21,000 CSS px on desktop and
~32,000 on mobile, so the capture wrapped.

**Do this instead** for V6: capture the viewport at scroll fractions.
The reusable pattern: for each profile (desktop 1440x900, mobile 390x844) load the page,
then screenshot at 0/25/50/75/100% of `scrollHeight - innerHeight`. Five stops per profile
reads the whole page and every frame stays legible.

**Clean the frame before shooting**, or the shots are useless as review artifacts:
- Debug toolbars: inject a `display:none !important` style tag before the first shot
- Cookie banner: click "Accept All" before the first shot
- Nag and sponsorship popups inside the app you are shooting: dismiss them **immediately
  before every screenshot**, not once at the start — most of them return on navigation
- Your own site's furniture (social-proof popups, banners) can appear mid-run; it is fine
  to leave those in, just don't mistake one for a layout bug

**Light/dark**: check whether the site actually has a colour-scheme toggle before the
manifest promises "desktop/mobile × light/dark" — that is four shots to produce and review.
A `data-theme` attribute is not proof: it is often a per-section theme, not a colour scheme.
