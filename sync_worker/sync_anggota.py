#!/usr/bin/env python3
"""
Standalone sync worker: fetch data anggota dari ZAWA API per provinsi
lalu insert ke tabel zawa_anggota.

Provinsi di-ambil dari tampilan-filter.json (semua path zawa/<slug>)
kecuali Aceh (slug: anggota) dan endpoint non-provinsi lainnya.

Batas per provinsi: LIMIT_PER_PROVINSI data (default=100).
API mengembalikan array langsung (bukan cursor/pagination).

Environment variables yang dibutuhkan:
  DATABASE_URL          - MySQL connection string
  ZAWA_API_KEY          - API key ZAWA Kemenag
  LIMIT_PER_PROVINSI    - (opsional) max data per provinsi, default=100 (0=semua)
  SLEEP_BETWEEN         - (opsional) jeda antar provinsi detik, default=0.3
  PROVINSI              - (opsional) jalankan untuk 1 provinsi saja, misal: jambi
"""

import os
import sys
import time
import logging
import requests
from datetime import datetime as dt
from dotenv import load_dotenv

load_dotenv()

# ─── Logging ───────────────────────────────────────────────────
log_dir = "/app/logs/sync"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"{log_dir}/anggota.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("sync_anggota")

# ─── Config ────────────────────────────────────────────────────
DATABASE_URL       = os.environ["DATABASE_URL"]
ZAWA_API_KEY       = os.environ.get("ZAWA_API_KEY", "")
ZAWA_BASE          = "https://spl-satudata.kemenag.go.id/core/api"
ZAWA_TIMEOUT       = 60
LIMIT_PER_PROVINSI = int(os.environ.get("LIMIT_PER_PROVINSI", "100"))  # 0 = semua data
SLEEP_BETWEEN      = float(os.environ.get("SLEEP_BETWEEN", "0.3"))
ONLY_PROVINSI      = os.environ.get("PROVINSI", "").strip().lower()

if not ZAWA_API_KEY:
    logger.warning("ZAWA_API_KEY tidak di-set! Request ke API mungkin ditolak.")

# ─── Daftar provinsi (dari tampilan-filter.json, skip Aceh) ───
PROVINSI_LIST = {
    "jambi":      "Jambi",
    "sumbar":     "Sumatera Barat",
    "riau":       "Riau",
    "sumut":      "Sumatera Utara",
    "kepriau":    "Kepulauan Riau",
    "babel":      "Bangka Belitung",
    "lampung":    "Lampung",
    "bengkulu":   "Bengkulu",
    "sumsel":     "Sumatera Selatan",
    "dkijakarta": "DKI Jakarta",
    "jabar":      "Jawa Barat",
    "jateng":     "Jawa Tengah",
    "diy":        "DI Yogyakarta",
    "jatim":      "Jawa Timur",
    "banten":     "Banten",
    "bali":       "Bali",
    "ntb":        "Nusa Tenggara Barat",
    "ntt":        "Nusa Tenggara Timur",
    "kalbar":     "Kalimantan Barat",
    "kalteng":    "Kalimantan Tengah",
    "kalsel":     "Kalimantan Selatan",
    "kaltim":     "Kalimantan Timur",
    "kaltara":    "Kalimantan Utara",
    "sulut":      "Sulawesi Utara",
    "sulteng":    "Sulawesi Tengah",
    "sulsel":     "Sulawesi Selatan",
    "sultra":     "Sulawesi Tenggara",
    "gorontalo":  "Gorontalo",
    "sulbar":     "Sulawesi Barat",
    "maluku":     "Maluku",
    "malut":      "Maluku Utara",
    "papbar":     "Papua Barat",
    "papua":      "Papua",
    "papsel":     "Papua Selatan",
    "papteng":    "Papua Tengah",
    "papgu":      "Papua Pegunungan",
    "papdy":      "Papua Barat Daya",
}

# BPS kode -> slug (untuk auto-repair provinsi_slug dari kode KTP)
BPS_MAP = {
    "jambi":      "15", "sumbar":     "13", "riau":       "14", "sumut":      "12",
    "kepriau":    "21", "babel":      "19", "lampung":    "18", "bengkulu":   "17",
    "sumsel":     "16", "dkijakarta": "31", "jabar":      "32", "jateng":     "33",
    "diy":        "34", "jatim":      "35", "banten":     "36", "bali":       "51",
    "ntb":        "52", "ntt":        "53", "kalbar":     "61", "kalteng":    "62",
    "kalsel":     "63", "kaltim":     "64", "kaltara":    "65", "sulut":      "71",
    "sulteng":    "72", "sulsel":     "73", "sultra":     "74", "gorontalo":  "75",
    "sulbar":     "76", "maluku":     "81", "malut":      "82", "papbar":     "91",
    "papua":      "94", "papsel":     "95", "papteng":    "96", "papgu":      "97",
    "papdy":      "92",
}
_BPS_TO_SLUG = {v: k for k, v in BPS_MAP.items()}

