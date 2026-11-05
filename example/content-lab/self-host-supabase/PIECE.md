---
slug: self-host-supabase
title: "Self-Host Supabase: The Parts the Docker Compose Doesn't Tell You"
status: Shipped            # Planned | Recon | Drafting | In Review | Shipped | Seeded
stage: S8                  # current stage S0–S9
mode: checkpoint           # interactive | checkpoint | autonomous
hub: "Self Hosting"
target_keywords: ["self host supabase", "self hosted supabase"]
budget_est: "$0"
budget_spent: "$0"
opened: 2026-08-11
updated: 2026-08-11
lab_resources: ""          # everything ALIVE for this piece (droplets, DNS, Coolify
                           # projects). Name any box you BORROW from another piece too —
                           # `do.py destroy` reads this to refuse a destroy that would
                           # delete a sibling's evidence. MUST be "" when the piece idles.
url: "https://learnwithhasan.com/guide/self-host-supabase/"
shipped: "2026-08-12, commit 057fb87"
seeded: ""                 # S9: date + brain commit
session_note: "SHIPPED (commit 057fb87). Checkpoint 2 passed (Hasan: 'ship it'). Idle."
next_action: "S9 (later, with Hasan): distill ledger → brain candidate entries + catalog row; prune raw/"
---

<!-- This frontmatter IS the LEDGER. content-lab/LEDGER.md is generated from these
     fields across all pieces, so keep status/stage/updated/lab_resources honest and
     never hand-edit the LEDGER itself. -->


# Self-Host Supabase — piece file

> Resume protocol: read this file top to bottom, then do `next_action`. Update
> frontmatter + the relevant log section after every meaningful step.

## Idea (Hasan's words, verbatim)

> new Self-host Supabase — use slug "self-host-supabase". How-to guide for the
> Self-Hosting hub, from the hub's guide plan guide list. Target:
> "self host supabase" / "self hosted supabase", ~640/mo. Angle: the hard parts
> nobody documents — the official docker compose gets you a login screen, but
> auth config, SMTP, storage, connection pooling, upgrades, and backups are
> where every real deployment breaks; document those from a real run. Lab: own
> DigitalOcean droplet (cf-self-host-supabase), official compose — no Coolify
> lab needed. NOTE: 5 sibling factory sessions are running concurrently
> (install-docker-ubuntu, reverse-proxy, self-host-n8n, self-host-wordpress,
> what-is-self-hosting) — follow the parallel-session rules strictly: lock.py
> status first, claim before touching anything, use your assigned port, and
> plan cross-links to siblings but only ship links whose targets are live.

## Stage checklist

### S0 Intake
- [x] `lock.py claim self-host-supabase` taken; port **8156**
- [x] Slug confirmed with Hasan (pre-specified in the opening request)
- [x] Workspace dirs created (recon/ scripts/ evidence/ evidence/raw/ assets/ assets/raw/ drafts/)

### S1 Brain pull
- [x] knowledge-base `INDEX.md` read; `identity/*` loaded
- [x] Topic-relevant knowledge/lenses loaded (list below in Brain context)

### S2 SEO-GEO recon
- [x] Keyword research (the keyword API, 3 seeds; no 2nd source — cluster uniformly small, SERP is the signal)
- [x] Top-15 SERP fetched + dissected (both phrasings return identical 9 organic results)
- [x] GEO/AEO analysis
- [x] Gap analysis + differentiator candidates
- [x] `recon/recon-report.md` written

### S3 Editorial plan  →  CHECKPOINT 1
- [x] Thesis + differentiator + will-NOT-do scope guard
- [x] Outline (H2s + components)
- [x] Evidence manifest (experiments, infra, scripts planned, cost estimate)
- [x] Asset manifest (every capture/clone/chart/OG planned)
- [x] Hub routing + CTA confirmed
- [x] **Checkpoint 1 approved by Hasan** (record below)

### S4 Lab run
- [ ] Infra provisioned (per manifest; `lab_resources` frontmatter updated)
- [ ] All experiments executed as scripts in `scripts/`
- [ ] Evidence captured to `evidence/` (raw → `evidence/raw/`)
- [ ] Teardown done — `do.py sweep` clean or GUARDED-only; `lab_resources` back to ""

### S5 Assets
- [ ] Real captures per spec
- [ ] Clones built (HTML in workspace) + rendered
- [ ] Charts + OG image
- [ ] Finals in `assets/`, sources preserved

### S6 Draft
- [ ] Full draft in `drafts/` citing evidence
- [ ] `claims.md` complete — zero orphan claims

