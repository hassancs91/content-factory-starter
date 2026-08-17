#!/usr/bin/env bash
# E5b — remaining pooling tests, every client bounded (timeout + connect_timeout),
# host psql (postgresql-client), after the supavisor tenant re-seed fixed the hang.
set -uo pipefail
cd /root/supabase/docker
PW=$(grep POSTGRES_PASSWORD= /root/creds.e2 | cut -d= -f2)
T="your-tenant-id"
Q() { PGPASSWORD=$PW PGCONNECT_TIMEOUT=8 timeout 25 psql "$1" ${2:+-c "$2"} ${3:+-c "$3"}; }
echo "=== E5b bounded pooling === $(date -u +%FT%TZ)"

echo "--- prepared statements, session mode 5432 (one connection, works) ---"
Q "postgresql://postgres.$T@localhost:5432/postgres?sslmode=disable" \
  "PREPARE q AS SELECT 1;" "EXECUTE q;" 2>&1 | tail -3

echo "--- prepared statements, transaction mode 6543, SAME connection ---"
Q "postgresql://postgres.$T@localhost:6543/postgres?sslmode=disable" \
  "PREPARE q AS SELECT 1;" "EXECUTE q;" 2>&1 | tail -3

echo "--- transaction mode, PREPARE then EXECUTE on SEPARATE connections (the ORM shape) ---"
Q "postgresql://postgres.$T@localhost:6543/postgres?sslmode=disable" "PREPARE q2 AS SELECT 2;" 2>&1 | tail -1
Q "postgresql://postgres.$T@localhost:6543/postgres?sslmode=disable" "EXECUTE q2;" 2>&1 | tail -2

echo "--- connection math ---"
docker exec supabase-db psql -U supabase_admin -d postgres -tAc "show max_connections;"
grep -E '^POOLER_(DEFAULT_POOL_SIZE|MAX_CLIENT_CONN|DB_POOL_SIZE)=' .env

echo "--- 25 parallel bounded clients through 6543 (pool size 20) ---"
seq 1 25 | xargs -P 25 -I{} env PGPASSWORD=$PW PGCONNECT_TIMEOUT=8 \
  timeout 30 psql "postgresql://postgres.$T@localhost:6543/postgres?sslmode=disable" \
  -tAc "select pg_sleep(0.5), {};" > /tmp/pool_par.out 2>&1
echo "parallel_rc=$?"
echo "parallel_ok_count: $(grep -c '^t|' /tmp/pool_par.out)"
echo "parallel_errors: $(grep -ci 'error\|fatal' /tmp/pool_par.out)"
echo "--- backend connections during idle (the multiplexing proof) ---"
docker exec supabase-db psql -U supabase_admin -d postgres -tAc \
  "select count(*) from pg_stat_activity where application_name ilike '%supavisor%' or usename='postgres';"
echo "date_end_utc: $(date -u +%FT%TZ)"
