#!/usr/bin/env python3
"""
Standalone sync worker: ambil semua NKK dari zawa_anggota
yang belum ada di zawa_keluarga, fetch ke API ZAWA per-NKK,
lalu insert ke DB.

Environment variables yang dibutuhkan:
  DATABASE_URL   - MySQL connection string
  ZAWA_API_KEY   - API key ZAWA Kemenag
  BATCH_SIZE     - (opsional) jumlah NKK per run, default=0 (semua)
  SLEEP_BETWEEN  - (opsional) jeda antar request detik, default=0.1
"""

import os
import sys
import time
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Logging ────────────────────────────────────────────────────
log_dir = "/app/logs/sync"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"{log_dir}/keluarga_full.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("sync_keluarga")

# ── Config ─────────────────────────────────────────────────────
DATABASE_URL  = os.environ["DATABASE_URL"]
ZAWA_API_KEY  = os.environ.get("ZAWA_API_KEY", "")
ZAWA_BASE     = "https://spl-satudata.kemenag.go.id/core/api"
ZAWA_TIMEOUT  = 60
BATCH_SIZE    = int(os.environ.get("BATCH_SIZE", "0"))    # 0 = semua
SLEEP_BETWEEN = float(os.environ.get("SLEEP_BETWEEN", "0.1"))
LOG_EVERY     = int(os.environ.get("LOG_EVERY", "25"))    # progress setiap N NKK

if not ZAWA_API_KEY:
    logger.warning("ZAWA_API_KEY tidak di-set! Request ke API mungkin ditolak.")

# ── SQLAlchemy (standalone, tanpa Flask) ───────────────────────
from sqlalchemy import create_engine, text, distinct, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped
from sqlalchemy import String, Integer, Text, DateTime, Numeric, BigInteger
from datetime import datetime as dt
from decimal import Decimal, InvalidOperation

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def _s(val):
    if val is None: return None
    s = str(val).strip()
    return s if s else None

def _i(val):
    if val is None or str(val).strip() == '': return None
    try: return int(val)
    except: return None


class ZawaAnggota(Base):
    __tablename__ = "zawa_anggota"
    id                       = mapped_column(BigInteger, primary_key=True)
    nomor_kartu_keluarga     = mapped_column(String(20), nullable=True)
    nomor_induk_kependudukan = mapped_column(String(20), nullable=False)


