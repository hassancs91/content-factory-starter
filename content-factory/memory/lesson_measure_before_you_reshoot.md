# Measure staleness before re-shooting; "refresh the screenshots" is not free

From `react-native-docs-polish` (2026-07-31). The brief said "re-shoot stale
screenshots". The honest answer turned out to be: almost none of them were stale.

## What the measurement said

`scripts/e6_screenshot_staleness.py` compares each shipped webp against a fresh capture
of the same screen, pixel for pixel (same geometry, so no resampling), and reports mean
absolute difference plus the share of pixels that moved:

```
camera           0.29   0.0%  identical enough - keep
i18n             0.19   0.0%  identical enough - keep
home             6.58   5.3%  minor drift        <- only the account email differs
onboarding      20.18  11.9%  STALE - reshoot    <- FALSE POSITIVE, see below
```

7 of 10 were pixel-identical. Two more differed only because the screenshot showed a
different test account's email. Re-shooting all ten would have produced ten changed
binaries in the diff of a **live** product, for no reader-visible improvement.

## The false positive is the interesting part

`onboarding` looked stale at 20.18 mean diff. It was not. The capture script had
navigated to `/onboarding/welcome` using an account that had **already completed
onboarding**, so the app redirected to Home and I photographed the home screen. The
diff was real; my capture was wrong.

Reaching a first-run screen needs a first-run account. Any screen behind a
one-time gate (onboarding, welcome tours, empty states before first data) has to be
shot with a fresh signup, and the assertion has to be on the rendered text
(`'Welcome aboard' in body`), not on the URL you asked for. Same lesson as
[[lesson_assert_on_what_the_user_sees]], one layer up.

## What actually justified a change

- `onboarding.webp` — re-shot properly, from a brand-new account.
- `offline.webp`, `iap.webp` — genuinely absent, and offline is a headline claim.
- `paywall` — captured, inspected, and **deliberately not shipped**: without RevenueCat
  keys and a dev build it renders an "add your key" placeholder. A screenshot of a TODO
  is worse than no screenshot.
- Then `offline.webp` was re-shot a **second** time, because a template fix landed
  mid-run that changed the copy on that very screen. A capture is only valid against
  the head it was taken from; if the product moves during the run, re-shoot what moved.

## Rule

Before re-shooting, write the diff script. Report "N of M materially changed" as a
finding. Churning assets on a live product is a cost, and "they look old" is not
evidence. The corollary: shipping an asset that shows copy you just changed upstream is
the same drift, in the other direction.
