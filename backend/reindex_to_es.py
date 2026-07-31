#!/usr/bin/env python3
"""
reindex_to_es.py

Isi Elasticsearch dari data MySQL yang sudah ada (ZawaAnggota & ZawaKeluarga).

Fitur:
  - ID-based pagination (WHERE id > last_id) — tidak lambat seperti OFFSET
  - Checkpoint file (reindex_checkpoint.json) — bisa dilanjut kalau gagal di tengah
  - Retry per batch (3x) untuk error ES sementara (network blip, timeout)
  - Error log terpisah (reindex_errors.log) — gagal per row dicatat, tidak abort
  - Progress bar sederhana di terminal

Cara pakai:

    # Normal (lanjut dari checkpoint kalau ada):
    docker compose exec api python reindex_to_es.py

    # Mulai dari awal (ignore checkpoint):
    docker compose exec api python reindex_to_es.py --fresh

    # Hanya reindex satu tabel:
    docker compose exec api python reindex_to_es.py --only anggota
    docker compose exec api python reindex_to_es.py --only keluarga
"""

import os
import sys
import json
import time
import logging
import argparse
from decimal import Decimal
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Pastikan app context Flask tersedia agar SQLAlchemy bisa dipakai
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app
from app.extensions import db
from app.models.zawa import ZawaAnggota, ZawaKeluarga
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, BulkIndexError

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ES_URL           = os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
INDEX_ANGGOTA    = "dtsen_anggota"
INDEX_KELUARGA   = "dtsen_keluarga"
BATCH_SIZE       = 500       # dokumen per bulk request
MAX_RETRY        = 3         # retry per batch jika ES error
RETRY_DELAY      = 5         # detik antar retry
CHECKPOINT_FILE  = "/tmp/reindex_checkpoint.json"
ERROR_LOG_FILE   = "/tmp/reindex_errors.log"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("reindex")

err_handler = logging.FileHandler(ERROR_LOG_FILE)
err_handler.setLevel(logging.ERROR)
err_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
log.addHandler(err_handler)


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------

def _load_checkpoint() -> dict:
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"anggota_last_id": 0, "keluarga_last_id": 0}


def _save_checkpoint(cp: dict):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(cp, f)


def _clear_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)


# ---------------------------------------------------------------------------
# Serializer helpers
# Semua nilai harus JSON-serializable dan cocok dengan ES mapping.
# ---------------------------------------------------------------------------

def _safe_int(val) -> int | None:
    """Cast ke int, return None jika gagal atau kosong."""
    if val is None:
        return None
    try:
        s = str(val).strip()
        return int(s) if s else None
    except (ValueError, TypeError):
        return None


def _safe_str(val) -> str | None:
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def _safe_long(val) -> int | None:
    """Cast Decimal/float/str ke int (untuk omzet)."""
    if val is None:
        return None
    try:
        return int(Decimal(str(val)))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Row → ES document serializers
# Urutan field mengikuti mapping create_es_index.py.
# Tipe harus cocok persis:
#   keyword  → str
#   integer  → int
#   long     → int
#   date     → str "YYYY-MM-DD"
#   text     → str
# ---------------------------------------------------------------------------