# ─── SQLAlchemy standalone ─────────────────────────────────────
from sqlalchemy import (
    create_engine, select, String, Integer, Text, DateTime,
    Numeric, BigInteger,
)
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column
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

def _d(val):
    if val is None or str(val).strip() == '': return None
    try: return Decimal(str(val))
    except InvalidOperation: return None


class ZawaAnggota(Base):
    __tablename__ = "zawa_anggota"

    id                                                 = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nomor_induk_kependudukan                           = mapped_column(String(20),  unique=True, nullable=False, index=True)
    nomor_kartu_keluarga                               = mapped_column(String(20),  nullable=True, index=True)
    nama                                               = mapped_column(String(255), nullable=True)
    jenis_kelamin                                      = mapped_column(String(2),   nullable=True)
    tanggal_lahir                                      = mapped_column(String(30),  nullable=True)
    status_kawin                                       = mapped_column(String(5),   nullable=True)
    status_hubungan_keluarga                           = mapped_column(String(5),   nullable=True)
    alamat_ktp                                         = mapped_column(Text,        nullable=True)
    dusun_ktp                                          = mapped_column(String(100), nullable=True)
    rt_ktp                                             = mapped_column(Integer,     nullable=True)
    rw_ktp                                             = mapped_column(Integer,     nullable=True)
    kelurahan_desa_ktp                                 = mapped_column(String(100), nullable=True)
    kecamatan_ktp                                      = mapped_column(String(100), nullable=True)
    kabupaten_kota_ktp                                 = mapped_column(String(100), nullable=True)
    provinsi_ktp                                       = mapped_column(String(100), nullable=True)
    kode_kelurahan_desa_ktp                            = mapped_column(String(15),  nullable=True)
    kode_kecamatan_ktp                                 = mapped_column(String(10),  nullable=True)
    kode_kabupaten_kota_ktp                            = mapped_column(String(10),  nullable=True)
    kode_provinsi_ktp                                  = mapped_column(String(10),  nullable=True)
    partisipasi_sekolah                                = mapped_column(String(5),   nullable=True)
    jenjang_tertinggi_yang_diduduki                    = mapped_column(Integer,     nullable=True)
    kelas_tertinggi_yang_diduduki                      = mapped_column(Integer,     nullable=True)
    ijazah_tertinggi_yang_dimiliki                     = mapped_column(Integer,     nullable=True)
    status_bekerja                                     = mapped_column(String(5),   nullable=True)
    status_dalam_pekerjaan_utama                       = mapped_column(String(5),   nullable=True)
    lapangan_usaha_dari_pekerjaan_utama                = mapped_column(Integer,     nullable=True)
    lapangan_usaha_dari_usaha_utama                    = mapped_column(Integer,     nullable=True)
    kepemilikan_usaha                                  = mapped_column(String(5),   nullable=True)
    jumlah_usaha                                       = mapped_column(Integer,     nullable=True)
    omzet_usaha_utama                                  = mapped_column(Numeric(15, 2), nullable=True)
    jumlah_pekerja_yang_dibayar_dari_usaha_utama       = mapped_column(Integer,     nullable=True)
    jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama = mapped_column(Integer,     nullable=True)
    penglihatan                                        = mapped_column(String(5),   nullable=True)
    pendengaran                                        = mapped_column(String(5),   nullable=True)
    berjalan_atau_naik_tangga                          = mapped_column(String(5),   nullable=True)
    menggunakan_tangan_jari                            = mapped_column(String(5),   nullable=True)
    mengingat_berkonsentrasi                           = mapped_column(String(5),   nullable=True)
    mengurus_diri                                      = mapped_column(String(5),   nullable=True)
    berbicara_komunikasi                               = mapped_column(String(5),   nullable=True)
    belajar_kemampuan_intelektual                      = mapped_column(String(5),   nullable=True)
    pengendalian_perilaku                              = mapped_column(String(5),   nullable=True)
    kesedihan_depresi                                  = mapped_column(String(5),   nullable=True)
    kondisi_gizi                                       = mapped_column(String(5),   nullable=True)
    penyakit_kronis                                    = mapped_column(Integer,     nullable=True)
    pbi_nas                                            = mapped_column(String(5),   nullable=True)
    pbi_pemda                                          = mapped_column(String(5),   nullable=True)
    id_pelanggan_pln                                   = mapped_column(String(20),  nullable=True)
    provinsi_slug                                      = mapped_column(String(20),  nullable=True, index=True)
    synced_at                                          = mapped_column(DateTime,    default=dt.utcnow)

    @classmethod
    def from_api(cls, item: dict, provinsi_slug: str):
        raw_tgl = item.get("tanggal_lahir") or ""
        tgl = str(raw_tgl).strip()[:10] if raw_tgl else None
        return cls(
            nomor_induk_kependudukan                           = str(item.get("nomor_induk_kependudukan") or ""),
            nomor_kartu_keluarga                               = _s(item.get("nomor_kartu_keluarga")),
            nama                                               = _s(item.get("nama")),
            jenis_kelamin                                      = _s(item.get("jenis_kelamin")),
            tanggal_lahir                                      = tgl,
            status_kawin                                       = _s(item.get("status_kawin")),
            status_hubungan_keluarga                           = _s(item.get("status_hubungan_keluarga")),
            alamat_ktp                                         = _s(item.get("alamat_ktp")),
            dusun_ktp                                          = _s(item.get("dusun_ktp")),
            rt_ktp                                             = _i(item.get("rt_ktp")),
            rw_ktp                                             = _i(item.get("rw_ktp")),
            kelurahan_desa_ktp                                 = _s(item.get("kelurahan_desa_ktp")),
            kecamatan_ktp                                      = _s(item.get("kecamatan_ktp")),
            kabupaten_kota_ktp                                 = _s(item.get("kabupaten_kota_ktp")),
            provinsi_ktp                                       = _s(item.get("provinsi_ktp")),
            kode_kelurahan_desa_ktp                            = _s(item.get("kode_kelurahan_desa_ktp")),
            kode_kecamatan_ktp                                 = _s(item.get("kode_kecamatan_ktp")),
            kode_kabupaten_kota_ktp                            = _s(item.get("kode_kabupaten_kota_ktp")),
            kode_provinsi_ktp                                  = _s(item.get("kode_provinsi_ktp")),
            partisipasi_sekolah                                = _s(item.get("partisipasi_sekolah")),
            jenjang_tertinggi_yang_diduduki                    = _i(item.get("jenjang_tertinggi_yang_diduduki")),
            kelas_tertinggi_yang_diduduki                      = _i(item.get("kelas_tertinggi_yang_diduduki")),
            ijazah_tertinggi_yang_dimiliki                     = _i(item.get("ijazah_tertinggi_yang_dimiliki")),
            status_bekerja                                     = _s(item.get("status_bekerja")),
            status_dalam_pekerjaan_utama                       = _s(item.get("status_dalam_pekerjaan_utama")),
            lapangan_usaha_dari_pekerjaan_utama                = _i(item.get("lapangan_usaha_dari_pekerjaan_utama")),
            lapangan_usaha_dari_usaha_utama                    = _i(item.get("lapangan_usaha_dari_usaha_utama")),
            kepemilikan_usaha                                  = _s(item.get("kepemilikan_usaha")),
            jumlah_usaha                                       = _i(item.get("jumlah_usaha")),
            omzet_usaha_utama                                  = _d(item.get("omzet_usaha_utama")),
            jumlah_pekerja_yang_dibayar_dari_usaha_utama       = _i(item.get("jumlah_pekerja_yang_dibayar_dari_usaha_utama")),
            jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama = _i(item.get("jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama")),
            penglihatan                                        = _s(item.get("penglihatan")),
            pendengaran                                        = _s(item.get("pendengaran")),
            berjalan_atau_naik_tangga                          = _s(item.get("berjalan_atau_naik_tangga")),
            menggunakan_tangan_jari                            = _s(item.get("menggunakan_tangan_jari")),
            mengingat_berkonsentrasi                           = _s(item.get("mengingat_berkonsentrasi")),
            mengurus_diri                                      = _s(item.get("mengurus_diri")),
            berbicara_komunikasi                               = _s(item.get("berbicara_komunikasi")),
            belajar_kemampuan_intelektual                      = _s(item.get("belajar_kemampuan_intelektual")),
            pengendalian_perilaku                              = _s(item.get("pengendalian_perilaku")),
            kesedihan_depresi                                  = _s(item.get("kesedihan_depresi")),
            kondisi_gizi                                       = _s(item.get("kondisi_gizi")),
            penyakit_kronis                                    = _i(item.get("penyakit_kronis")),
            pbi_nas                                            = _s(item.get("pbi_nas")),
            pbi_pemda                                          = _s(item.get("pbi_pemda")),
            id_pelanggan_pln                                   = _s(item.get("id_pelanggan_pln")),
            provinsi_slug                                      = provinsi_slug,
        )


