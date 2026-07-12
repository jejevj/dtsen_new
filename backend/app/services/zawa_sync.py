import threading
import logging
import os
import time
from datetime import datetime
from flask import current_app
from app.extensions import db
from app.models.zawa import ZawaAnggota, ZawaKeluarga, ZawaSyncLog
import requests

# ─── Konstanta ───────────────────────────────────────────────────────────────
ZAWA_BASE_URL  = "https://spl-satudata.kemenag.go.id/core/api/zawa"
ZAWA_API_KEY   = os.getenv("ZAWA_API_KEY", "prod-53a81004-085d-426b-a5a0-c6ef6cdf18e1")
ZAWA_PAGE_SIZE = 100   # items per request ke ZAWA
MAX_ANGGOTA_PER_PROVINSI = 10_000
MAX_KELUARGA_TOTAL       = 50_000
RETRY_MAX   = 3        # retry per page jika gagal
RETRY_DELAY = 5        # detik antar retry

# ─── State tracker (in-memory) ───────────────────────────────────────────────
_running_jobs: dict[str, bool] = {}
_jobs_lock = threading.Lock()

# ─── Logger setup ─────────────────────────────────────────────────────────────
def get_sync_logger(job_id: str) -> logging.Logger:
    """Buat logger per job dengan file handler di logs/sync/"""
    log_dir = os.path.join(os.getcwd(), "logs", "sync")
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(f"zawa_sync.{job_id}")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # File handler – log lengkap
        fh = logging.FileHandler(
            os.path.join(log_dir, f"{job_id}.log"), encoding="utf-8"
        )
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(fh)

        # Stream handler – tampil di stdout Flask
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        sh.setFormatter(logging.Formatter("[SYNC %(name)s] %(message)s"))
        logger.addHandler(sh)

    return logger


# ─── Helpers ──────────────────────────────────────────────────────────────────
def _headers() -> dict:
    return {"x-api-key": ZAWA_API_KEY, "Accept": "application/json"}


