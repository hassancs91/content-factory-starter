# Evidence + Asset Manifest — self-host-supabase

Approved at Checkpoint 1: PENDING · Approved budget: PENDING (requested: ~$1.00 droplet + ~$0 API)

## Experiments

Every experiment becomes a script in `scripts/` and lands output in `evidence/`.
Failures are evidence too — keep them.

| ID | Question it answers | Infra | Script (planned path) | Est cost | Est time | Status |
|---|---|---|---|---|---|---|
| E1 | Does the official compose fit a $24/mo 4GB box? Time-to-login-screen, container count, idle RAM total + per container (settled 10 min) | cf-self-host-supabase (s-2vcpu-4gb, fra1) | scripts/e1_bringup_measure.sh | $0.07 | ~2h wall | planned |
| E2 | What do the .env defaults leave exposed, and how do you actually rotate JWT secret + ANON/SERVICE_ROLE keys + dashboard password (the #1 GitHub-discussion trap) | same box | scripts/e2_secrets_rotation.sh | — | 1h | planned |
| E3 | Why auth silently breaks: GoTrue SMTP config, signup confirmation + magic link actually delivered (Mailpit on-box catches them; prod relay documented, DO blocks port 25) | same box | scripts/e3_auth_smtp.sh | — | 1h | planned |
| E4 | Does Storage work out of the box? Upload via API + serve + image transform check; S3 option deferred to MinIO guide cross-link | same box | scripts/e4_storage.sh | — | 0.5h | planned |
| E5 | Pooling: direct 5432 vs Supavisor 6543 transaction mode — connection math + the prepared-statements gotcha, demonstrated | same box | scripts/e5_pooling.sh | — | 1h | planned |
| E6 | What upgrading actually takes: pin previous images → upgrade to current, 1s-resolution probe, measured downtime (the Plausible move) | same box | scripts/e6_upgrade_timed.sh | — | 1h | planned |
| E7 | Backups that RESTORE: pg dump + storage volume → wipe volumes → restore onto fresh stack → verify row + uploaded file survive | same box | scripts/e7_backup_restore.sh | — | 1h | planned |
| E8 | Exposure: scanner hits in Kong/auth logs over the run's lifetime on a virgin IP (cheap refresh of the 2m35s story) | same box (log read at end) | scripts/e8_exposure_logs.sh | — | 0.2h | planned |

If E1 OOMs on 4GB that is the headline evidence; re-run on s-4vcpu-8gb ($0.071/hr) and
report BOTH numbers ("4GB does/doesn't survive, 8GB idles at N"). Est below assumes some
8GB hours.

Infra plan:
- Droplet: 1 × s-2vcpu-4gb (fra1, from golden) alive ≈ 8–10h wall-clock ≈ $0.36, plus
  possible s-4vcpu-8gb hours ≈ $0.30. **Total est ≈ $0.70, cap $1.50** (lesson: cost is
  wall-clock, not experiment count).
- DNS: `supabase.lab.example.com` → droplet (dns.py), for real HTTPS via Caddy +
  honest exposure logs. Removed at teardown.
- No Coolify lab (per brief). No API spend beyond the keyword API already logged.

Teardown checklist:
- [ ] `do.py destroy self-host-supabase` + `do.py sweep` clean (GUARDED-only OK)
- [ ] `dns.py rm supabase` + `dns.py sweep` clean
- [ ] PIECE.md `lab_resources` cleared

## Assets

| ID | Type | Shows | Source | Status |
|---|---|---|---|---|
| A1 | capture | Studio login screen — "the compose gets you here" | droplet, browser | planned |
| A2 | capture | Studio dashboard with real test table + data | droplet, browser | planned |
| A3 | capture | Mailpit inbox: the confirmation email that never sends by default | droplet, browser | planned |
| A4 | chart | RAM per container (settled), the "what you're actually running" bar chart | E1 evidence, dataviz skill | planned |
| A5 | chart/clone | Upgrade downtime timeline (probe log, 1s resolution) | E6 evidence | planned |
| A6 | clone | Terminal blocks for key command outputs (clone-kit style) | E1/E7 evidence | planned |
| A7 | og | Social share card | scripts/generate_image.py, Studio light+indigo | planned |

Capture spec: plan doc §7 defaults (viewport stops, not --full; djdt/banners cleaned).