class ZawaSyncLog(Base):
    __tablename__ = "zawa_sync_log"
    id            = mapped_column(Integer,    primary_key=True, autoincrement=True)
    sync_type     = mapped_column(String(50), nullable=False)
    provinsi_slug = mapped_column(String(20), nullable=True)
    status        = mapped_column(String(20), nullable=False, default="pending")
    total_fetched = mapped_column(Integer,    nullable=True, default=0)
    total_saved   = mapped_column(Integer,    nullable=True, default=0)
    total_skipped = mapped_column(Integer,    nullable=True, default=0)
    total_error   = mapped_column(Integer,    nullable=True, default=0)
    error_message = mapped_column(Text,       nullable=True)
    started_at    = mapped_column(DateTime,   nullable=False, default=dt.utcnow)
    finished_at   = mapped_column(DateTime,   nullable=True)


# ─── ZAWA fetch helpers ────────────────────────────────────────

def _headers():
    h = {"Accept": "application/json"}
    if ZAWA_API_KEY:
        h["x-api-key"] = ZAWA_API_KEY
    return h


def fetch_anggota(slug: str):
    """
    Fetch semua data anggota dari endpoint zawa/<slug>.
    API mengembalikan: { "success": true, "data": [ {...}, ... ] }
    data adalah array langsung, BUKAN cursor-based pagination.

    Return: (items list, error_str | None)
    """
    url = f"{ZAWA_BASE}/zawa/{slug}"
    try:
        resp = requests.get(url, timeout=ZAWA_TIMEOUT, headers=_headers())
        resp.raise_for_status()
        raw = resp.json()
    except requests.exceptions.Timeout:
        return [], "Timeout"
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response else "?"
        return [], f"HTTP {code}"
    except Exception as e:
        return [], str(e)

    # ✔️ data adalah list langsung
    data = raw.get("data", [])
    if isinstance(data, list):
        return data, None

    # Fallback: jika ternyata wrapped dalam dict (antisipasi perubahan API)
    if isinstance(data, dict):
        items = data.get("items") or data.get("data") or []
        return items, None

    return [], f"Format response tidak dikenal: {type(data)}"


