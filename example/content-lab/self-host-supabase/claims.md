# Claims map — self-host-supabase

Every factual/numeric claim in the draft → evidence file or primary source. Built during S6.

## Stack anatomy
- 11 containers, all healthy on a 4GB box → `evidence/e1_bringup.out` (container list + count)
- Gateway is **Envoy v1.39.0** (not Kong) → `evidence/e1_bringup.out` (image list, `supabase-envoy`)
- No analytics/Logflare container in current compose → `evidence/e1_bringup.out` (11-container list has none); recon `recon/serp/pages/04-*` shows old guides centered on it
- Component versions (Postgres 17.6.1.136, gotrue v2.189.0, postgrest v14.12, storage-api v1.60.4, studio 2026.08.03, supavisor 2.9.5, edge-runtime v1.74.0, imgproxy v3.30.1, postgres-meta v0.96.6, realtime v2.102.3) → `evidence/e1_bringup.out` (image tags)
- Repo commit 241bb11, 2026-08-11 → `evidence/e1_bringup.out`

## Resource numbers
- Clone 2s, image pull 114s, 8.9GB images pulled → `evidence/e1_bringup.out`
- Studio serving 20s after `up -d` (307 redirect to /project/default) → `evidence/e1_bringup.out`
- Settled per-container RAM: studio 255, storage 220, realtime 206, meta 124, db 121, edge 100, imgproxy 100, pooler 187, envoy 84, auth 35, rest 32 MiB → `evidence/e1_bringup.out` (docker stats)
- Whole stack idle ≈ 1.5 GB used / 2.37 GB free of 3.9 GB → `evidence/e1_bringup.out` (free -m)
- Disk 11 GB used, images 8.9 GB → `evidence/e1_bringup.out`
- Min viable = 4 GB comfortable (measured 1.5GB idle + workload headroom); 2 GB tight, 1 GB no → INFERENCE from the 1.5GB measurement, labeled as recommendation not measurement

## Secrets
- Default DASHBOARD_PASSWORD=this_password_is_insecure_and_should_be_updated (publicly documented) → `evidence/e2_secrets_rotation.out` + supabase/supabase .env.example (primary)
- Default JWT_SECRET / ANON_KEY / SERVICE_ROLE_KEY are the demo values shipped in the repo → `evidence/e2_secrets_rotation.out`
- ANON/SERVICE_ROLE keys are JWTs signed with JWT_SECRET; can self-sign with openssl HS256 (no web form) → `evidence/e2_secrets_rotation.out` (sign_jwt worked, new keys 200)
- Restart after .env change ≈ 58s → `evidence/e2_secrets_rotation.out`
- POSTGRES_PASSWORD after first boot: changing .env alone does NOT rotate the DB (bind-mount volume keeps first-boot pw); must ALTER USER on the 7 roles → `evidence/e2_secrets_rotation.out` + `evidence/e5b_pooling.out` (old pw fails, new works via pooler)

## Auth / SMTP
- Default SMTP points at nonexistent supabase-mail:2500 → signup returns 500 "Error sending confirmation email" (`dial tcp: lookup supabase-mail ... server misbehaving`) → `evidence/e3_auth_smtp.out`
- User row IS created but unconfirmable → `evidence/e3_auth_smtp.out` (audit event, user_confirmation_requested)
- With real SMTP: signup 200 + confirmation_sent_at, "Confirm Your Email" delivered w/ code → `evidence/e3b_auth_smtp_retry.out` + asset a3_mailpit_inbox
- GoTrue rate limit: 2nd email inside 60s → 429 over_email_send_rate_limit → `evidence/e3b_auth_smtp_retry.out`
- DO blocks outbound port 25 → brain `lesson-2026-05-self-host-smtp-port-25-ptr` + used relay on 587 in prod (documented, not run)

