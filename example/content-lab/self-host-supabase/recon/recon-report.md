# SEO-GEO Recon — self-host-supabase

Date: 2026-08-11 · Sources: a keyword API; volumes consistent across 3 seed pulls (no second-source cross-check run — no single volume drives the plan, the cluster is uniformly small and the SERP is the signal)
Raw payloads: `recon/keywords.json`, `recon/serp/*.json`, fetched pages in `recon/serp/pages/`

## 1. Keywords

| Keyword | Volume | Intent | Role |
|---|---:|---|---|
| supabase self host | 590 | How-to | **primary** (highest-volume phrasing) |
| supabase self hosted | 590 | How-to/info | primary variant (same SERP) |
| self host supabase | 320 | How-to | secondary (briefed phrasing) |
| self hosted supabase | 320 | How-to | secondary |
| supabase docker | 260 | How-to | secondary H2 |
| supabase docker compose | 90 | How-to | secondary H2 |
| install supabase | 110 | How-to | absorbed |
| supabase self hosted limitations | 10 | Question | H2 (GEO) |
| supabase self host vs cloud | 10 | Question | H2 (GEO) |
| supabase self host pricing | 10 | Question | H2 (GEO) |
| digitalocean supabase | 10 | How-to | absorbed (our lab IS this) |

Cluster ≈ 1,900/mo — about 3× the ~640 in the plan doc, because `supabase self host(ed)`
(590+590) outweighs the briefed `self host supabase` phrasings. Same SERP for both
orderings (verified: both queries return the identical top 9), so one page takes the
whole cluster. `supabase` head term (135k) belongs to the future Wave-2 APP page, not
this guide — do not chase it here.

## 2. Top-15 SERP dissection

Queries: `self host supabase` + `supabase self hosted` · US · 2026-08-11 · **identical top 9, only 9 organic results returned per query**

| # | URL | Words | Schema | First-hand? | Covers | Misses |
|---|---|---:|---|---|---|---|
| 1 | supabase.com/docs/guides/self-hosting | 577 | Breadcrumb | n/a (vendor) | Index page: links to docker guide, lists "your responsibilities" | The actual how-to is a click deeper; no numbers, no ops detail |
| 2 | reddit.com r/Supabase (2 threads) | — | — | anecdotes | "how easy is it" + "best decision I made" sentiment | Not a guide at all |
| 3 | supabase.com troubleshooting: feature availability | 172 | — | n/a | Table of what's missing self-hosted | 172 words; no how-to |
| 4 | github.com discussion #39820 "Self-hosting: what's working (and what's not)?" | 20,012 | — | YES (users) | THE pain list: analytics/Logflare (94 mentions), Kong (59), upgrades (20), backups (13), Supavisor, SMTP, volume-permission traps, key generation | It's a forum thread — zero structure, no walkthrough |
| 5 | news.ycombinator.com | 788 | — | anecdotes | "is it one command or a maze" debate | Not a guide |
| 6 | youtube.com "Self-Hosted Supabase in 10 Minutes" | — | — | demo | Cloudbean-sponsored quick demo | The 10-minute framing IS the problem we document past |
| 7 | rapidnative.com (mobile-app SaaS blog) | 4,735 | Article+FAQPage | **no** | Best-structured competitor: architecture, .env, SMTP, storage, backups, hidden costs — all prose | Zero measurements, zero real box, generic advice ("consider monitoring"), mobile-app angle |
| 8 | activeno.de "ultimate guide" | 3,628 | none | YES | Real hands-on: MinIO S3, nginx, Authelia in front of Studio, env config | **Dated 2023-08** — predates Supavisor pooler, analytics changes, current compose; nginx/Authelia path diverges from official stack |
| 9 | supadex.app | 688 | none | no | Thin listicle: CLI vs Coolify/EasyPanel | 688 words of nothing |

Only two real guide competitors (#7, #8). #7 is comprehensive but evidence-free; #8 is
evidence-backed but three years stale. Nobody has both current + first-hand.

## 3. GEO / AEO

- No AI Overview in the the keyword API payload for either query (organic-only). PAA-shaped
  questions live in the related-keywords tail instead (limitations / vs cloud / pricing).
- What an answer engine would lift: (a) a **feature-gap table** (what cloud has that
  self-hosted lacks — the vendor's own troubleshooting page is 172 words, beatable);
  (b) a **minimum-requirements answer with a measured number** ("self-hosted Supabase
  runs ~N containers and idles at N GB RAM — a $X/mo droplet"); (c) numbered install
  steps; (d) a real cost comparison vs Supabase Cloud Pro ($25/mo).
- Question-shaped H2s worth owning: "How much RAM does self-hosted Supabase need?" ·
  "What's missing in self-hosted Supabase?" (limitations) · "Self-hosted vs Supabase
  Cloud: what does it actually cost?" · "How do you upgrade self-hosted Supabase?" ·
  "How do you back up self-hosted Supabase?"

## 4. Gap analysis → differentiator

What ALL ranking pages miss that a first-hand run can own:

1. **Measured resource truth.** Nobody publishes what the ~12-container stack actually
   idles at, or the minimum viable droplet. The #1 HN/Reddit question is "how heavy is
   it really".
2. **The after-the-login-screen ops.** GitHub #39820 is 20k words of users hitting SMTP,
   analytics, Kong, pooler, upgrade and backup pain — no ranking page walks through
   fixing them on a live box. That thread is our outline, written by the audience.
3. **Current-stack accuracy.** The only hands-on competitor (#8) is from 2023-08 and
   predates the current compose (Supavisor, analytics/Logflare requirement, vault key).
   Every "current" page (#7) is prose without a box.
4. **Measured upgrade + restore-tested backup.** The proven LWH move (Plausible guide:
   16s downtime) applied to a stack people genuinely fear upgrading.
5. **Exposure reality.** Studio ships behind basic auth; a fresh droplet gets scanned in
   minutes (prior lab evidence). Nobody covers what to lock down before DNS even exists.

**Recommended differentiator:** the piece Hasan briefed, now SERP-proven: *"the official
docker compose gets you a login screen; here is the real run through everything after
it"* — auth/SMTP, storage, pooler, upgrade (timed), backup (restore-tested), security —
each section anchored to a measured number or captured failure from a real
DigitalOcean droplet, current compose, versions and dates stamped.

## 5. Recommendations

- Slug: `self-host-supabase`
- Meta title (≤60): `Self-Host Supabase: What Breaks After docker compose up`
- Meta description (≤155): `A real self-hosted Supabase run on a $x/mo VPS: auth emails, storage, connection pooling, a timed upgrade, a restore-tested backup, and what broke.`
- Hub: Self Hosting
- Internal links IN: self-hosting hub index; future Supabase APP page (`guide_slug` hook); siblings install-docker-ubuntu + reverse-proxy (their "next steps"); coolify starter guide's "beyond Coolify" mentions
- Internal links OUT: install-docker-ubuntu (prereq), reverse-proxy (concept), what-is-self-hosting (context), secure-coolify-vps (hardening), MinIO guide (S3 storage option), VPS board (money) — **ship only links whose targets are live at S8**
- Schema plan: Article + HowTo (install section) + FAQPage (limitations / RAM / vs cloud)