def correct_slug_from_item(item: dict, fallback_slug: str) -> str:
    """Tentukan provinsi_slug yang benar dari kode_provinsi_ktp."""
    kode = str(item.get("kode_provinsi_ktp") or "").strip().zfill(2)
    return _BPS_TO_SLUG.get(kode) or fallback_slug


# ─── Sync satu provinsi ────────────────────────────────────────

def sync_provinsi(session, slug: str, label: str) -> dict:
    logger.info(f"  ┌─ [{slug}] {label} — mulai fetch")
    started   = dt.utcnow()
    saved = skipped = error = 0
    error_msg = None

    sync_log = ZawaSyncLog(
        sync_type=f"anggota:{slug}",
        provinsi_slug=slug,
        status="running",
        started_at=started,
    )
    session.add(sync_log)
    session.commit()

    # ─ Fetch semua data dari API (satu request, array langsung)
    all_items, err = fetch_anggota(slug)

    if err:
        logger.warning(f"  │  [{slug}] FETCH ERROR: {err}")
        error_msg = err
        sync_log.status        = "failed"
        sync_log.error_message = error_msg
        sync_log.total_error   = 1
        sync_log.finished_at   = dt.utcnow()
        session.commit()
        return {"slug": slug, "label": label, "fetched": 0,
                "saved": 0, "skipped": 0, "error": 1,
                "status": "failed", "durasi": 0}

    total_api = len(all_items)
    # Potong sesuai LIMIT_PER_PROVINSI
    items = all_items[:LIMIT_PER_PROVINSI] if LIMIT_PER_PROVINSI > 0 else all_items
    logger.info(f"  │  [{slug}] API returned {total_api} rows, processing {len(items)} (limit={LIMIT_PER_PROVINSI or 'semua'})")

    for item in items:
        nik = str(item.get("nomor_induk_kependudukan") or "").strip()
        if not nik:
            skipped += 1
            continue

        # Cek duplikat NIK
        exists = session.execute(
            select(ZawaAnggota.id).where(
                ZawaAnggota.nomor_induk_kependudukan == nik
            )
        ).first()

        if exists:
            # Auto-repair provinsi_slug jika salah
            correct = correct_slug_from_item(item, slug)
            row = session.execute(
                select(ZawaAnggota).where(
                    ZawaAnggota.nomor_induk_kependudukan == nik
                )
            ).scalars().first()
            if row and row.provinsi_slug != correct:
                row.provinsi_slug = correct
                session.commit()
            skipped += 1
            continue

        try:
            correct = correct_slug_from_item(item, slug)
            obj = ZawaAnggota.from_api(item, correct)
            session.add(obj)
            session.commit()
            saved += 1
        except Exception as e:
            session.rollback()
            logger.warning(f"  │  [{slug}] INSERT ERR NIK={nik}: {e}")
            error += 1

    duration  = round((dt.utcnow() - started).total_seconds(), 1)
    status    = "failed" if error_msg else "success"

    sync_log.status        = status
    sync_log.total_fetched = len(items)
    sync_log.total_saved   = saved
    sync_log.total_skipped = skipped
    sync_log.total_error   = error
    sync_log.finished_at   = dt.utcnow()
    session.commit()

    logger.info(
        f"  └─ [{slug}] selesai: api={total_api} processed={len(items)} "
        f"saved={saved} skipped={skipped} error={error} ({duration}s)"
    )
    return {"slug": slug, "label": label, "fetched": len(items),
            "saved": saved, "skipped": skipped, "error": error,
            "status": status, "durasi": duration}