class ZawaKeluarga(Base):
    __tablename__ = "zawa_keluarga"
    id                           = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nomor_kartu_keluarga         = mapped_column(String(20), unique=True, nullable=False, index=True)
    nama_anggota_keluarga        = mapped_column(String(255), nullable=True)
    jumlah_anggota_keluarga      = mapped_column(Integer, nullable=True)
    alamat                       = mapped_column(Text, nullable=True)
    kelurahan_desa               = mapped_column(String(100), nullable=True)
    kecamatan                    = mapped_column(String(100), nullable=True)
    kabupaten_kota               = mapped_column(String(100), nullable=True)
    provinsi                     = mapped_column(String(100), nullable=True)
    kode_kelurahan_desa          = mapped_column(String(15), nullable=True)
    kode_kecamatan               = mapped_column(String(10), nullable=True)
    kode_kabupaten_kota          = mapped_column(String(10), nullable=True)
    kode_provinsi                = mapped_column(String(10), nullable=True)
    luas_lantai                  = mapped_column(Integer, nullable=True)
    jenis_lantai_terluas         = mapped_column(Integer, nullable=True)
    jenis_dinding_terluas        = mapped_column(Integer, nullable=True)
    jenis_atap_terluas           = mapped_column(Integer, nullable=True)
    jenis_kloset                 = mapped_column(String(5), nullable=True)
    fasilitas_bab                = mapped_column(String(5), nullable=True)
    sumber_air_minum_utama       = mapped_column(Integer, nullable=True)
    sumber_penerangan_utama      = mapped_column(String(5), nullable=True)
    bahan_bakar_utama_memasak    = mapped_column(Integer, nullable=True)
    daya_terpasang               = mapped_column(Integer, nullable=True)
    pembuangan_akhir_tinja       = mapped_column(String(5), nullable=True)
    status_kepemilikan_rumah     = mapped_column(String(5), nullable=True)
    kepemilikan_aset             = mapped_column(String(5), nullable=True)
    aset_bergerak_sepeda_motor           = mapped_column(String(5), nullable=True)
    aset_bergerak_mobil                  = mapped_column(String(5), nullable=True)
    aset_bergerak_sepeda                 = mapped_column(String(5), nullable=True)
    aset_bergerak_perahu                 = mapped_column(String(5), nullable=True)
    aset_bergerak_kapal_perahu_motor     = mapped_column(String(5), nullable=True)
    aset_bergerak_smartphone             = mapped_column(String(5), nullable=True)
    aset_bergerak_komputer_laptop_tablet = mapped_column(String(5), nullable=True)
    aset_bergerak_lemari_es              = mapped_column(String(5), nullable=True)
    aset_bergerak_ac                     = mapped_column(String(5), nullable=True)
    aset_bergerak_tv_datar               = mapped_column(String(5), nullable=True)
    aset_bergerak_emas_perhiasan         = mapped_column(String(5), nullable=True)
    aset_bergerak_tabung_gas             = mapped_column(String(5), nullable=True)
    aset_bergerak_pemanas_air            = mapped_column(String(5), nullable=True)
    aset_bergerak_telepon_rumah          = mapped_column(String(5), nullable=True)
    aset_tidak_bergerak_rumah_lainnya    = mapped_column(String(5), nullable=True)
    aset_tidak_bergerak_lahan_lainnya    = mapped_column(String(5), nullable=True)
    jumlah_ternak_sapi          = mapped_column(Integer, nullable=True)
    jumlah_ternak_kerbau        = mapped_column(Integer, nullable=True)
    jumlah_ternak_kuda          = mapped_column(Integer, nullable=True)
    jumlah_ternak_kambing_domba = mapped_column(Integer, nullable=True)
    jumlah_ternak_babi          = mapped_column(Integer, nullable=True)
    pbi_nas                     = mapped_column(String(5), nullable=True)
    pbi_pemda                   = mapped_column(String(5), nullable=True)
    desil_nasional              = mapped_column(String(5), nullable=True)
    id_pelanggan_pln            = mapped_column(String(20), nullable=True)
    synced_at                   = mapped_column(DateTime, default=dt.utcnow)

    @classmethod
    def from_api(cls, item: dict):
        return cls(
            nomor_kartu_keluarga         = str(item.get("nomor_kartu_keluarga") or "").strip(),
            nama_anggota_keluarga        = _s(item.get("nama_anggota_keluarga")),
            jumlah_anggota_keluarga      = _i(item.get("jumlah_anggota_keluarga")),
            alamat                       = _s(item.get("alamat")),
            kelurahan_desa               = _s(item.get("kelurahan_desa")),
            kecamatan                    = _s(item.get("kecamatan")),
            kabupaten_kota               = _s(item.get("kabupaten_kota")),
            provinsi                     = _s(item.get("provinsi")),
            kode_kelurahan_desa          = _s(item.get("kode_kelurahan_desa")),
            kode_kecamatan               = _s(item.get("kode_kecamatan")),
            kode_kabupaten_kota          = _s(item.get("kode_kabupaten_kota")),
            kode_provinsi                = _s(item.get("kode_provinsi")),
            luas_lantai                  = _i(item.get("luas_lantai")),
            jenis_lantai_terluas         = _i(item.get("jenis_lantai_terluas")),
            jenis_dinding_terluas        = _i(item.get("jenis_dinding_terluas")),
            jenis_atap_terluas           = _i(item.get("jenis_atap_terluas")),
            jenis_kloset                 = _s(item.get("jenis_kloset")),
            fasilitas_bab                = _s(item.get("fasilitas_bab")),
            sumber_air_minum_utama       = _i(item.get("sumber_air_minum_utama")),
            sumber_penerangan_utama      = _s(item.get("sumber_penerangan_utama")),
            bahan_bakar_utama_memasak    = _i(item.get("bahan_bakar_utama_memasak")),
            daya_terpasang               = _i(item.get("daya_terpasang")),
            pembuangan_akhir_tinja       = _s(item.get("pembuangan_akhir_tinja")),
            status_kepemilikan_rumah     = _s(item.get("status_kepemilikan_rumah")),
            kepemilikan_aset             = _s(item.get("kepemilikan_aset")),
            aset_bergerak_sepeda_motor           = _s(item.get("aset_bergerak_sepeda_motor")),
            aset_bergerak_mobil                  = _s(item.get("aset_bergerak_mobil")),
            aset_bergerak_sepeda                 = _s(item.get("aset_bergerak_sepeda")),
            aset_bergerak_perahu                 = _s(item.get("aset_bergerak_perahu")),
            aset_bergerak_kapal_perahu_motor     = _s(item.get("aset_bergerak_kapal_perahu_motor")),
            aset_bergerak_smartphone             = _s(item.get("aset_bergerak_smartphone")),
            aset_bergerak_komputer_laptop_tablet = _s(item.get("aset_bergerak_komputer_laptop_tablet")),
            aset_bergerak_lemari_es              = _s(item.get("aset_bergerak_lemari_es")),
            aset_bergerak_ac                     = _s(item.get("aset_bergerak_ac")),
            aset_bergerak_tv_datar               = _s(item.get("aset_bergerak_tv_datar")),
            aset_bergerak_emas_perhiasan         = _s(item.get("aset_bergerak_emas_perhiasan")),
            aset_bergerak_tabung_gas             = _s(item.get("aset_bergerak_tabung_gas")),
            aset_bergerak_pemanas_air            = _s(item.get("aset_bergerak_pemanas_air")),
            aset_bergerak_telepon_rumah          = _s(item.get("aset_bergerak_telepon_rumah")),
            aset_tidak_bergerak_rumah_lainnya    = _s(item.get("aset_tidak_bergerak_rumah_lainnya")),
            aset_tidak_bergerak_lahan_lainnya    = _s(item.get("aset_tidak_bergerak_lahan_lainnya")),
            jumlah_ternak_sapi          = _i(item.get("jumlah_ternak_sapi")),
            jumlah_ternak_kerbau        = _i(item.get("jumlah_ternak_kerbau")),
            jumlah_ternak_kuda          = _i(item.get("jumlah_ternak_kuda")),
            jumlah_ternak_kambing_domba = _i(item.get("jumlah_ternak_kambing_domba")),
            jumlah_ternak_babi          = _i(item.get("jumlah_ternak_babi")),
            pbi_nas                     = _s(item.get("pbi_nas")),
            pbi_pemda                   = _s(item.get("pbi_pemda")),
            desil_nasional              = _s(item.get("desil_nasional")),
            id_pelanggan_pln            = _s(item.get("id_pelanggan_pln")),
        )


