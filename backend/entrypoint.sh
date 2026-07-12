#!/bin/bash
# ============================================================
# entrypoint.sh — Auto-start sync worker + gunicorn
# ============================================================

set -e

BASEDIR="/app"
LOG_DIR="$BASEDIR/logs/sync"
mkdir -p "$LOG_DIR"

echo "[entrypoint] ============================================"
echo "[entrypoint] Starting DTSEN API container..."
echo "[entrypoint] ============================================"

# ─── Slug provinsi sesuai endpoint ZAWA API (dari tampilan-filter.json) ───────
ALL_PROVINSI=(
  aceh
  sumut
  sumbar
  riau
  kepriau
  jambi
  sumsel
  babel
  bengkulu
  lampung
  dkijakarta
  jabar
  banten
  jateng
  diy
  jatim
  bali
  ntb
  ntt
  kalbar
  kalteng
  kalsel
  kaltim
  kaltara
  sulut
  gorontalo
  sulteng
  sulbar
  sulsel
  sultra
  maluku
  malut
  papbar
  papdy
  papgu
  papsel
  papteng
  papua
)

# ─── Helper: kill stale worker jika PID file ada tapi proses masih jalan ──────
_kill_stale() {
  local pid_file=$1
  if [ -f "$pid_file" ]; then
    local old_pid
    old_pid=$(cat "$pid_file" 2>/dev/null || echo "")
    if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then
      echo "[entrypoint] Killing stale worker PID=$old_pid..."
      kill -TERM "$old_pid" 2>/dev/null || true
      sleep 2
      kill -9 "$old_pid" 2>/dev/null || true
    fi
    rm -f "$pid_file"
  fi
}

# ─── Auto-start sync workers di background ───────────────────────────────────
SYNC_PROVINSI="${SYNC_PROVINSI:-}"
SYNC_KELUARGA="${SYNC_KELUARGA:-true}"

if [ "$SYNC_PROVINSI" = "all" ]; then
  # Sequential — semua provinsi satu per satu dalam satu background process
  PID_FILE="$LOG_DIR/worker_anggota_all.pid"
  LOG_FILE="$LOG_DIR/worker_anggota_all.log"
  _kill_stale "$PID_FILE"
  echo "[entrypoint] Memulai sync anggota SEMUA provinsi (sequential)..."
  (
    for prov in "${ALL_PROVINSI[@]}"; do
      echo "[sync-all] === Mulai provinsi: $prov ==="
      python3 -u "$BASEDIR/scripts/sync_worker.py" anggota "$prov" \
        >> "$LOG_DIR/worker_anggota_${prov}.log" 2>&1
      echo "[sync-all] === Selesai provinsi: $prov ==="
    done
    echo "[sync-all] === SEMUA PROVINSI SELESAI ==="
  ) >> "$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  echo "[entrypoint] Worker sync-all dimulai (PID=$!)"

elif [ -n "$SYNC_PROVINSI" ]; then
  # Paralel — beberapa provinsi spesifik (pisahkan dengan koma)
  IFS=',' read -ra PROV_LIST <<< "$SYNC_PROVINSI"
  for prov in "${PROV_LIST[@]}"; do
    prov=$(echo "$prov" | tr -d ' ' | tr '[:upper:]' '[:lower:]')
    PID_FILE="$LOG_DIR/worker_anggota_${prov}.pid"
    LOG_FILE="$LOG_DIR/worker_anggota_${prov}.log"

    _kill_stale "$PID_FILE"

    echo "[entrypoint] Memulai sync worker anggota: $prov"
    nohup python3 -u "$BASEDIR/scripts/sync_worker.py" anggota "$prov" \
      >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "[entrypoint] Worker anggota $prov dimulai (PID=$!)"
  done
else
  echo "[entrypoint] SYNC_PROVINSI tidak di-set, sync anggota di-skip."
  echo "[entrypoint] Set SYNC_PROVINSI=all untuk semua, atau SYNC_PROVINSI=aceh,sumut,..."
fi

if [ "$SYNC_KELUARGA" = "true" ]; then
  PID_FILE="$LOG_DIR/worker_keluarga.pid"
  LOG_FILE="$LOG_DIR/worker_keluarga.log"

  _kill_stale "$PID_FILE"

  echo "[entrypoint] Memulai sync worker keluarga..."
  nohup python3 -u "$BASEDIR/scripts/sync_worker.py" keluarga \
    >> "$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  echo "[entrypoint] Worker keluarga dimulai (PID=$!)"
else
  echo "[entrypoint] SYNC_KELUARGA=false, sync keluarga di-skip."
fi

echo "[entrypoint] ============================================"
echo "[entrypoint] Menjalankan gunicorn..."
echo "[entrypoint] ============================================"

exec gunicorn \
  --bind 0.0.0.0:5000 \
  --workers 4 \
  --timeout 120 \
  wsgi:app
