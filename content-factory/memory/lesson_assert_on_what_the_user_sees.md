---
name: lesson_assert_on_what_the_user_sees
description: UI verification that asserts on the transport (a websocket opening, a 200) passes when the feature is broken — assert on the rendered thing instead.
---

# Assert on what the user would see, not on the transport

On `secure-coolify-vps` the claim under test was "the web terminal still works with port
6002 closed to the internet". The check watched the browser's websockets, saw
`wss://.../terminal/ws` open, counted zero connections to 6002, and reported a pass.

It was a **false pass**. No server had been selected in the dropdown, so the socket opened
and no shell ever attached. The screenshot showed an empty page with "Select a server or
container" still in the picker. A claim that the terminal worked would have shipped
untested.

Two bugs hid behind the same green result: the script grabbed the sidebar's *team*
switcher instead of the server picker (`select:visible` first match), and on the retry it
selected the `default` placeholder option because the filter only excluded options
containing "team".

**The rule: an assertion must name the thing a reader would see.** Here that was the
rendered prompt, `root@cf-secure-coolify-vps:~#`, read back out of the xterm pane, plus a
count of `.xterm` canvases. Transport-level signals are supporting evidence, never the
assertion.

Applies to: websocket checks, HTTP status codes, "the container is running", "the API
returned 200". All of them are true on a broken feature. Ask what the user would see, then
assert on that string.

Corollary that caught both bugs: **print the options before selecting one.** Dumping every
`<select>` with its `wire:model` and full option list made the wrong-dropdown and
placeholder problems obvious in one run. Cheap, and it turns a silent mis-select into a
visible one. See [[lesson_v6_capture_long_pages]] for the related capture-hygiene rules.
