#!/usr/bin/env bash
# Golden-image bootstrap for content-factory lab droplets (Ubuntu 24.04).
# Deliberately minimal: piece-specific dependencies belong in each piece's own
# scripts so the evidence ledger records them.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
# First boot runs cloud-init + unattended-upgrades which hold the dpkg lock.
APT="apt-get -o DPkg::Lock::Timeout=600"

echo "== wait for first-boot apt to finish =="
cloud-init status --wait || true

echo "== apt base =="
$APT update -y
$APT install -y ca-certificates curl git jq htop unzip

echo "== docker =="
curl -fsSL https://get.docker.com | sh
systemctl enable --now docker

echo "== versions =="
docker --version
docker compose version
git --version
jq --version

echo "== cleanup for snapshot =="
$APT clean
rm -rf /var/lib/apt/lists/*
cloud-init clean --logs 2>/dev/null || true
truncate -s 0 /etc/machine-id 2>/dev/null || true

echo "BOOTSTRAP_OK"