# ─── Main ──────────────────────────────────────────────────────

def main():
    targets = PROVINSI_LIST
    if ONLY_PROVINSI:
        if ONLY_PROVINSI not in PROVINSI_LIST:
            logger.error(
                f"Provinsi '{ONLY_PROVINSI}' tidak dikenal. "
                f"Pilihan: {', '.join(PROVINSI_LIST)}"
            )
            sys.exit(1)
        targets = {ONLY_PROVINSI: PROVINSI_LIST[ONLY_PROVINSI]}

    logger.info("=" * 65)
    logger.info("SYNC ANGGOTA — START")
    logger.info(f"DATABASE          : {DATABASE_URL.split('@')[-1]}")
    logger.info(f"LIMIT/PROVINSI    : {LIMIT_PER_PROVINSI or 'semua data'}")
    logger.info(f"SLEEP ANTAR PROV  : {SLEEP_BETWEEN}s")
    logger.info(f"TARGET PROVINSI   : {ONLY_PROVINSI or 'semua (' + str(len(targets)) + ' provinsi)'}")
    logger.info(f"SKIP ACEH         : ya")
    logger.info("=" * 65)

    session = Session()
    started = dt.utcnow()
    results = []
    grand_saved = grand_skip = grand_err = 0

    try:
        for slug, label in targets.items():
            result = sync_provinsi(session, slug, label)
            results.append(result)
            grand_saved += result["saved"]
            grand_skip  += result["skipped"]
            grand_err   += result["error"]
            time.sleep(SLEEP_BETWEEN)

    except KeyboardInterrupt:
        logger.warning("Dihentikan oleh user (Ctrl+C)")
    except Exception as e:
        logger.error(f"FATAL: {e}", exc_info=True)
        sys.exit(1)
    finally:
        session.close()

    duration = round((dt.utcnow() - started).total_seconds())
    logger.info("=" * 65)
    logger.info(f"SELESAI     provinsi={len(results)}")
    logger.info(f"TOTAL       saved={grand_saved}  skipped={grand_skip}  error={grand_err}")
    logger.info(f"DURASI      {duration}s ({round(duration / 60, 1)} menit)")
    logger.info("=" * 65)

    logger.info("\nRINGKASAN PER PROVINSI:")
    logger.info(f"{'Slug':<12} {'Label':<25} {'Fetched':>8} {'Saved':>7} {'Skip':>6} {'Err':>5}  {'Status'}")
    logger.info("-" * 75)
    for r in results:
        logger.info(
            f"{r['slug']:<12} {r['label']:<25} {r['fetched']:>8} "
            f"{r['saved']:>7} {r['skipped']:>6} {r['error']:>5}  {r['status']}"
        )


if __name__ == "__main__":
    main()