def _serialize_anggota(row: ZawaAnggota) -> dict:
    return {
        "_index": INDEX_ANGGOTA,
        "_id":    str(row.nomor_induk_kependudukan),  # NIK sebagai doc ID (idempotent)
        "_source": {
            "nomor_induk_kependudukan":  _safe_str(row.nomor_induk_kependudukan),
            "nomor_kartu_keluarga":      _safe_str(row.nomor_kartu_keluarga),
            "nama":                      _safe_str(row.nama),
            "jenis_kelamin":             _safe_str(row.jenis_kelamin),
            "tanggal_lahir":             _safe_str(row.tanggal_lahir),   # sudah YYYY-MM-DD di DB
            "status_kawin":              _safe_str(row.status_kawin),
            "status_hubungan_keluarga":  _safe_str(row.status_hubungan_keluarga),
            "alamat_ktp":                _safe_str(row.alamat_ktp),
            "dusun_ktp":                 _safe_str(row.dusun_ktp),
            "rt_ktp":                    _safe_int(row.rt_ktp),
            "rw_ktp":                    _safe_int(row.rw_ktp),
            "kelurahan_desa_ktp":        _safe_str(row.kelurahan_desa_ktp),
            "kecamatan_ktp":             _safe_str(row.kecamatan_ktp),
            "kabupaten_kota_ktp":        _safe_str(row.kabupaten_kota_ktp),
            "provinsi_ktp":              _safe_str(row.provinsi_ktp),
            "kode_kelurahan_desa_ktp":   _safe_str(row.kode_kelurahan_desa_ktp),
            "kode_kecamatan_ktp":        _safe_str(row.kode_kecamatan_ktp),
            "kode_kabupaten_kota_ktp":   _safe_str(row.kode_kabupaten_kota_ktp),
            "kode_provinsi_ktp":         _safe_str(row.kode_provinsi_ktp),
            "partisipasi_sekolah":               _safe_str(row.partisipasi_sekolah),
            "jenjang_tertinggi_yang_diduduki":   _safe_int(row.jenjang_tertinggi_yang_diduduki),
            "kelas_tertinggi_yang_diduduki":     _safe_int(row.kelas_tertinggi_yang_diduduki),
            "ijazah_tertinggi_yang_dimiliki":    _safe_int(row.ijazah_tertinggi_yang_dimiliki),
            "status_bekerja":                    _safe_str(row.status_bekerja),
            "status_dalam_pekerjaan_utama":      _safe_str(row.status_dalam_pekerjaan_utama),
            "lapangan_usaha_dari_pekerjaan_utama":              _safe_int(row.lapangan_usaha_dari_pekerjaan_utama),
            "lapangan_usaha_dari_usaha_utama":                  _safe_int(row.lapangan_usaha_dari_usaha_utama),
            "kepemilikan_usaha":                                _safe_str(row.kepemilikan_usaha),
            "jumlah_usaha":                                     _safe_int(row.jumlah_usaha),
            "omzet_usaha_utama":                                _safe_long(row.omzet_usaha_utama),
            "jumlah_pekerja_yang_dibayar_dari_usaha_utama":     _safe_int(row.jumlah_pekerja_yang_dibayar_dari_usaha_utama),
            "jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama": _safe_int(row.jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama),
            "penglihatan":               _safe_str(row.penglihatan),
            "pendengaran":               _safe_str(row.pendengaran),
            "berjalan_atau_naik_tangga": _safe_str(row.berjalan_atau_naik_tangga),
            "menggunakan_tangan_jari":   _safe_str(row.menggunakan_tangan_jari),
            "mengingat_berkonsentrasi":  _safe_str(row.mengingat_berkonsentrasi),
            "mengurus_diri":             _safe_str(row.mengurus_diri),
            "berbicara_komunikasi":      _safe_str(row.berbicara_komunikasi),
            "belajar_kemampuan_intelektual": _safe_str(row.belajar_kemampuan_intelektual),
            "pengendalian_perilaku":     _safe_str(row.pengendalian_perilaku),
            "kesedihan_depresi":         _safe_str(row.kesedihan_depresi),
            "kondisi_gizi":              _safe_str(row.kondisi_gizi),
            "penyakit_kronis":           _safe_int(row.penyakit_kronis),
            "pbi_nas":                   _safe_str(row.pbi_nas),
            "pbi_pemda":                 _safe_str(row.pbi_pemda),
            "id_pelanggan_pln":          _safe_str(row.id_pelanggan_pln),
            "provinsi_slug":             _safe_str(row.provinsi_slug),
        }
    }


