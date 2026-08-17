# Lesson: `loading="lazy"` images render as blank boxes in full-page captures

**What happened (what-is-self-hosting V6, 2026-08-11):** the guide's three real
screenshots rendered as empty white `<figure>` frames in the V6 desktop capture, while
every inline-HTML figure looked fine. The static URLs were 200 — nothing was broken.
Playwright's `full_page=True` screenshot does not scroll the page, so images below the
fold with `loading="lazy"` (which every performance checklist tells you to put on
in-content images) never start loading before the shot.

**Fix that works:** before the full-page screenshot, scroll through the whole page in
~800px steps with ~250ms settles, scroll back to top, wait ~800ms, then shoot. Put that pre-scroll inside your capture
wrapper so it is not something anyone has to remember.

**How to apply:** any V6 (or refresh) capture of a finished page must either pre-scroll
like that or shoot viewport stops (which scroll by construction). If a screenshot shows
an empty framed box where an `<img>` should be, suspect this before suspecting paths —
`curl -w %{http_code}` the static URL first; it costs nothing and splits the two causes.

Related: [[lesson_v6_capture_long_pages]] (the 16k-px surface limit — the OTHER reason
full-page shots lie; this run hit both on one page).
