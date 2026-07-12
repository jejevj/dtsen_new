#!/usr/bin/env python3
"""
Detached sync worker — jalankan di luar Flask untuk full background sync.

Cara pakai:
  # Sync anggota provinsi Aceh (detach, log ke file)
  nohup python scripts/sync_worker.py anggota aceh >> logs/sync/worker.log 2>&1 &
  echo $! > logs/sync/worker.pid

  # Sync keluarga
  nohup python scripts/sync_worker.py keluarga >> logs/sync/worker_keluarga.log 2>&1 &
  echo $! > logs/sync/worker_keluarga.pid

  # Cek apakah masih berjalan
  kill -0 $(cat logs/sync/worker.pid) && echo 'RUNNING' || echo 'STOPPED'

  # Stop manual
  kill $(cat logs/sync/worker.pid)
"""

import sys
import os
import logging
import time
import signal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from app.extensions import db
from app.models.zawa import ZawaAnggota, ZawaKeluarga, ZawaSyncLog
from app.services.zawa_sync import (
    _fetch_page, _save_cursor, _load_cursor, _clear_cursor,
    ZAWA_BASE_URL, ZAWA_PAGE_SIZE,
    MAX_ANGGOTA_PER_PROVINSI, MAX_KELUARGA_TOTAL,
)
from datetime import datetime

# ─── Setup logging ────────────────────────────────────────────────────
log_dir = os.path.join(os.getcwd(), "logs", "sync")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("sync_worker")

# ─── Graceful shutdown ──────────────────────────────────────────────────
_stop = False

def _handle_signal(sig, frame):
    global _stop
    logger.warning(f"Signal {sig} diterima. Menghentikan setelah batch ini...")
    _stop = True

signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)


# ─── Worker functions ──────────────────────────────────────────────────
def run_sync_anggota(app, provinsi: str):
    job_id = f"worker_anggota_{provinsi}"
    logger.info(f"=== WORKER START: sync anggota provinsi={provinsi} ===")

    fh = logging.FileHandler(
        os.path.join(log_dir, f"{job_id}.log"), encoding="utf-8"
    )
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)

    total_fetched = 0
    total_saved = 0
    cursor = _load_cursor(job_id)
    if cursor:
        logger.info(f"Resume dari cursor: {cursor}")

    with app.app_context():
        sync_log = ZawaSyncLog(
            sync_type=f"anggota_{provinsi}",
            status="running",
        )
        db.session.add(sync_log)
        db.session.commit()

        try:
            while not _stop:
                if total_fetched >= MAX_ANGGOTA_PER_PROVINSI:
                    logger.info(f"Batas {MAX_ANGGOTA_PER_PROVINSI} tercapai.")
                    break

                params = {"provinsi": provinsi, "limit": ZAWA_PAGE_SIZE}
                if cursor:
                    params["cursor"] = cursor

                page_data = _fetch_page(f"{ZAWA_BASE_URL}/anggota", params, logger)

                if page_data is None:
                    raise RuntimeError("Gagal fetch halaman setelah semua retry.")

                items = page_data.get("items", [])
                if not items:
                    logger.info("Items kosong. Selesai.")
                    break

                batch_saved = 0
                for item in items:
                    nik = str(item.get("nomor_induk_kependudukan") or "")
                    if nik and not ZawaAnggota.query.filter_by(nomor_induk_kependudukan=nik).first():
                        db.session.add(ZawaAnggota.from_api(item, provinsi))
                        batch_saved += 1

                db.session.commit()

                batch_fetched = len(items)
                total_fetched += batch_fetched
                total_saved += batch_saved

                # ✔ FIX: Cek apakah cursor berubah — jika sama, stop untuk hindari infinite loop
                new_cursor = page_data.get("nextCursor") or page_data.get("next_cursor")
                if new_cursor and new_cursor == cursor:
                    logger.warning(
                        f"Cursor tidak berubah ({new_cursor}). "
                        "API mungkin stuck. Menghentikan untuk mencegah infinite loop."
                    )
                    break

                cursor = new_cursor
                _save_cursor(job_id, cursor)

                logger.info(
                    f"Page OK | fetched={batch_fetched} saved={batch_saved} | "
                    f"total_fetched={total_fetched} total_saved={total_saved} | "
                    f"cursor={cursor}"
                )

                if not page_data.get("hasNextPage") or not cursor:
                    logger.info("Tidak ada halaman berikutnya. Selesai.")
                    break

                time.sleep(0.1)

            status = "stopped" if _stop else "success"
            sync_log.status = status
            sync_log.total_fetched = total_fetched
            sync_log.total_saved = total_saved
            sync_log.finished_at = datetime.utcnow()
            db.session.commit()

            if not _stop:
                _clear_cursor(job_id)
            logger.info(f"=== WORKER SELESAI status={status} total_saved={total_saved} ===")

        except Exception as exc:
            db.session.rollback()
            sync_log.status = "failed"
            sync_log.error_message = str(exc)[:1000]
            sync_log.total_fetched = total_fetched
            sync_log.total_saved = total_saved
            sync_log.finished_at = datetime.utcnow()
            db.session.commit()
            logger.error(f"=== WORKER ERROR: {exc} ===")
            logger.info("Cursor disimpan. Jalankan ulang untuk resume.")
            sys.exit(1)