def _serialize_keluarga(row: ZawaKeluarga) -> dict:
    return {
        "_index": INDEX_KELUARGA,
        "_id":    str(row.nomor_kartu_keluarga),  # NKK sebagai doc ID (idempotent)
        "_source": {
            "nomor_kartu_keluarga":      _safe_str(row.nomor_kartu_keluarga),
            "nama_anggota_keluarga":     _safe_str(row.nama_anggota_keluarga),
            "jumlah_anggota_keluarga":   _safe_int(row.jumlah_anggota_keluarga),
            "alamat":                    _safe_str(row.alamat),
            "kelurahan_desa":            _safe_str(row.kelurahan_desa),
            "kecamatan":                 _safe_str(row.kecamatan),
            "kabupaten_kota":            _safe_str(row.kabupaten_kota),
            "provinsi":                  _safe_str(row.provinsi),
            "kode_kelurahan_desa":       _safe_str(row.kode_kelurahan_desa),
            "kode_kecamatan":            _safe_str(row.kode_kecamatan),
            "kode_kabupaten_kota":       _safe_str(row.kode_kabupaten_kota),
            "kode_provinsi":             _safe_str(row.kode_provinsi),
            "luas_lantai":               _safe_int(row.luas_lantai),
            "jenis_lantai_terluas":      _safe_int(row.jenis_lantai_terluas),
            "jenis_dinding_terluas":     _safe_int(row.jenis_dinding_terluas),
            "jenis_atap_terluas":        _safe_int(row.jenis_atap_terluas),
            "jenis_kloset":              _safe_str(row.jenis_kloset),
            "fasilitas_bab":             _safe_str(row.fasilitas_bab),
            "sumber_air_minum_utama":    _safe_int(row.sumber_air_minum_utama),
            "sumber_penerangan_utama":   _safe_str(row.sumber_penerangan_utama),
            "bahan_bakar_utama_memasak": _safe_int(row.bahan_bakar_utama_memasak),
            "daya_terpasang":            _safe_int(row.daya_terpasang),
            "pembuangan_akhir_tinja":    _safe_str(row.pembuangan_akhir_tinja),
            "status_kepemilikan_rumah":  _safe_str(row.status_kepemilikan_rumah),
            "kepemilikan_aset":          _safe_str(row.kepemilikan_aset),
            "aset_bergerak_sepeda_motor":             _safe_str(row.aset_bergerak_sepeda_motor),
            "aset_bergerak_mobil":                    _safe_str(row.aset_bergerak_mobil),
            "aset_bergerak_sepeda":                   _safe_str(row.aset_bergerak_sepeda),
            "aset_bergerak_perahu":                   _safe_str(row.aset_bergerak_perahu),
            "aset_bergerak_kapal_perahu_motor":       _safe_str(row.aset_bergerak_kapal_perahu_motor),
            "aset_bergerak_smartphone":               _safe_str(row.aset_bergerak_smartphone),
            "aset_bergerak_komputer_laptop_tablet":   _safe_str(row.aset_bergerak_komputer_laptop_tablet),
            "aset_bergerak_lemari_es":                _safe_str(row.aset_bergerak_lemari_es),
            "aset_bergerak_ac":                       _safe_str(row.aset_bergerak_ac),
            "aset_bergerak_tv_datar":                 _safe_str(row.aset_bergerak_tv_datar),
            "aset_bergerak_emas_perhiasan":           _safe_str(row.aset_bergerak_emas_perhiasan),
            "aset_bergerak_tabung_gas":               _safe_str(row.aset_bergerak_tabung_gas),
            "aset_bergerak_pemanas_air":              _safe_str(row.aset_bergerak_pemanas_air),
            "aset_bergerak_telepon_rumah":            _safe_str(row.aset_bergerak_telepon_rumah),
            "aset_tidak_bergerak_rumah_lainnya":      _safe_str(row.aset_tidak_bergerak_rumah_lainnya),
            "aset_tidak_bergerak_lahan_lainnya":      _safe_str(row.aset_tidak_bergerak_lahan_lainnya),
            "jumlah_ternak_sapi":          _safe_int(row.jumlah_ternak_sapi),
            "jumlah_ternak_kerbau":        _safe_int(row.jumlah_ternak_kerbau),
            "jumlah_ternak_kuda":          _safe_int(row.jumlah_ternak_kuda),
            "jumlah_ternak_kambing_domba": _safe_int(row.jumlah_ternak_kambing_domba),
            "jumlah_ternak_babi":          _safe_int(row.jumlah_ternak_babi),
            "pbi_nas":          _safe_str(row.pbi_nas),
            "pbi_pemda":        _safe_str(row.pbi_pemda),
            # desil_nasional: DB String(5) → cast ke int
            "desil_nasional":   _safe_int(row.desil_nasional),
            "id_pelanggan_pln": _safe_str(row.id_pelanggan_pln),
        }
    }


# ---------------------------------------------------------------------------
# Bulk send dengan retry
# ---------------------------------------------------------------------------