class ZawaSyncLog(Base):
    __tablename__ = "zawa_sync_log"
    id            = mapped_column(Integer, primary_key=True, autoincrement=True)
    sync_type     = mapped_column(String(50), nullable=False)
    provinsi_slug = mapped_column(String(20), nullable=True)
    status        = mapped_column(String(20), nullable=False, default="pending")
    total_fetched = mapped_column(Integer, nullable=True, default=0)
    total_saved   = mapped_column(Integer, nullable=True, default=0)
    total_skipped = mapped_column(Integer, nullable=True, default=0)
    total_error   = mapped_column(Integer, nullable=True, default=0)
    error_message = mapped_column(Text, nullable=True)
    started_at    = mapped_column(DateTime, nullable=False, default=dt.utcnow)
    finished_at   = mapped_column(DateTime, nullable=True)


# ── ZAWA fetch helper ──────────────────────────────────────────

def _zawa_headers():
    h = {"Accept": "application/json"}
    if ZAWA_API_KEY:
        h["x-api-key"] = ZAWA_API_KEY
    return h


def fetch_keluarga_by_nkk(nkk: str):
    """
    Fetch data keluarga dari API.
    Return: (item_dict | None, error_str | None, not_found_bool)
    """
    url = f"{ZAWA_BASE}/zawa/keluarga-by-nik"
    try:
        resp = requests.get(url, params={"nomor_kartu_keluarga": nkk},
                            timeout=ZAWA_TIMEOUT, headers=_zawa_headers())
        if resp.status_code == 404:
            return None, None, True
        resp.raise_for_status()
        raw = resp.json()
    except requests.exceptions.Timeout:
        return None, "Timeout", False
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else 0
        return None, f"HTTP {status}", False
    except Exception as e:
        return None, str(e), False

    data = raw.get("data")
    if isinstance(data, dict) and data:
        non_meta_keys = {k for k in data if k not in (
            "items", "data", "limit", "currentPage", "totalItems",
            "totalPages", "hasNextPage", "hasPreviousPage", "nextCursor"
        )}
        if non_meta_keys:
            return data, None, False
        items = data.get("items") or []
        return items[0] if items else None, None, not bool(items)
    return None, "Empty response", False