def _fetch_page(url: str, params: dict, logger: logging.Logger) -> dict | None:
    """Fetch 1 halaman dengan retry logic. Return None jika semua retry gagal."""
    for attempt in range(1, RETRY_MAX + 1):
        try:
            resp = requests.get(url, headers=_headers(), params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if data.get("success"):
                return data["data"]
            logger.warning(f"API response success=false | attempt={attempt}")
        except Exception as exc:
            logger.warning(f"Fetch error attempt={attempt}/{RETRY_MAX}: {exc}")
            if attempt < RETRY_MAX:
                time.sleep(RETRY_DELAY * attempt)  # exponential backoff
    return None


def _save_cursor(job_id: str, cursor: str | None):
    """Simpan cursor ke file agar bisa resume jika proses mati."""
    cursor_dir = os.path.join(os.getcwd(), "logs", "sync")
    os.makedirs(cursor_dir, exist_ok=True)
    path = os.path.join(cursor_dir, f"{job_id}.cursor")
    with open(path, "w") as f:
        f.write(cursor or "")


def _load_cursor(job_id: str) -> str | None:
    """Muat cursor dari file jika ada (untuk resume)."""
    path = os.path.join(os.getcwd(), "logs", "sync", f"{job_id}.cursor")
    if os.path.exists(path):
        with open(path) as f:
            val = f.read().strip()
            return val if val else None
    return None


def _clear_cursor(job_id: str):
    path = os.path.join(os.getcwd(), "logs", "sync", f"{job_id}.cursor")
    if os.path.exists(path):
        os.remove(path)


# ─── Core sync functions ──────────────────────────────────────────────────────
def _sync_anggota_provinsi(app, provinsi: str, sync_log_id: int):
    """Sync anggota untuk 1 provinsi. Dipanggil di thread terpisah."""
    job_id = f"anggota_{provinsi}_{sync_log_id}"
    logger = get_sync_logger(job_id)
    logger.info(f"=== MULAI sync anggota provinsi={provinsi} ===")

    total_saved  = 0
    total_fetched = 0
    cursor = _load_cursor(job_id)  # resume dari cursor jika ada

    if cursor:
        logger.info(f"Resume dari cursor: {cursor}")

    with app.app_context():
        sync_log = db.session.get(ZawaSyncLog, sync_log_id)
        sync_log.status = "running"
        db.session.commit()

        try:
            while True:
                if total_fetched >= MAX_ANGGOTA_PER_PROVINSI:
                    logger.info(f"Batas {MAX_ANGGOTA_PER_PROVINSI} baris tercapai.")
                    break

                params = {
                    "provinsi": provinsi,
                    "limit": ZAWA_PAGE_SIZE,
                }
                if cursor:
                    params["cursor"] = cursor

                page_data = _fetch_page(
                    f"{ZAWA_BASE_URL}/anggota", params, logger
                )

                if page_data is None:
                    raise RuntimeError(f"Gagal fetch halaman setelah {RETRY_MAX} retry")

                items = page_data.get("items", [])
                if not items:
                    break

                # Bulk upsert per batch
                rows = []
                for item in items:
                    rows.append(ZawaAnggota.from_api(item, provinsi))

                # Upsert: insert ignore untuk duplikat NIK
                for row in rows:
                    existing = ZawaAnggota.query.filter_by(
                        nomor_induk_kependudukan=str(row.nomor_induk_kependudukan)
                    ).first()
                    if not existing:
                        db.session.add(row)

                db.session.commit()

                batch_count = len(items)
                total_fetched += batch_count
                total_saved   += batch_count

                cursor = page_data.get("nextCursor")
                _save_cursor(job_id, cursor)

                logger.info(
                    f"Page OK | fetched={batch_count} | "
                    f"total={total_fetched}/{MAX_ANGGOTA_PER_PROVINSI} | "
                    f"nextCursor={cursor}"
                )

                if not page_data.get("hasNextPage") or not cursor:
                    logger.info("Tidak ada halaman berikutnya. Selesai.")
                    break

            # Selesai sukses
            sync_log.status        = "success"
            sync_log.total_fetched = total_fetched
            sync_log.total_saved   = total_saved
            sync_log.finished_at   = datetime.utcnow()
            db.session.commit()
            _clear_cursor(job_id)
            logger.info(f"=== SELESAI sukses. total_saved={total_saved} ===")

        except Exception as exc:
            db.session.rollback()
            sync_log.status        = "failed"
            sync_log.error_message = str(exc)[:1000]
            sync_log.total_fetched = total_fetched
            sync_log.total_saved   = total_saved
            sync_log.finished_at   = datetime.utcnow()
            db.session.commit()
            logger.error(f"=== ERROR: {exc} ===")
            logger.info(f"Cursor tersimpan di job_id={job_id} untuk resume.")

        finally:
            with _jobs_lock:
                _running_jobs.pop(job_id, None)


def _sync_keluarga(app, sync_log_id: int):
    """Sync keluarga global. Dipanggil di thread terpisah."""
    job_id = f"keluarga_{sync_log_id}"
    logger = get_sync_logger(job_id)
    logger.info("=== MULAI sync keluarga ===")

    total_saved   = 0
    total_fetched = 0
    cursor = _load_cursor(job_id)

    if cursor:
        logger.info(f"Resume dari cursor: {cursor}")

    with app.app_context():
        sync_log = db.session.get(ZawaSyncLog, sync_log_id)
        sync_log.status = "running"
        db.session.commit()

        try:
            while True:
                if total_fetched >= MAX_KELUARGA_TOTAL:
                    logger.info(f"Batas {MAX_KELUARGA_TOTAL} baris tercapai.")
                    break

                params = {"limit": ZAWA_PAGE_SIZE}
                if cursor:
                    params["cursor"] = cursor

                page_data = _fetch_page(
                    f"{ZAWA_BASE_URL}/keluarga", params, logger
                )

                if page_data is None:
                    raise RuntimeError(f"Gagal fetch halaman setelah {RETRY_MAX} retry")

                items = page_data.get("items", [])
                if not items:
                    break

                for item in items:
                    existing = ZawaKeluarga.query.filter_by(
                        nomor_kartu_keluarga=str(item.get("nomor_kartu_keluarga"))
                    ).first()
                    if not existing:
                        db.session.add(ZawaKeluarga.from_api(item))

                db.session.commit()

                batch_count    = len(items)
                total_fetched += batch_count
                total_saved   += batch_count

                cursor = page_data.get("nextCursor")
                _save_cursor(job_id, cursor)

                logger.info(
                    f"Page OK | fetched={batch_count} | "
                    f"total={total_fetched}/{MAX_KELUARGA_TOTAL} | "
                    f"nextCursor={cursor}"
                )

                if not page_data.get("hasNextPage") or not cursor:
                    logger.info("Tidak ada halaman berikutnya. Selesai.")
                    break

            sync_log.status        = "success"
            sync_log.total_fetched = total_fetched
            sync_log.total_saved   = total_saved
            sync_log.finished_at   = datetime.utcnow()
            db.session.commit()
            _clear_cursor(job_id)
            logger.info(f"=== SELESAI sukses. total_saved={total_saved} ===")

        except Exception as exc:
            db.session.rollback()
            sync_log.status        = "failed"
            sync_log.error_message = str(exc)[:1000]
            sync_log.total_fetched = total_fetched
            sync_log.total_saved   = total_saved
            sync_log.finished_at   = datetime.utcnow()
            db.session.commit()
            logger.error(f"=== ERROR: {exc} ===")

        finally:
            with _jobs_lock:
                _running_jobs.pop(job_id, None)


# ─── Public API ───────────────────────────────────────────────────────────────
def start_sync_anggota(app, provinsi: str) -> dict:
    """Mulai background sync anggota untuk 1 provinsi. Return job info."""
    job_key = f"anggota_{provinsi}"

    with _jobs_lock:
        if _running_jobs.get(job_key):
            return {"status": "already_running", "job_key": job_key}
        _running_jobs[job_key] = True

    with app.app_context():
        log = ZawaSyncLog(
            sync_type=f"anggota_{provinsi}",
            status="pending",
        )
        db.session.add(log)
        db.session.commit()
        log_id = log.id

    t = threading.Thread(
        target=_sync_anggota_provinsi,
        args=(app, provinsi, log_id),
        daemon=True,
        name=f"sync-anggota-{provinsi}"
    )
    t.start()

    return {
        "status": "started",
        "job_key": job_key,
        "sync_log_id": log_id,
        "log_file": f"logs/sync/anggota_{provinsi}_{log_id}.log"
    }


def start_sync_keluarga(app) -> dict:
    """Mulai background sync keluarga global. Return job info."""
    job_key = "keluarga"

    with _jobs_lock:
        if _running_jobs.get(job_key):
            return {"status": "already_running", "job_key": job_key}
        _running_jobs[job_key] = True

    with app.app_context():
        log = ZawaSyncLog(
            sync_type="keluarga",
            status="pending",
        )
        db.session.add(log)
        db.session.commit()
        log_id = log.id

    t = threading.Thread(
        target=_sync_keluarga,
        args=(app, log_id),
        daemon=True,
        name="sync-keluarga"
    )
    t.start()

    return {
        "status": "started",
        "job_key": job_key,
        "sync_log_id": log_id,
        "log_file": f"logs/sync/keluarga_{log_id}.log"
    }


def get_running_jobs() -> list:
    with _jobs_lock:
        return list(_running_jobs.keys())
