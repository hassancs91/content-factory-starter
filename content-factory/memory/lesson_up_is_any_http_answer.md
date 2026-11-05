---
name: lesson_up_is_any_http_answer
description: A readiness poll that waits for a 200 fails a healthy app that answers 302 (a fresh Uptime Kuma 2 redirects into setup); "up" is any HTTP answer, and the evidence records which one.
---

# "Up" is any HTTP answer, not a 200

**What happened (self-host-uptime-kuma, 2026-10-21):** the boot probe polled `/` until it
got a `200`. A fresh Uptime Kuma 2 never answers 200 there. Within 3.5 to 4.8 seconds of
start it answers `302`, a redirect into its database-setup page, because no database has
been chosen yet. The poll kept waiting and reported 158 s for a boot that takes under 5.
That poll and the image pull cost the first attempt 14 minutes.

Plenty of apps do this on a fresh install: a redirect to setup or to a login page, a 401
from an API root. Each of those means the server is up.

**Rule:** a readiness poll counts any real HTTP answer as up (2xx, 3xx, 4xx). `000`
(nothing listening yet) and 5xx mean not yet. Record the code you got, so the evidence says
what "up" meant:

```bash
CODE=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/" || true)
case "$CODE" in 2*|3*|4*) break;; esac
```

Write the code down even when it looks boring. This 302 pointed at the database-setup page,
and that page became one of the piece's experiments.

Readiness is not correctness. Whether the page works is a separate assertion, on what a
user would see: [[lesson_assert_on_what_the_user_sees]] is the mirror of this one (there a
200 passed a broken feature; here waiting for a 200 failed a healthy app).