# ── Main sync logic ────────────────────────────────────────────

def main():
    logger.info("=" * 60)
    logger.info("SYNC KELUARGA FULL — START")
    logger.info(f"DATABASE : {DATABASE_URL.split('@')[-1]}")
    logger.info(f"BATCH    : {'semua' if BATCH_SIZE == 0 else BATCH_SIZE}")
    logger.info(f"SLEEP    : {SLEEP_BETWEEN}s")
    logger.info("=" * 60)

    session = Session()
    started = dt.utcnow()

    sync_log = ZawaSyncLog(
        sync_type="keluarga_full",
        provinsi_slug=None,
        status="running",
        started_at=started,
    )
    session.add(sync_log)
    session.commit()

    try:
        existing_set = set(
            row[0] for row in session.execute(
                select(ZawaKeluarga.nomor_kartu_keluarga)
            ).fetchall()
        )

        all_nkk = [
            row[0] for row in session.execute(
                select(distinct(ZawaAnggota.nomor_kartu_keluarga))
                .where(
                    ZawaAnggota.nomor_kartu_keluarga.isnot(None),
                    ZawaAnggota.nomor_kartu_keluarga != ''
                )
            ).fetchall()
        ]

        pending = [nkk for nkk in all_nkk if nkk not in existing_set]
        if BATCH_SIZE > 0:
            pending = pending[:BATCH_SIZE]

        total = len(pending)
        logger.info(f"Total NKK di zawa_anggota : {len(all_nkk)}")
        logger.info(f"Sudah ada di zawa_keluarga: {len(existing_set)}")
        logger.info(f"Akan di-fetch             : {total}")

        saved = skipped = error = 0

        for i, nkk in enumerate(pending, 1):
            item, err, not_found = fetch_keluarga_by_nkk(nkk)

            if not_found:
                skipped += 1
            elif err:
                logger.warning(f"[{i}/{total}] ERR NKK={nkk}: {err}")
                error += 1
            elif item:
                nkk_str = str(item.get("nomor_kartu_keluarga") or "").strip()
                exists = session.execute(
                    select(ZawaKeluarga.id).where(
                        ZawaKeluarga.nomor_kartu_keluarga == nkk_str
                    )
                ).first()
                if exists:
                    skipped += 1
                else:
                    try:
                        obj = ZawaKeluarga.from_api(item)
                        session.add(obj)
                        session.commit()
                        saved += 1
                    except Exception as e:
                        session.rollback()
                        logger.warning(f"[{i}/{total}] INSERT ERR NKK={nkk}: {e}")
                        error += 1
            else:
                skipped += 1

            if i % LOG_EVERY == 0 or i == total:
                elapsed = round((dt.utcnow() - started).total_seconds())
                remaining = total - i
                avg = elapsed / i if i > 0 else 0
                eta = round(avg * remaining)
                logger.info(
                    f"[{i}/{total}] saved={saved} skipped={skipped} error={error} "
                    f"| elapsed={elapsed}s ETA={eta}s"
                )

            time.sleep(SLEEP_BETWEEN)

        sync_log.status        = "success" if error == 0 or saved > 0 else "failed"
        sync_log.total_fetched = saved + error
        sync_log.total_saved   = saved
        sync_log.total_skipped = skipped
        sync_log.total_error   = error
        sync_log.finished_at   = dt.utcnow()
        session.commit()

        duration = round((sync_log.finished_at - started).total_seconds())
        logger.info("=" * 60)
        logger.info(f"SELESAI  saved={saved}  skipped={skipped}  error={error}")
        logger.info(f"Durasi   : {duration} detik ({round(duration/60, 1)} menit)")
        logger.info("=" * 60)

    except Exception as e:
        session.rollback()
        sync_log.status        = "failed"
        sync_log.error_message = str(e)[:1000]
        sync_log.finished_at   = dt.utcnow()
        session.commit()
        logger.error(f"FATAL ERROR: {e}")
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
