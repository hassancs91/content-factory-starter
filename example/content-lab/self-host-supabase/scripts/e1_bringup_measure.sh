#!/usr/bin/env bash
# E1 — official Supabase compose bring-up on a 4GB droplet, measured.
# Runs detached on the box; writes /root/e1.log, touches /root/e1.done at the end.
set -uo pipefail
LOG=/root/e1.log
exec >"$LOG" 2>&1

echo "=== E1 bring-up + measure ==="
echo "host: $(hostname) | kernel: $(uname -r)"
echo "date_start_utc: $(date -u +%FT%TZ)"
echo "boot_time_utc: $(uptime -s)"
free -m; nproc
docker --version; docker compose version

echo "--- clone (sparse, docker dir only) ---"
T0=$(date +%s)
git clone --filter=blob:none --no-checkout --depth 1 https://github.com/supabase/supabase /root/supabase
cd /root/supabase
git sparse-checkout set docker
git checkout
echo "clone_seconds: $(( $(date +%s) - T0 ))"
git log -1 --format='repo_commit: %h %cI'

cd /root/supabase/docker
cp .env.example .env
echo "--- image tags in compose ---"
grep -E '^\s+image:' docker-compose.yml | sed 's/^\s*//' | sort -u

echo "--- pull (timed) ---"
T0=$(date +%s)
docker compose pull -q
PULL_S=$(( $(date +%s) - T0 ))
echo "pull_seconds: $PULL_S"
docker system df

echo "--- up -d (timed to login screen) ---"
T0=$(date +%s)
docker compose up -d
UP_RC=$?
echo "compose_up_rc: $UP_RC"
# Poll Kong :8000 until the dashboard basic-auth challenge answers (401 = alive),
# then until authed request returns HTML (200 = Studio actually serving).
DEADLINE=$(( $(date +%s) + 900 ))
T_401=""; T_200=""
while [ $(date +%s) -lt $DEADLINE ]; do
  CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/ || true)
  [ -z "$T_401" ] && [ "$CODE" = "401" ] && T_401=$(( $(date +%s) - T0 )) && echo "kong_basic_auth_alive_seconds: $T_401"
  CODE2=$(curl -s -o /tmp/studio.html -w '%{http_code}' -u supabase:this_password_is_insecure_and_should_be_updated http://localhost:8000/ || true)
  if [ "$CODE2" = "200" ] || [ "$CODE2" = "307" ]; then T_200=$(( $(date +%s) - T0 )); echo "studio_serving_seconds: $T_200 (http $CODE2)"; break; fi
  sleep 2
done
echo "studio_html_first_bytes:"; head -c 400 /tmp/studio.html; echo

echo "--- container states right after up ---"
docker compose ps --format 'table {{.Name}}\t{{.Image}}\t{{.Status}}'

echo "--- settle 10 minutes ---"
sleep 600
echo "date_settled_utc: $(date -u +%FT%TZ)"
echo "--- health after settle ---"
docker compose ps --format 'table {{.Name}}\t{{.Status}}'
echo "--- docker stats (settled, no-stream) ---"
docker stats --no-stream --format 'table {{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}'
echo "--- free -m (settled) ---"
free -m
echo "--- top RSS processes ---"
ps -eo rss,comm --sort=-rss | head -15
echo "--- disk ---"
df -h / ; docker system df
echo "--- container count ---"
docker ps -q | wc -l

echo "date_end_utc: $(date -u +%FT%TZ)"
touch /root/e1.done