### S7 Verification (loop each until clean)
- [ ] V1 Evidence cross-check + adversarial pass
- [ ] V2 Claims map verified
- [ ] V3 Technical (check, render, schema, links, lint)
- [ ] V4 Voice (brain voice.md + anti-generic)
- [ ] V5 SEO-GEO vs recon report
- [ ] V6 Visual (desktop/mobile, light/dark screenshots)

### S8 Ship  →  CHECKPOINT 2
- [ ] `lock.py ship-claim` taken (blocks until no other piece is mid-ship)
- [ ] Template + registry + assets → site; reverse links proposed/applied
- [ ] `manage.py check` + render test green
- [ ] Commit is hunk-scoped; `lock.py ship-release` the moment it lands
- [ ] `url` + `shipped` frontmatter filled
- [ ] **Checkpoint 2: Hasan reviewed rendered page** (record below)

### S9 Brain seed
- [ ] Ledger distilled → candidate entries presented
- [ ] Hasan-approved entries written to brain + INDEX + content catalog
- [ ] `evidence/raw/` + `assets/raw/` pruned; `seeded` filled and `status: Seeded`
      (that alone moves the row into the LEDGER Archive table)
- [ ] `lock.py release self-host-supabase`

## Brain context loaded (S1)

- `identity/core.md`, `identity/voice.md`, `identity/beliefs.md` — canonical voice + positioning
- `lenses/self-hosting.md` — platform lens: public ceiling, core+beliefs identity
- `story-2026-05-added-up-my-cloud-bills` — $8.4k/yr managed-cloud math; Supabase Cloud vs self-host cost framing
- `take-2026-07-maintenance-burden-in-seconds` — measured-upgrade-downtime move; repeat it for the Supabase upgrade section
- `story-2026-07-fresh-server-found-in-minutes` — fresh droplet scanned in 2m35s; security framing for exposed Studio/API
- `lesson-2026-05-self-host-smtp-port-25-ptr` — SMTP is a known Supabase self-host pain (auth emails); DO blocks port 25 → use a relay
- `lesson-2026-06-minio-openmaxio-console` — S3 Sig-V4 hostname trap; Supabase Storage has the same public-URL binding class of bug
- `the hub's guide plan` §11.C — this piece is one of 4 app deep-dive guides (self host supabase 640/mo, R5); a Supabase APP page (`supabase` 135k, Wave 2) will exist separately — guide targets the how-to intent only

## Recon summary (S2)