def _bulk_with_retry(es: Elasticsearch, actions: list, label: str) -> int:
    """Kirim bulk ke ES, retry MAX_RETRY kali. Return jumlah sukses."""
    for attempt in range(1, MAX_RETRY + 1):
        try:
            success, errors = bulk(es, actions, raise_on_error=False, stats_only=False)
            if errors:
                for err in errors:
                    doc_id = err.get("index", {}).get("_id", "?")
                    reason = err.get("index", {}).get("error", {}).get("reason", "unknown")
                    log.error(f"{label} | bulk error doc_id={doc_id}: {reason}")
            return success
        except Exception as exc:
            if attempt < MAX_RETRY:
                log.warning(f"{label} | bulk attempt {attempt} gagal: {exc}. Retry dalam {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                log.error(f"{label} | bulk GAGAL setelah {MAX_RETRY} percobaan: {exc}")
                return 0


# ---------------------------------------------------------------------------
# Reindex per tabel
# ---------------------------------------------------------------------------

def reindex_anggota(es: Elasticsearch, last_id: int, cp: dict):
    total = db.session.query(ZawaAnggota).count()
    log.info(f"[ANGGOTA] Total rows di MySQL: {total:,} | Mulai dari id > {last_id}")

    indexed = 0
    batch_num = 0
    current_last_id = last_id

    while True:
        rows = (
            db.session.query(ZawaAnggota)
            .filter(ZawaAnggota.id > current_last_id)
            .order_by(ZawaAnggota.id)
            .limit(BATCH_SIZE)
            .all()
        )
        if not rows:
            break

        actions = [_serialize_anggota(r) for r in rows]
        success = _bulk_with_retry(es, actions, "ANGGOTA")
        indexed += success
        batch_num += 1
        current_last_id = rows[-1].id

        # Simpan checkpoint setiap batch
        cp["anggota_last_id"] = current_last_id
        _save_checkpoint(cp)

        pct = (indexed / total * 100) if total else 0
        log.info(
            f"[ANGGOTA] batch={batch_num} | indexed={indexed:,}/{total:,} ({pct:.1f}%) "
            f"| last_id={current_last_id}"
        )

        db.session.expire_all()  # bebaskan memori SQLAlchemy per batch

    log.info(f"[ANGGOTA] Selesai. Total ter-index: {indexed:,}")
    return indexed


def reindex_keluarga(es: Elasticsearch, last_id: int, cp: dict):
    total = db.session.query(ZawaKeluarga).count()
    log.info(f"[KELUARGA] Total rows di MySQL: {total:,} | Mulai dari id > {last_id}")

    indexed = 0
    batch_num = 0
    current_last_id = last_id

    while True:
        rows = (
            db.session.query(ZawaKeluarga)
            .filter(ZawaKeluarga.id > current_last_id)
            .order_by(ZawaKeluarga.id)
            .limit(BATCH_SIZE)
            .all()
        )
        if not rows:
            break

        actions = [_serialize_keluarga(r) for r in rows]
        success = _bulk_with_retry(es, actions, "KELUARGA")
        indexed += success
        batch_num += 1
        current_last_id = rows[-1].id

        cp["keluarga_last_id"] = current_last_id
        _save_checkpoint(cp)

        pct = (indexed / total * 100) if total else 0
        log.info(
            f"[KELUARGA] batch={batch_num} | indexed={indexed:,}/{total:,} ({pct:.1f}%) "
            f"| last_id={current_last_id}"
        )

        db.session.expire_all()

    log.info(f"[KELUARGA] Selesai. Total ter-index: {indexed:,}")
    return indexed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Reindex MySQL → Elasticsearch")
    parser.add_argument(
        "--fresh", action="store_true",
        help="Ignore checkpoint, mulai dari id=0"
    )
    parser.add_argument(
        "--only", choices=["anggota", "keluarga"],
        help="Hanya reindex satu tabel"
    )
    args = parser.parse_args()

    # ES client
    es = Elasticsearch(ES_URL, request_timeout=60)
    if not es.ping():
        log.error(f"Tidak dapat terhubung ke Elasticsearch di {ES_URL}")
        sys.exit(1)
    log.info(f"Terhubung ke Elasticsearch: {ES_URL}")

    # Checkpoint
    if args.fresh:
        _clear_checkpoint()
        log.info("--fresh: checkpoint dihapus, mulai dari awal.")
    cp = _load_checkpoint()
    log.info(f"Checkpoint saat ini: {cp}")

    started = datetime.now()

    # Flask app context untuk SQLAlchemy
    flask_app = create_app()
    with flask_app.app_context():
        if args.only == "keluarga":
            reindex_keluarga(es, cp.get("keluarga_last_id", 0), cp)
        elif args.only == "anggota":
            reindex_anggota(es, cp.get("anggota_last_id", 0), cp)
        else:
            reindex_anggota(es, cp.get("anggota_last_id", 0), cp)
            reindex_keluarga(es, cp.get("keluarga_last_id", 0), cp)

    elapsed = datetime.now() - started
    log.info(f"[SELESAI] Total waktu: {elapsed}")
    log.info(f"Error log: {ERROR_LOG_FILE}")

    # Hapus checkpoint jika selesai bersih
    if not args.only:
        _clear_checkpoint()
        log.info("Checkpoint dihapus (reindex selesai penuh).")


if __name__ == "__main__":
    main()
