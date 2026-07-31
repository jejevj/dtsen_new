#!/usr/bin/env python3
"""
create_es_index.py

Buat (atau re-create) index Elasticsearch untuk:
  - dtsen_anggota  : mapping ZawaAnggota
  - dtsen_keluarga : mapping ZawaKeluarga

Jalankan SATU KALI sebelum reindex_to_es.py:

    # Dari host (ES harus sudah running):
    docker compose exec api python create_es_index.py

    # Atau langsung dari host jika ES port di-expose (dev only):
    ES_URL=http://localhost:9200 python create_es_index.py

Opsi:
    --force   Hapus index yang sudah ada lalu buat ulang (HAPUS SEMUA DATA!)
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

load_dotenv()

ES_URL         = os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
INDEX_ANGGOTA  = "dtsen_anggota"
INDEX_KELUARGA = "dtsen_keluarga"

# ---------------------------------------------------------------------------
# Setting umum untuk kedua index
# ---------------------------------------------------------------------------
COMMON_SETTINGS = {
    "number_of_shards":   1,   # single-node, 1 shard cukup
    "number_of_replicas": 0,   # tidak ada replica (single-node)
    "max_result_window":  50_000,
    "analysis": {
        "analyzer": {
            "indonesia_analyzer": {
                "type":      "custom",
                "tokenizer": "standard",
                "filter":    ["lowercase", "asciifolding"],
            }
        }
    }
}


# ---------------------------------------------------------------------------
# Mapping: dtsen_anggota  (ZawaAnggota)
# Semua field di _ANGGOTA_COLUMN_MAP dari baseline.py dicakup di sini.
#
# Konvensi tipe:
#   - text + keyword sub-field : teks bebas yang perlu full-text search DAN filter exact
#   - keyword                  : nilai kategorikal / kode (is_filter=True, nilai terbatas)
#   - integer / long           : angka bulat
#   - float                    : angka desimal
#   - date (yyyy-MM-dd)        : tanggal (tanggal_lahir) untuk filter range usia
# ---------------------------------------------------------------------------
MAPPING_ANGGOTA = {
    "settings": COMMON_SETTINGS,
    "mappings": {
        "dynamic": "strict",   # tolak field tak dikenal agar mapping tidak menggelembung
        "properties": {

            # ── Kunci utama ──────────────────────────────────────────────
            "nomor_induk_kependudukan": {"type": "keyword"},  # NIK 16 digit, exact only
            "nomor_kartu_keluarga":     {"type": "keyword"},  # NKK 16 digit, join ke keluarga

            # ── Identitas ────────────────────────────────────────────────
            "nama": {
                "type": "text",
                "analyzer": "indonesia_analyzer",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}
            },
            "jenis_kelamin":            {"type": "keyword"},
            "tanggal_lahir":            {"type": "date", "format": "yyyy-MM-dd"},  # untuk filter usia
            "status_kawin":             {"type": "keyword"},
            "status_hubungan_keluarga": {"type": "keyword"},

            # ── Alamat KTP ───────────────────────────────────────────────
            "alamat_ktp": {
                "type": "text",
                "analyzer": "indonesia_analyzer",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 512}}
            },
            "dusun_ktp":                {"type": "keyword"},
            "rt_ktp":                   {"type": "keyword"},
            "rw_ktp":                   {"type": "keyword"},
            "kelurahan_desa_ktp":       {"type": "keyword"},
            "kecamatan_ktp":            {"type": "keyword"},
            "kabupaten_kota_ktp":       {"type": "keyword"},
            "provinsi_ktp":             {"type": "keyword"},
            # Kode wilayah — keyword untuk exact match & filter bertingkat
            "kode_kelurahan_desa_ktp":  {"type": "keyword"},
            "kode_kecamatan_ktp":       {"type": "keyword"},
            "kode_kabupaten_kota_ktp":  {"type": "keyword"},
            "kode_provinsi_ktp":        {"type": "keyword"},

            # ── Pendidikan ───────────────────────────────────────────────
            "partisipasi_sekolah":              {"type": "keyword"},
            "jenjang_tertinggi_yang_diduduki":  {"type": "keyword"},
            "kelas_tertinggi_yang_diduduki":    {"type": "keyword"},
            "ijazah_tertinggi_yang_dimiliki":   {"type": "keyword"},

            # ── Pekerjaan ────────────────────────────────────────────────
            "status_bekerja":                   {"type": "keyword"},
            "status_dalam_pekerjaan_utama":     {"type": "keyword"},
            "lapangan_usaha_dari_pekerjaan_utama": {"type": "keyword"},
            "lapangan_usaha_dari_usaha_utama":  {"type": "keyword"},
            "kepemilikan_usaha":                {"type": "keyword"},
            "jumlah_usaha":                     {"type": "integer"},
            "omzet_usaha_utama":                {"type": "long"},
            "jumlah_pekerja_yang_dibayar_dari_usaha_utama":     {"type": "integer"},
            "jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama": {"type": "integer"},

            # ── Disabilitas ──────────────────────────────────────────────
            "penglihatan":              {"type": "keyword"},
            "pendengaran":              {"type": "keyword"},
            "berjalan_atau_naik_tangga":{"type": "keyword"},
            "menggunakan_tangan_jari":  {"type": "keyword"},
            "mengingat_berkonsentrasi": {"type": "keyword"},
            "mengurus_diri":            {"type": "keyword"},
            "berbicara_komunikasi":     {"type": "keyword"},
            "belajar_kemampuan_intelektual": {"type": "keyword"},
            "pengendalian_perilaku":    {"type": "keyword"},
            "kesedihan_depresi":        {"type": "keyword"},

            # ── Kesehatan & PBI ─────────────────────────────────────────
            "kondisi_gizi":             {"type": "keyword"},
            "penyakit_kronis":          {"type": "keyword"},
            "pbi_nas":                  {"type": "keyword"},
            "pbi_pemda":                {"type": "keyword"},

            # ── PLN ─────────────────────────────────────────────────────
            "id_pelanggan_pln":         {"type": "keyword"},

            # ── Metadata internal (dari provinsi_slug di DB) ─────────────
            "provinsi_slug":            {"type": "keyword"},
        }
    }
}


# ---------------------------------------------------------------------------
# Mapping: dtsen_keluarga  (ZawaKeluarga)
# Semua field di _KELUARGA_COLUMN_MAP dari baseline.py dicakup di sini.
# ---------------------------------------------------------------------------
MAPPING_KELUARGA = {
    "settings": COMMON_SETTINGS,
    "mappings": {
        "dynamic": "strict",
        "properties": {

            # ── Kunci utama ──────────────────────────────────────────────
            "nomor_kartu_keluarga": {"type": "keyword"},

            # ── Identitas kepala keluarga ────────────────────────────────
            "nama_anggota_keluarga": {
                "type": "text",
                "analyzer": "indonesia_analyzer",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}
            },
            "jumlah_anggota_keluarga": {"type": "integer"},

            # ── Alamat ───────────────────────────────────────────────────
            "alamat": {
                "type": "text",
                "analyzer": "indonesia_analyzer",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 512}}
            },
            "kelurahan_desa":       {"type": "keyword"},
            "kecamatan":            {"type": "keyword"},
            "kabupaten_kota":       {"type": "keyword"},
            "provinsi":             {"type": "keyword"},
            "kode_kelurahan_desa":  {"type": "keyword"},
            "kode_kecamatan":       {"type": "keyword"},
            "kode_kabupaten_kota":  {"type": "keyword"},
            "kode_provinsi":        {"type": "keyword"},

            # ── Kondisi rumah ────────────────────────────────────────────
            "luas_lantai":           {"type": "float"},
            "jenis_lantai_terluas":  {"type": "keyword"},
            "jenis_dinding_terluas": {"type": "keyword"},
            "jenis_atap_terluas":    {"type": "keyword"},
            "jenis_kloset":          {"type": "keyword"},
            "fasilitas_bab":         {"type": "keyword"},
            "sumber_air_minum_utama":{"type": "keyword"},
            "sumber_penerangan_utama":{"type": "keyword"},
            "bahan_bakar_utama_memasak": {"type": "keyword"},
            "daya_terpasang":        {"type": "keyword"},
            "pembuangan_akhir_tinja":{"type": "keyword"},
            "status_kepemilikan_rumah": {"type": "keyword"},

            # ── Aset ─────────────────────────────────────────────────────
            "kepemilikan_aset":      {"type": "keyword"},
            "aset_bergerak_sepeda_motor":            {"type": "keyword"},
            "aset_bergerak_mobil":                   {"type": "keyword"},
            "aset_bergerak_sepeda":                  {"type": "keyword"},
            "aset_bergerak_perahu":                  {"type": "keyword"},
            "aset_bergerak_kapal_perahu_motor":      {"type": "keyword"},
            "aset_bergerak_smartphone":              {"type": "keyword"},
            "aset_bergerak_komputer_laptop_tablet":  {"type": "keyword"},
            "aset_bergerak_lemari_es":               {"type": "keyword"},
            "aset_bergerak_ac":                      {"type": "keyword"},
            "aset_bergerak_tv_datar":                {"type": "keyword"},
            "aset_bergerak_emas_perhiasan":          {"type": "keyword"},
            "aset_bergerak_tabung_gas":              {"type": "keyword"},
            "aset_bergerak_pemanas_air":             {"type": "keyword"},
            "aset_bergerak_telepon_rumah":           {"type": "keyword"},
            "aset_tidak_bergerak_rumah_lainnya":     {"type": "keyword"},
            "aset_tidak_bergerak_lahan_lainnya":     {"type": "keyword"},

            # ── Ternak (integer untuk filter range "0", "1-5", ">5") ─────
            "jumlah_ternak_sapi":         {"type": "integer"},
            "jumlah_ternak_kerbau":       {"type": "integer"},
            "jumlah_ternak_kuda":         {"type": "integer"},
            "jumlah_ternak_kambing_domba":{"type": "integer"},
            "jumlah_ternak_babi":         {"type": "integer"},

            # ── PBI & desil ──────────────────────────────────────────────
            "pbi_nas":         {"type": "keyword"},
            "pbi_pemda":       {"type": "keyword"},
            "desil_nasional":  {"type": "integer"},   # filter: IN (1,2,3,4)
            "id_pelanggan_pln":{"type": "keyword"},
        }
    }
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_client() -> Elasticsearch:
    client = Elasticsearch(ES_URL, request_timeout=30)
    if not client.ping():
        print(f"[ERROR] Tidak dapat terhubung ke Elasticsearch di {ES_URL}")
        sys.exit(1)
    print(f"[OK] Terhubung ke Elasticsearch: {ES_URL}")
    return client


def _delete_index_if_exists(client: Elasticsearch, index: str):
    try:
        client.indices.delete(index=index)
        print(f"[INFO] Index '{index}' dihapus.")
    except NotFoundError:
        pass


def _create_index(client: Elasticsearch, index: str, body: dict, force: bool):
    if client.indices.exists(index=index):
        if force:
            _delete_index_if_exists(client, index)
        else:
            print(f"[SKIP] Index '{index}' sudah ada. Gunakan --force untuk re-create.")
            return
    client.indices.create(index=index, body=body)
    print(f"[OK] Index '{index}' berhasil dibuat.")
    info = client.indices.get(index=index)
    shards = info[index]["settings"]["index"]["number_of_shards"]
    print(f"       shards={shards}, replicas=0, dynamic=strict")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Buat ES index untuk DTSEN.")
    parser.add_argument(
        "--force", action="store_true",
        help="Hapus index yang sudah ada dan buat ulang (HAPUS SEMUA DATA!)"
    )
    args = parser.parse_args()

    if args.force:
        print("[PERINGATAN] --force aktif: index yang ada akan DIHAPUS dan dibuat ulang!")

    client = _get_client()

    _create_index(client, INDEX_ANGGOTA,  MAPPING_ANGGOTA,  args.force)
    _create_index(client, INDEX_KELUARGA, MAPPING_KELUARGA, args.force)

    print("\n[SELESAI] Semua index sudah siap. Lanjutkan dengan: python reindex_to_es.py")


if __name__ == "__main__":
    main()
