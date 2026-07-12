#!/bin/bash
# ============================================================
# entrypoint.sh — Auto-start sync worker + gunicorn
# ============================================================
# Script ini dijalankan setiap kali container start/recreate.
# Sync worker dijalankan di background, lalu gunicorn dilanjutkan.
# ============================================================

set -e

BASEDIR="/app"
LOG_DIR="$BASEDIR/logs/sync"
mkdir -p "$LOG_DIR"

echo "[entrypoint] ============================================"
echo "[entrypoint] Starting DTSEN API container..."
echo "[entrypoint] ============================================"

# ─── Auto-start sync workers di background ───────────────────────────────────
# Ambil daftar provinsi dari env SYNC_PROVINSI (comma-separated),
# fallback ke semua provinsi jika tidak di-set.
SYNC_PROVINSI="${SYNC_PROVINSI:-}"
SYNC_KELUARGA="${SYNC_KELUARGA:-true}"

if [ -n "$SYNC_PROVINSI" ]; then
  IFS=',' read -ra PROV_LIST <<< "$SYNC_PROVINSI"
  for prov in "${PROV_LIST[@]}"; do
    prov=$(echo "$prov" | tr -d ' ' | tr '[:upper:]' '[:lower:]')
    PID_FILE="$LOG_DIR/worker_anggota_${prov}.pid"
    LOG_FILE="$LOG_DIR/worker_anggota_${prov}.log"

    # Cek apakah worker untuk provinsi ini sudah running
    if [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
      echo "[entrypoint] Worker anggota $prov sudah running (PID=$(cat $PID_FILE)), skip."
    else
      echo "[entrypoint] Memulai sync worker anggota: $prov"
      nohup python3 -u "$BASEDIR/scripts/sync_worker.py" anggota "$prov" \
        >> "$LOG_FILE" 2>&1 &
      echo $! > "$PID_FILE"
      echo "[entrypoint] Worker anggota $prov dimulai (PID=$!)"
    fi
  done
else
  echo "[entrypoint] SYNC_PROVINSI tidak di-set, sync anggota di-skip."
  echo "[entrypoint] Set env SYNC_PROVINSI=aceh,jakarta,... untuk auto-start."
fi

if [ "$SYNC_KELUARGA" = "true" ]; then
  PID_FILE="$LOG_DIR/worker_keluarga.pid"
  LOG_FILE="$LOG_DIR/worker_keluarga.log"

  if [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
    echo "[entrypoint] Worker keluarga sudah running (PID=$(cat $PID_FILE)), skip."
  else
    echo "[entrypoint] Memulai sync worker keluarga..."
    nohup python3 -u "$BASEDIR/scripts/sync_worker.py" keluarga \
      >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "[entrypoint] Worker keluarga dimulai (PID=$!)"
  fi
else
  echo "[entrypoint] SYNC_KELUARGA=false, sync keluarga di-skip."
fi

echo "[entrypoint] ============================================"
echo "[entrypoint] Menjalankan gunicorn..."
echo "[entrypoint] ============================================"

# ─── Jalankan gunicorn (foreground, sebagai PID utama container) ──────────────
exec gunicorn \
  --bind 0.0.0.0:5000 \
  --workers 4 \
  --timeout 120 \
  wsgi:app
