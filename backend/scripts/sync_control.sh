#!/bin/bash
# ============================================================
# sync_control.sh — Kontrol background sync worker ZAWA
# ============================================================
# Cara pakai:
#   ./scripts/sync_control.sh start anggota aceh
#   ./scripts/sync_control.sh start keluarga
#   ./scripts/sync_control.sh status
#   ./scripts/sync_control.sh stop anggota aceh
#   ./scripts/sync_control.sh logs anggota aceh
#   ./scripts/sync_control.sh resume anggota aceh
# ============================================================

BASEDIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$BASEDIR/logs/sync"
PID_DIR="$LOG_DIR"
PYTHON="${PYTHON:-python3}"

mkdir -p "$LOG_DIR"

_pid_file() {
  local type=$1 prov=$2
  if [ "$type" = "anggota" ]; then
    echo "$PID_DIR/worker_anggota_${prov}.pid"
  else
    echo "$PID_DIR/worker_keluarga.pid"
  fi
}

_log_file() {
  local type=$1 prov=$2
  if [ "$type" = "anggota" ]; then
    echo "$LOG_DIR/worker_anggota_${prov}.log"
  else
    echo "$LOG_DIR/worker_keluarga.log"
  fi
}

cmd_start() {
  local type=$1 prov=$2
  local pid_file log_file
  pid_file=$(_pid_file "$type" "$prov")
  log_file=$(_log_file "$type" "$prov")

  # Cek apakah sudah berjalan
  if [ -f "$pid_file" ]; then
    local old_pid
    old_pid=$(cat "$pid_file")
    if kill -0 "$old_pid" 2>/dev/null; then
      echo "[INFO] Worker sudah berjalan (PID=$old_pid). Gunakan 'status' untuk cek."
      return 1
    else
      echo "[WARN] PID file ada tapi proses mati. Membersihkan..."
      rm -f "$pid_file"
    fi
  fi

  echo "[INFO] Memulai sync $type ${prov:+provinsi=$prov}..."

  if [ "$type" = "anggota" ]; then
    nohup "$PYTHON" -u "$BASEDIR/scripts/sync_worker.py" anggota "$prov" \
      >> "$log_file" 2>&1 &
  else
    nohup "$PYTHON" -u "$BASEDIR/scripts/sync_worker.py" keluarga \
      >> "$log_file" 2>&1 &
  fi

  local new_pid=$!
  echo "$new_pid" > "$pid_file"
  echo "[OK] Worker dimulai (PID=$new_pid)"
  echo "[OK] Log: $log_file"
}

cmd_stop() {
  local type=$1 prov=$2
  local pid_file
  pid_file=$(_pid_file "$type" "$prov")

  if [ ! -f "$pid_file" ]; then
    echo "[INFO] Tidak ada PID file. Worker mungkin tidak berjalan."
    return 0
  fi

  local pid
  pid=$(cat "$pid_file")

  if kill -0 "$pid" 2>/dev/null; then
    echo "[INFO] Mengirim SIGTERM ke PID=$pid (graceful stop)..."
    kill -TERM "$pid"
    sleep 3
    if kill -0 "$pid" 2>/dev/null; then
      echo "[WARN] Proses masih berjalan. Kirim SIGKILL..."
      kill -9 "$pid"
    fi
    echo "[OK] Worker dihentikan."
  else
    echo "[INFO] Proses PID=$pid tidak ditemukan (sudah mati)."
  fi

  rm -f "$pid_file"
}

cmd_status() {
  echo "========================================"
  echo " STATUS SYNC WORKER ZAWA"
  echo "========================================"

  # Cek semua PID file
  local found=0
  for pid_file in "$PID_DIR"/*.pid; do
    [ -f "$pid_file" ] || continue
    found=1
    local pid name
    pid=$(cat "$pid_file")
    name=$(basename "$pid_file" .pid)
    if kill -0 "$pid" 2>/dev/null; then
      echo "  ✅ RUNNING  | $name | PID=$pid"
    else
      echo "  ❌ STOPPED  | $name | PID=$pid (stale)"
    fi
  done

  [ $found -eq 0 ] && echo "  Tidak ada worker aktif."

  echo ""
  echo " Log files:"
  for log_file in "$LOG_DIR"/*.log; do
    [ -f "$log_file" ] || continue
    local size
    size=$(du -sh "$log_file" 2>/dev/null | cut -f1)
    echo "  📄 $log_file ($size)"
  done
  echo "========================================"
}

cmd_logs() {
  local type=$1 prov=$2
  local log_file
  log_file=$(_log_file "$type" "$prov")

  if [ ! -f "$log_file" ]; then
    echo "[INFO] Log file tidak ditemukan: $log_file"
    return 1
  fi

  echo "[INFO] Menampilkan log: $log_file"
  echo "--- Tekan Ctrl+C untuk berhenti ---"
  tail -f "$log_file"
}

cmd_resume() {
  local type=$1 prov=$2
  local cursor_file

  if [ "$type" = "anggota" ]; then
    cursor_file="$LOG_DIR/worker_anggota_${prov}.cursor"
  else
    cursor_file="$LOG_DIR/worker_keluarga.cursor"
  fi

  if [ -f "$cursor_file" ]; then
    echo "[INFO] Cursor ditemukan: $(cat $cursor_file)"
    echo "[INFO] Melanjutkan sync dari posisi terakhir..."
    cmd_start "$type" "$prov"
  else
    echo "[INFO] Tidak ada cursor tersimpan. Mulai dari awal."
    cmd_start "$type" "$prov"
  fi
}

# ─── Main ─────────────────────────────────────────────────────────────────────
case "$1" in
  start)  cmd_start  "$2" "$3" ;;
  stop)   cmd_stop   "$2" "$3" ;;
  status) cmd_status             ;;
  logs)   cmd_logs   "$2" "$3" ;;
  resume) cmd_resume "$2" "$3" ;;
  *)
    echo "Usage: $0 {start|stop|status|logs|resume} [anggota|keluarga] [provinsi]"
    echo ""
    echo "Contoh:"
    echo "  $0 start  anggota aceh"
    echo "  $0 start  keluarga"
    echo "  $0 status"
    echo "  $0 stop   anggota aceh"
    echo "  $0 logs   anggota aceh"
    echo "  $0 resume anggota aceh   # lanjut dari cursor terakhir"
    ;;
esac