def run_sync_keluarga(app):
    job_id = "worker_keluarga"
    logger.info("=== WORKER START: sync keluarga ===")

    fh = logging.FileHandler(
        os.path.join(log_dir, f"{job_id}.log"), encoding="utf-8"
    )
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)

    total_fetched = 0
    total_saved = 0
    cursor = _load_cursor(job_id)
    if cursor:
        logger.info(f"Resume dari cursor: {cursor}")

    with app.app_context():
        sync_log = ZawaSyncLog(sync_type="keluarga", status="running")
        db.session.add(sync_log)
        db.session.commit()

        try:
            while not _stop:
                if total_fetched >= MAX_KELUARGA_TOTAL:
                    logger.info(f"Batas {MAX_KELUARGA_TOTAL} tercapai.")
                    break

                params = {"limit": ZAWA_PAGE_SIZE}
                if cursor:
                    params["cursor"] = cursor

                page_data = _fetch_page(f"{ZAWA_BASE_URL}/keluarga", params, logger)

                if page_data is None:
                    raise RuntimeError("Gagal fetch halaman setelah semua retry.")

                items = page_data.get("items", [])
                if not items:
                    logger.info("Items kosong. Selesai.")
                    break

                batch_saved = 0
                for item in items:
                    nkk = str(item.get("nomor_kartu_keluarga") or "")
                    if nkk and not ZawaKeluarga.query.filter_by(nomor_kartu_keluarga=nkk).first():
                        db.session.add(ZawaKeluarga.from_api(item))
                        batch_saved += 1

                db.session.commit()

                batch_fetched = len(items)
                total_fetched += batch_fetched
                total_saved += batch_saved

                # ✔ FIX: Cek apakah cursor berubah — jika sama, stop untuk hindari infinite loop
                new_cursor = page_data.get("nextCursor") or page_data.get("next_cursor")
                if new_cursor and new_cursor == cursor:
                    logger.warning(
                        f"Cursor tidak berubah ({new_cursor}). "
                        "API mungkin stuck. Menghentikan untuk mencegah infinite loop."
                    )
                    break

                cursor = new_cursor
                _save_cursor(job_id, cursor)

                logger.info(
                    f"Page OK | fetched={batch_fetched} saved={batch_saved} | "
                    f"total_fetched={total_fetched} total_saved={total_saved} | "
                    f"cursor={cursor}"
                )

                if not page_data.get("hasNextPage") or not cursor:
                    logger.info("Tidak ada halaman berikutnya. Selesai.")
                    break

                time.sleep(0.1)

            status = "stopped" if _stop else "success"
            sync_log.status = status
            sync_log.total_fetched = total_fetched
            sync_log.total_saved = total_saved
            sync_log.finished_at = datetime.utcnow()
            db.session.commit()

            if not _stop:
                _clear_cursor(job_id)
            logger.info(f"=== WORKER SELESAI status={status} total_saved={total_saved} ===")

        except Exception as exc:
            db.session.rollback()
            sync_log.status = "failed"
            sync_log.error_message = str(exc)[:1000]
            sync_log.total_fetched = total_fetched
            sync_log.total_saved = total_saved
            sync_log.finished_at = datetime.utcnow()
            db.session.commit()
            logger.error(f"=== WORKER ERROR: {exc} ===")
            sys.exit(1)


# ─── Entry point ─────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/sync_worker.py anggota <provinsi>")
        print("  python scripts/sync_worker.py keluarga")
        sys.exit(1)

    sync_type = sys.argv[1].lower()
    app = create_app()

    if sync_type == "anggota":
        if len(sys.argv) < 3:
            print("Error: provinsi wajib untuk sync anggota")
            sys.exit(1)
        run_sync_anggota(app, sys.argv[2].lower())

    elif sync_type == "keluarga":
        run_sync_keluarga(app)

    else:
        print(f"Sync type tidak dikenal: {sync_type}")
        sys.exit(1)
