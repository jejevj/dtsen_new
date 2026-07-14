#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# update.sh — Pull latest code, rebuild, dan prune cache otomatis
# Usage: bash update.sh
# ─────────────────────────────────────────────────────────────────────────────
set -e

echo "[1/4] Pull latest code..."
git pull

echo "[2/4] Build dan recreate containers..."
docker compose up -d --build

echo "[3/4] Prune dangling images dan build cache..."
docker image prune -f
docker builder prune -f

echo "[4/4] Status containers:"
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo ""
echo "Disk usage setelah update:"
df -h / | tail -1