## Pooling
- Both host ports 5432 + 6543 are Supavisor; raw Postgres only inside docker network → `evidence/e45_storage_pooling.out` (ss -tlnp docker-proxy)
- POOLER_DEFAULT_POOL_SIZE=20, MAX_CLIENT_CONN=100, DB_POOL_SIZE=5, PG max_connections=100 → `evidence/e45` + `evidence/e5b_pooling.out`
- Pooler requires tenant suffix `postgres.<POOLER_TENANT_ID>`; plain `postgres` → FATAL ENOIDENTIFIER → `evidence/e5b_pooling.out`
- Rotating secrets after boot silently breaks Supavisor (tenant creds snapshot); fix = delete _supavisor.users+tenants + restart → session transcript (SCRAM ArgumentError traceback) + `evidence/e5b_pooling.out` addendum
- 25/25 parallel clients OK; cross-connection PREPARE/EXECUTE 5/5 (prepared statements work in txn mode) → `evidence/e5b_pooling.out` addendum
- old pw → "password authentication failed" (rotation proof) → `evidence/e5b` + e8 lockdown run

## Storage
- Default file backend: upload → public serve byte-identical → imgproxy resize 200 → `evidence/e45_storage_pooling.out`
- Bytes at ./volumes/storage/stub/stub/<bucket>/... (STORAGE_TENANT_ID=stub) → `evidence/e45_storage_pooling.out`
- storage-api stores object metadata in POSIX xattrs (user.supabase.content-type, cache-control) → `evidence/e7c_xattr_storage_fix.out` (getfattr)

## Upgrade
- Timed upgrade (downgrade to gotrue v2.185.0/postgrest v14.7/studio 07.27 → back to current): up 3s, wall 5s → `evidence/e6_upgrade_timed.out`
- Downtime: 11 non-200 probe samples, longest contiguous outage 5s, several 1-2s blips (rolling per-service restart) → `evidence/e6_upgrade_timed.out` + `evidence/raw/e6_probe.log`
- Signup 200 after upgrade → `evidence/e6_upgrade_timed.out`
- Compose does NOT auto-load override; needs -f both files → `evidence/e6` (first run applied nothing) + `evidence/e8_https_caddy.out`

## Backups
- `docker compose down -v` does NOT delete data: db + storage are BIND MOUNTS (./volumes/db/data, ./volumes/storage); only db-config named volume dies → `evidence/e7_backup_restore.out` (sentinel survived) + docker inspect mounts
- Real restore drill: rm -rf bind mounts → boot from zero (0 auth users, sentinel table gone) → restore → sentinel row + 2 auth users back → `evidence/e7b_real_wipe_restore.out`
- pg_dumpall restore emits benign "already exists" errors (built-in roles/extensions) under ON_ERROR_STOP=0 → `evidence/e7b` (~341 lines, breakdown)
- Plain tar of storage → restored object 500 ENODATA; tar --xattrs → byte-identical 200 → `evidence/e7c_xattr_storage_fix.out`
- Interrupted dumpall restore half-migrates _supavisor → pooler crash-loop "relation clusters already exists"; fix drop schema _supavisor cascade + restart → `evidence/e7c`

## HTTPS / security
- Caddy → real Let's Encrypt cert (issuer Let's Encrypt, 90-day, notAfter Nov 10 2026) on supabase.lab.example.com; https auth/health 200 → `evidence/e8_https_caddy.out`
- Lockdown via ports !override to 127.0.0.1: 0.0.0.0 bindings gone, raw :8000 external refused, https via Caddy still 200 → `evidence/e8_https_caddy.out`
- Compose service names ≠ container names (gateway service = api-gw) → `evidence/e8_https_caddy.out`
- Exposure: boot 12:34:14, first uninvited SSH 12:54:53 (~20 min), 246 attempts, 25 IPs, 75 usernames, "admin" ×92 → `evidence/e_exposure.out`; reinforces brain story-2026-07-fresh-server-found-in-minutes

## Cost / vs Cloud
- Supabase Cloud Pro = $25/mo → supabase.com/pricing (primary; verify at V-time)
- Cloud free tier pauses after 1 week inactivity, 500MB db → supabase.com/pricing (primary; verify)
- Droplet run cost this guide ≈ $0.76 → PIECE.md cost log

## Assets
- a2_studio_table_editor: customers table, 3 rows, RLS disabled badge, real HTTPS URL → captured `assets/raw/a2_studio_table_editor.png`
- a3_mailpit_inbox: 5 "Confirm Your Email" from Supabase Lab → `assets/raw/a3_mailpit_inbox.png`
- a5_studio_auth_users: real signups (ada, founder, post-upgrade, works-now) → `assets/raw/a5_studio_auth_users.png`