- Cluster ≈ 1,900/mo (3× the brief): `supabase self host(ed)` 590+590 beats `self host(ed) supabase` 320+320; one SERP for all phrasings.
- SERP is discussion-heavy (docs index, Reddit, GitHub #39820, HN) — only 2 real guides: RapidNative (4,735w, zero evidence) and activeno.de (hands-on but 2023-08 stale).
- GitHub #39820 = the outline written by the audience: analytics/Logflare 94 mentions, Kong 59, upgrades 20, backups 13, SMTP, pooler, permission traps.
- Differentiator: current compose + real DO droplet + measured numbers (idle RAM, timed upgrade, restore-tested backup) — nobody has current AND first-hand.
- GEO H2s: RAM needed / what's missing self-hosted / vs cloud cost / upgrade / backup. Schema: Article + HowTo + FAQPage.

## Editorial plan (S3)

**Thesis:** The official docker compose gets you a Supabase login screen in minutes.
Everything that makes it a real deployment — secrets, auth emails, storage, pooling,
HTTPS, upgrades, backups — is undocumented folklore scattered across a 20k-word GitHub
thread. This guide is that folklore, run for real on one droplet, with numbers.

**Differentiator:** current compose + first-hand evidence. The only hands-on competitor
(activeno.de) is from 2023-08; the only comprehensive one (RapidNative) never touched a
box. We publish measured idle RAM per container, a timed upgrade, a restore-tested
backup, and captured failures.

**Will NOT do:**
- Not the `supabase` head-term app page (135k) — that's the Wave-2 APP page's job.
- No Kubernetes, no multi-node, no Coolify path (docs point at compose; Coolify guide can come later).
- No deep reverse-proxy tutorial (sibling guide's job — link it), no SMTP-server-from-scratch (Postal guide exists).
- No edge functions deep-dive (mention status honestly, move on).

**Outline (H2s):**
1. What you actually get (stack anatomy: ~12 containers, what each does; feature-gap table vs Cloud)
2. What it needs (measured: RAM idle/settled, min viable droplet, cost vs Cloud Pro $25/mo)
3. Install, done right (compose + the .env/secrets work FIRST: JWT/anon/service keys, dashboard password, vault key)
4. Auth emails: the part that silently breaks (GoTrue SMTP, confirmation + magic link proven delivered)
5. Storage (file backend proven via API; S3 option → MinIO guide)
6. Connection pooling (5432 vs Supavisor 6543, when each, the gotcha)
7. HTTPS + lock-down (Caddy in front of Kong via lab subdomain; scanner-log evidence; link reverse-proxy + secure-vps)
8. Upgrading without fear (timed, 1s probe)
9. Backups that restore (dump + volumes → wipe → restore → verify)
10. Self-hosted vs Cloud: the honest verdict + FAQ (RAM / limitations / cost H2s for GEO)

**Evidence manifest:** see `evidence-manifest.md` in this folder (E1–E8, est ≈$0.70 cap $1.50)
**Asset manifest:** see `evidence-manifest.md` §Assets (A1–A7)

**Hub routing + CTA:** hub `self-hosting`; funnel → VPS board (DO refer link), self-hosting
course CTA; cross-links to siblings (install-docker-ubuntu, reverse-proxy,
what-is-self-hosting) ONLY if live at S8. Schema: Article + HowTo + FAQPage.

## Checkpoint 1 record

2026-08-11 — Hasan approved the plan as presented ("apprive"), no changes requested.
Approved budget: ~$0.70 est, $1.50 cap droplet spend. Mailpit-on-box approach for auth
emails stands (real 587 relay documented in prose for production).

## Lab run log (S4)

- 2026-08-11 15:33 UTC — cf-self-host-supabase created (s-2vcpu-4gb, fra1, 203.0.113.10), DNS supabase.lab.example.com set.
- E1 launched detached 15:4x — SURPRISE during pull: current compose uses **envoyproxy/envoy v1.39.0** as the gateway, not Kong. Every ranking competitor documents Kong (RapidNative) or nginx (activeno.de 2023). Also seen: edge-runtime v1.74.0, storage-api v1.60.4. Full tag list lands in e1 evidence.
- Scripts e2–e8 written; e8 adjusted to supabase-envoy after e1 confirmed names.
- E1 DONE (evidence/e1_bringup.out): repo commit 241bb11 (2026-08-11). 11 containers, ALL healthy on 4GB. Timings: sparse clone 2s, pull 114s (8.9GB images), `up -d` → Studio serving in 20s. Settled (10 min): container RAM sum ≈ 1,464MiB; free shows 1,545MB used / 2,370MB available; disk 11GB used. Biggest per-container: studio 255MiB, storage 220MiB, realtime 206MiB, pooler 187MiB. Stack surprises: Envoy gateway (Kong gone), NO analytics/Logflare container, Postgres 17.6, Supavisor publishes BOTH 5432+6543 on 0.0.0.0 (internet-exposed with documented default creds), dashboard basic-auth 401 with publicly documented default password, SMTP defaults point at nonexistent supabase-mail:2500 (auth emails dead on arrival).
- E2 DONE (evidence/e2_secrets_rotation.out): rotated JWT_SECRET + self-signed ANON/SERVICE_ROLE JWTs (openssl HS256, no web form needed) + dashboard pw + vault key + SECRET_KEY_BASE; restart 58s; old keys now 401, new accepted. Nuances: (a) `/rest/v1/` root returns 403 even with a VALID anon key (OpenAPI restricted) — 401-vs-403 distinguishes bad key from no-permission; real health probe = `auth/v1/health` + apikey (200). (b) in-container psql can't prove password rotation (local trust auth accepts anything) — POSTGRES_PASSWORD after first boot requires ALTER USER on 7 roles, done + stack healthy; end-to-end proof deferred to E5's host-side pooler connections which use the new password.
- E3 DONE (evidence/e3_auth_smtp.out + e3b retry): default SMTP host `supabase-mail:2500` doesn't exist → signup returns 500 "Error sending confirmation email", user created but unconfirmable (exact GoTrue error captured: `dial tcp: lookup supabase-mail ... server misbehaving`). With Mailpit wired via SMTP_* env: signup 200 with confirmation_sent_at, "Confirm Your Email" delivered (code 624377). Bonus: GoTrue built-in rate limit — 2nd email inside 60s → 429 over_email_send_rate_limit. Retry note: mailpit must join `supabase_default` network, not docker_default.
- E4 DONE (evidence/e45_storage_pooling.out): bucket create → png upload → public serve byte-identical → imgproxy resize 200. Bytes at `volumes/storage/stub/stub/<bucket>/<path>/<uuid>` on host (STORAGE_TENANT_ID=stub).
- E5 SAGA (evidence/e45 + e5b_pooling.out): first run HUNG 8h at 25-parallel-clients (waiter timed out silently; caught on manual check). Diagnosis chain: (1) psql sslmode=prefer + Supavisor without downstream cert can stall; (2) REAL cause: E2's rotation — Supavisor snapshots tenant creds at first boot encrypted with VAULT_ENC_KEY; after rotating both, its backend SCRAM auth crashes (Postgrex ArgumentError, traceback captured) and CLIENTS HANG FOREVER, no error. FIX (documented for guide): `delete from _supavisor.users; delete from _supavisor.tenants;` + `docker compose restart supavisor` → re-seeds from env. After fix: txn 6543 + session 5432 both work w/ new pw; no tenant suffix → FATAL ENOIDENTIFIER; old pw → clean auth failure (completes E2 proof). 25/25 parallel clients OK; cross-connection PREPARE/EXECUTE works 5/5 → Supavisor txn mode supports prepared statements (pgbouncer lore obsolete). GUIDE HEADLINE: set ALL secrets BEFORE first `up` — db volume AND supavisor tenant snapshot first-boot values; rotation later = silent pooler hang.
- Cost note: the 8h hang kept the droplet alive overnight — ~9.8h total ≈ $0.35 spent, still under $1.50 cap.
- E6 DONE after 2 false starts (evidence/e6_upgrade_timed.out + raw/e6_probe.log): (a) CRLF trap — git-bash `sed -i` rewrote script CRLF, bash died pre-log while sentinel still fired (memory updated: upload via `tr -d '\r'` + `bash -n`); (b) Compose v5.3.1 does NOT auto-load docker-compose.override.yml — must pass `-f docker-compose.yml -f docker-compose.override.yml` explicitly (guide-worthy). Real run: downgrade gotrue v2.189.0→v2.185.0, postgrest v14.12→v14.7, studio 08.03→07.27, then upgrade back: pull 2s (cached; first pull ~114s but happens BEFORE restart), up 3s, wall 5s. Probe (1s res): 11 non-200 samples total, longest contiguous outage 5s, several 1-2s blips. Signup 200 after upgrade. Matches the "maintenance burden in seconds" take.
- E7 first run (evidence/e7_backup_restore.out) BUSTED A MYTH instead of testing restore: `docker compose down -v` does NOT wipe self-hosted Supabase — Postgres data is a BIND MOUNT (`./volumes/db/data`), storage too (`./volumes/storage`); only the small `db-config` named volume dies. Sentinel row survived the "wipe", so that run proved persistence, not restore (and storage started 500ing). Guide-worthy on two fronts: (a) your data survives a compose down -v (good news), (b) your restore drill must rm -rf the bind mounts to be real.
- E7b DONE (evidence/e7b_real_wipe_restore.out): REAL wipe (down -v + rm -rf bind mounts) → boot from zero (0 auth users, sentinel table gone = wipe verified) → restore. DB restore works (sentinel row + 2 auth users back; ~341 benign "already exists" errors from pg_dumpall re-creating built-in roles/extensions, expected with ON_ERROR_STOP=0). TWO new gotchas: (1) interrupting the dumpall restore left Supavisor's schema half-migrated → pooler crash-loops on "relation clusters already exists"; fix = `drop schema _supavisor cascade` + restart (E7c). (2) storage restore via plain tar → object 500s. E7c ROOT CAUSE: storage-api stores object metadata (content-type, cache-control) in POSIX **extended attributes** (`user.supabase.*`); plain `tar`/`cp` drops them → ENODATA. FIX proven: `tar --xattrs --xattrs-include='*'` → byte-identical serve 200. BIG guide lesson: a Supabase backup MUST capture xattrs or every restored file 500s.
- E7c DONE (evidence/e7c_xattr_storage_fix.out): both fixes proven end-to-end; stack all-healthy.
- E8/HTTPS DONE (evidence/e8_https_caddy.out): Caddy in front of api-gw (Envoy) → real Let's Encrypt cert (issuer "Let's Encrypt", 90-day) on supabase.lab.example.com; https auth/health 200. Set SUPABASE_PUBLIC_URL/API_EXTERNAL_URL/SITE_URL to the domain so Studio works over real host. Lockdown: `ports: !override` to 127.0.0.1 for api-gw(8000)+supavisor(5432/6543) → 0.0.0.0 bindings gone, raw :8000 externally refused, https via Caddy still 200. GOTCHA: compose service names ≠ container names (gateway service = `api-gw`, not `envoy`); override needs the SERVICE key.
- Exposure DONE (evidence/e_exposure.out): SSH — first uninvited attempt 20 min after boot (12:34→12:54), 246 attempts, 25 IPs, 75 usernames, "admin" ×92. (Envoy HTTP log polluted by my own capture traffic — use SSH figures only.) Matches brain story-2026-07-fresh-server-found-in-minutes.
- ASSETS captured over real HTTPS (assets/raw/): a2 customers table w/ 3 rows + "RLS disabled" badge (hero), a3 Mailpit inbox 5 "Confirm Your Email", a4 SQL editor, a5 Auth users (real signups survived restore). All clean, placeholder data, real URL bar.
- TEARDOWN DONE: droplet destroyed 12:30 UTC, DNS removed, sweeps show only GUARDED sibling boxes. lab_resources cleared.

## Asset log (S5)

## Draft log (S6)

## Verification log (S7)

| Loop | Round | Findings | Fixed | Status |
|---|---|---|---|---|
| V1 evidence cross-check | 1 | every draft number spot-checked vs evidence/*.out (11 containers, 1.5GB idle, 20s, 5s upgrade downtime, 246 SSH/20min, 8.9GB) | n/a all match | ✅ |
| V2 claims map | 1 | claims.md built: every factual claim → evidence file or verified primary (supabase pricing/reqs via WebFetch) | zero orphans | ✅ |
| V3 technical | 1 | manage.py check clean; page 200; schema @graph has HowTo+FAQPage+Article+BreadcrumbList; hero-meta/last-verified/toc/breadcrumb present; no leftover template tags; all internal {% url %} resolve | — | ✅ |
| V4 voice | 1 | 2 em dashes in code comments (voice ban) | replaced w/ colon → 0 in my content | ✅ |
| V5 SEO-GEO | 1 | title+meta carry "self-host supabase"/"docker"; H2s cover GEO Qs (RAM/vs-cloud/cost/down-delete/email/upgrade); slug matches; hub+sibling links | matches recon report | ✅ |
| V6 visual | 1 | desktop light + stack section + backups: title/breadcrumb/callouts/stack-grid/terminal-copy all render on-brand; site theme uses own toggle not prefers-color-scheme (dark flag no-op, not a bug); 2 on-page images placed as webp, resolve 200 | — | ✅ |

## Ship record (S8)

2026-08-12 — commit **057fb87**, ship-lock held only for the commit. 6 files: registry
entry (hunk-staged; 2 sibling entries vibe-engineering + install-docker-ubuntu were
uncommitted in the working tree and deliberately EXCLUDED), template, 4 static images
(2 screenshots + card.webp + og.jpg, card generated via Gemini in the family style,
green glow). `manage.py check` clean, Client render 200, committed tree verified (3 own
refs, 0 foreign) via `git show HEAD:`. No sibling template edits (hub auto-lists by
`hub: self-hosting`, so reverse discovery is free). install-docker-ubuntu + reverse-proxy
siblings not yet live → not linked. URL:
https://learnwithhasan.com/guide/self-host-supabase/

## Checkpoint 2 record

2026-08-12 — Hasan reviewed the rendered page (served locally on 8156, screenshots of
title/stack-grid/backups shown) and approved with "ship it". No changes requested.

## Checkpoint 2 record

## Seed record (S9)

_(what entered the brain, what was rejected, catalog row)_

## Decision log

- 2026-08-11 — 5 sibling factory sessions running concurrently (install-docker-ubuntu,
  reverse-proxy, self-host-n8n, self-host-wordpress, what-is-self-hosting). Cross-link
  candidates, but ship a link ONLY if its target is live at ship time.
- 2026-08-11 — Lab plan per Hasan: own DO droplet `cf-self-host-supabase`, official
  Supabase docker compose. No Coolify lab.

## Cost log

| Date | Item | Est | Actual |
|---|---|---|---|
| 2026-08-11 | keyword-API recon (3 keyword seeds ×3cr + 2 SERP ×1cr) | 11 credits | 11 credits |
| 2026-08-11/12 | cf-self-host-supabase droplet (s-2vcpu-4gb, ~21h wall — 8h E5 hang overnight) | $0.70 (cap $1.50) | ~$0.76 |
