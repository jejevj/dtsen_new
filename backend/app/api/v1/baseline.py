import logging
import os
import re
import time
import requests
from datetime import date, datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import distinct, select, func
from . import api_v1_bp
from ...extensions import db
from ...models.zawa import ZawaAnggota, ZawaKeluarga, ZawaSyncLog
from ...models.t_dtsen_wilayah import TDtsenWilayah
from ...models.t_dtsen_akses import TDtsenAkses
from ...services.auth_service import parse_identity_str
from ...utils.crypto import (
    encrypt_identifier,
    decrypt_identifier,
)
from ...services.mustahik_service import MustahikService


logger = logging.getLogger('app')

PROVINSI_MAP = {
    "aceh":      {"label": "Aceh",               "slug": "anggota",    "bps": "11"},
    "sumut":     {"label": "Sumatera Utara",     "slug": "sumut",      "bps": "12"},
    "sumbar":    {"label": "Sumatera Barat",     "slug": "sumbar",     "bps": "13"},
    "riau":      {"label": "Riau",               "slug": "riau",       "bps": "14"},
    "jambi":     {"label": "Jambi",              "slug": "jambi",      "bps": "15"},
    "sumsel":    {"label": "Sumatera Selatan",   "slug": "sumsel",     "bps": "16"},
    "bengkulu":  {"label": "Bengkulu",           "slug": "bengkulu",   "bps": "17"},
    "lampung":   {"label": "Lampung",            "slug": "lampung",    "bps": "18"},
    "babel":     {"label": "Bangka Belitung",    "slug": "babel",      "bps": "19"},
    "kepriau":   {"label": "Kepulauan Riau",     "slug": "kepriau",    "bps": "21"},
    "dkijakarta":{"label": "DKI Jakarta",        "slug": "dkijakarta", "bps": "31"},
    "jabar":     {"label": "Jawa Barat",         "slug": "jabar",      "bps": "32"},
    "jateng":    {"label": "Jawa Tengah",        "slug": "jateng",     "bps": "33"},
    "diy":       {"label": "DI Yogyakarta",      "slug": "diy",        "bps": "34"},
    "jatim":     {"label": "Jawa Timur",         "slug": "jatim",      "bps": "35"},
    "banten":    {"label": "Banten",             "slug": "banten",     "bps": "36"},
    "bali":      {"label": "Bali",               "slug": "bali",       "bps": "51"},
    "ntb":       {"label": "Nusa Tenggara Barat","slug": "ntb",        "bps": "52"},
    "ntt":       {"label": "Nusa Tenggara Timur","slug": "ntt",        "bps": "53"},
    "kalbar":    {"label": "Kalimantan Barat",   "slug": "kalbar",     "bps": "61"},
    "kalteng":   {"label": "Kalimantan Tengah",  "slug": "kalteng",    "bps": "62"},
    "kalsel":    {"label": "Kalimantan Selatan", "slug": "kalsel",     "bps": "63"},
    "kaltim":    {"label": "Kalimantan Timur",   "slug": "kaltim",     "bps": "64"},
    "kaltara":   {"label": "Kalimantan Utara",   "slug": "kaltara",    "bps": "65"},
    "sulut":     {"label": "Sulawesi Utara",     "slug": "sulut",      "bps": "71"},
    "sulteng":   {"label": "Sulawesi Tengah",    "slug": "sulteng",    "bps": "72"},
    "sulsel":    {"label": "Sulawesi Selatan",   "slug": "sulsel",     "bps": "73"},
    "sultra":    {"label": "Sulawesi Tenggara",  "slug": "sultra",     "bps": "74"},
    "gorontalo": {"label": "Gorontalo",          "slug": "gorontalo",  "bps": "75"},
    "sulbar":    {"label": "Sulawesi Barat",     "slug": "sulbar",     "bps": "76"},
    "maluku":    {"label": "Maluku",             "slug": "maluku",     "bps": "81"},
    "malut":     {"label": "Maluku Utara",       "slug": "malut",      "bps": "82"},
    "papbar":    {"label": "Papua Barat",        "slug": "papbar",     "bps": "91"},
    "papua":     {"label": "Papua",              "slug": "papua",      "bps": "94"},
    "papsel":    {"label": "Papua Selatan",      "slug": "papsel",     "bps": "95"},
    "papteng":   {"label": "Papua Tengah",       "slug": "papteng",    "bps": "96"},
    "papgu":     {"label": "Papua Pegunungan",   "slug": "papgu",      "bps": "97"},
    "papdy":     {"label": "Papua Barat Daya",   "slug": "papdy",      "bps": "92"},
}

# Lookup: BPS kode (2 digit) → slug
_BPS_TO_SLUG: dict[str, str] = {v["bps"]: k for k, v in PROVINSI_MAP.items()}

ZAWA_BASE    = "https://spl-satudata.kemenag.go.id/core/api"
ZAWA_TIMEOUT = 60
ZAWA_LIMIT   = 10   # page size untuk ZAWA API
DB_PAGE_SIZE = 10   # page size untuk query DB lokal

SYNC_MAX_ANGGOTA_PER_PROVINSI = 10_000
SYNC_MAX_KELUARGA_PER_RUN     = 5_000

_CACHE: dict = {}
CACHE_TTL = 600

# ---------------------------------------------------------------------------
# Desil filter: hanya tampilkan keluarga & anggota desil nasional 1-4
# ---------------------------------------------------------------------------
_DESIL_ALLOWED = (1, 2, 3, 4)

# ---------------------------------------------------------------------------
# Mapping field_key (dari m_tampilan_dtsen) → nama kolom di ZawaAnggota
# ---------------------------------------------------------------------------
_ANGGOTA_COLUMN_MAP: dict[str, str] = {
    "nomor_induk_kependudukan":        "nomor_induk_kependudukan",
    "nomor_kartu_keluarga":            "nomor_kartu_keluarga",
    "nama":                            "nama",
    "jenis_kelamin":                   "jenis_kelamin",
    "tanggal_lahir":                   "tanggal_lahir",
    "status_kawin":                    "status_kawin",
    "status_hubungan_keluarga":        "status_hubungan_keluarga",
    "alamat_ktp":                      "alamat_ktp",
    "dusun_ktp":                       "dusun_ktp",
    "rt_ktp":                          "rt_ktp",
    "rw_ktp":                          "rw_ktp",
    "kelurahan_desa_ktp":              "kelurahan_desa_ktp",
    "kecamatan_ktp":                   "kecamatan_ktp",
    "kabupaten_kota_ktp":              "kabupaten_kota_ktp",
    "provinsi_ktp":                    "provinsi_ktp",
    "kode_kelurahan_desa_ktp":         "kode_kelurahan_desa_ktp",
    "kode_kecamatan_ktp":              "kode_kecamatan_ktp",
    "kode_kabupaten_kota_ktp":         "kode_kabupaten_kota_ktp",
    "kode_provinsi_ktp":               "kode_provinsi_ktp",
    "partisipasi_sekolah":             "partisipasi_sekolah",
    "jenjang_tertinggi_yang_diduduki": "jenjang_tertinggi_yang_diduduki",
    "kelas_tertinggi_yang_diduduki":   "kelas_tertinggi_yang_diduduki",
    "ijazah_tertinggi_yang_dimiliki":  "ijazah_tertinggi_yang_dimiliki",
    "status_bekerja":                  "status_bekerja",
    "status_dalam_pekerjaan_utama":    "status_dalam_pekerjaan_utama",
    "lapangan_usaha_dari_pekerjaan_utama":            "lapangan_usaha_dari_pekerjaan_utama",
    "lapangan_usaha_dari_usaha_utama":                "lapangan_usaha_dari_usaha_utama",
    "kepemilikan_usaha":               "kepemilikan_usaha",
    "jumlah_usaha":                    "jumlah_usaha",
    "omzet_usaha_utama":               "omzet_usaha_utama",
    "jumlah_pekerja_yang_dibayar_dari_usaha_utama":   "jumlah_pekerja_yang_dibayar_dari_usaha_utama",
    "jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama": "jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama",
    "penglihatan":                     "penglihatan",
    "pendengaran":                     "pendengaran",
    "berjalan_atau_naik_tangga":       "berjalan_atau_naik_tangga",
    "menggunakan_tangan_jari":         "menggunakan_tangan_jari",
    "mengingat_berkonsentrasi":        "mengingat_berkonsentrasi",
    "mengurus_diri":                   "mengurus_diri",
    "berbicara_komunikasi":            "berbicara_komunikasi",
    "belajar_kemampuan_intelektual":   "belajar_kemampuan_intelektual",
    "pengendalian_perilaku":           "pengendalian_perilaku",
    "kesedihan_depresi":               "kesedihan_depresi",
    "kondisi_gizi":                    "kondisi_gizi",
    "penyakit_kronis":                 "penyakit_kronis",
    "pbi_nas":                         "pbi_nas",
    "pbi_pemda":                       "pbi_pemda",
    "id_pelanggan_pln":                "id_pelanggan_pln",
}

# ---------------------------------------------------------------------------
# Mapping field_key → nama kolom di ZawaKeluarga
# ---------------------------------------------------------------------------
_KELUARGA_COLUMN_MAP: dict[str, str] = {
    "nomor_kartu_keluarga":              "nomor_kartu_keluarga",
    "nama_anggota_keluarga":             "nama_anggota_keluarga",
    "jumlah_anggota_keluarga":           "jumlah_anggota_keluarga",
    "alamat":                            "alamat",
    "kelurahan_desa":                    "kelurahan_desa",
    "kecamatan":                         "kecamatan",
    "kabupaten_kota":                    "kabupaten_kota",
    "provinsi":                          "provinsi",
    "kode_kelurahan_desa":               "kode_kelurahan_desa",
    "kode_kecamatan":                    "kode_kecamatan",
    "kode_kabupaten_kota":               "kode_kabupaten_kota",
    "kode_provinsi":                     "kode_provinsi",
    "luas_lantai":                       "luas_lantai",
    "jenis_lantai_terluas":              "jenis_lantai_terluas",
    "jenis_dinding_terluas":             "jenis_dinding_terluas",
    "jenis_atap_terluas":                "jenis_atap_terluas",
    "jenis_kloset":                      "jenis_kloset",
    "fasilitas_bab":                     "fasilitas_bab",
    "sumber_air_minum_utama":            "sumber_air_minum_utama",
    "sumber_penerangan_utama":           "sumber_penerangan_utama",
    "bahan_bakar_utama_memasak":         "bahan_bakar_utama_memasak",
    "daya_terpasang":                    "daya_terpasang",
    "pembuangan_akhir_tinja":            "pembuangan_akhir_tinja",
    "status_kepemilikan_rumah":          "status_kepemilikan_rumah",
    "kepemilikan_aset":                  "kepemilikan_aset",
    "aset_bergerak_sepeda_motor":        "aset_bergerak_sepeda_motor",
    "aset_bergerak_mobil":               "aset_bergerak_mobil",
    "aset_bergerak_sepeda":              "aset_bergerak_sepeda",
    "aset_bergerak_perahu":              "aset_bergerak_perahu",
    "aset_bergerak_kapal_perahu_motor":  "aset_bergerak_kapal_perahu_motor",
    "aset_bergerak_smartphone":          "aset_bergerak_smartphone",
    "aset_bergerak_komputer_laptop_tablet": "aset_bergerak_komputer_laptop_tablet",
    "aset_bergerak_lemari_es":           "aset_bergerak_lemari_es",
    "aset_bergerak_ac":                  "aset_bergerak_ac",
    "aset_bergerak_tv_datar":            "aset_bergerak_tv_datar",
    "aset_bergerak_emas_perhiasan":      "aset_bergerak_emas_perhiasan",
    "aset_bergerak_tabung_gas":          "aset_bergerak_tabung_gas",
    "aset_bergerak_pemanas_air":         "aset_bergerak_pemanas_air",
    "aset_bergerak_telepon_rumah":       "aset_bergerak_telepon_rumah",
    "aset_tidak_bergerak_rumah_lainnya": "aset_tidak_bergerak_rumah_lainnya",
    "aset_tidak_bergerak_lahan_lainnya": "aset_tidak_bergerak_lahan_lainnya",
    "jumlah_ternak_sapi":               "jumlah_ternak_sapi",
    "jumlah_ternak_kerbau":             "jumlah_ternak_kerbau",
    "jumlah_ternak_kuda":               "jumlah_ternak_kuda",
    "jumlah_ternak_kambing_domba":      "jumlah_ternak_kambing_domba",
    "jumlah_ternak_babi":               "jumlah_ternak_babi",
    "pbi_nas":                          "pbi_nas",
    "pbi_pemda":                        "pbi_pemda",
    "desil_nasional":                   "desil_nasional",
    "id_pelanggan_pln":                 "id_pelanggan_pln",
}

# Field ternak yang menggunakan filter range (nilai: "0", "1-5", ">5")
_TERNAK_RANGE_FIELDS = {
    "jumlah_ternak_sapi",
    "jumlah_ternak_kerbau",
    "jumlah_ternak_kuda",
    "jumlah_ternak_kambing_domba",
    "jumlah_ternak_babi",
}

# Kumpulan param yang bukan bagian dari filter dinamis (sudah ditangani secara eksplisit)
# usia_min dan usia_max ditangani khusus via _apply_usia_filter, bukan _apply_extra_filters
# total_count dikirim frontend saat pagination page > 1 untuk menghindari re-count
_RESERVED_PARAMS = {
    'provinsi', 'cursor', 'search', 'kabkota_kode', 'kecamatan_kode',
    'usia_min', 'usia_max', 'total_count',
}

# Kolom internal yang tidak perlu dikembalikan ke client
_EXCLUDE_COLUMNS = {"id", "synced_at", "provinsi_slug"}
_ENCRYPT_FIELDS = {
    "nomor_induk_kependudukan",
    "nomor_kartu_keluarga",
    "tanggal_lahir",
    "alamat_ktp",
}
_ENCRYPT_KELUARGA_FIELDS = {
    "nomor_kartu_keluarga",
    "alamat",
}

# ─── Kode wilayah normalizer ────────────────────────────────

def _normalize_kode(raw: str) -> tuple[str, str]:
    s = raw.strip()
    if '.' in s:
        plain  = s.replace('.', '')
        dotted = s
        return dotted, plain
    digits = re.sub(r'\D', '', s)
    if len(digits) == 4:
        dotted = f"{digits[:2]}.{digits[2:]}"
    elif len(digits) == 6:
        dotted = f"{digits[:2]}.{digits[2:4]}.{digits[4:]}"
    elif len(digits) == 10:
        dotted = f"{digits[:2]}.{digits[2:4]}.{digits[4:6]}.{digits[6:]}"
    else:
        dotted = s
    return dotted, digits


def _kode_filter(column, raw: str):
    dotted, plain = _normalize_kode(raw)
    if dotted == plain:
        return column == raw
    return db.or_(column == dotted, column == plain)


# ─── Provinsi resolver ──────────────────────────────────

def _resolve_provinsi(raw: str):
    if not raw:
        return None, None
    val = raw.lower().strip()
    if val in PROVINSI_MAP:
        return val, PROVINSI_MAP[val]
    if re.fullmatch(r'\d{1,2}', val):
        bps  = val.zfill(2)
        slug = _BPS_TO_SLUG.get(bps)
        if slug:
            return slug, PROVINSI_MAP[slug]
    return None, None


# ─── Identity & Access Control ───────────────────────────

def _current_identity() -> dict:
    return parse_identity_str(get_jwt_identity())

def _is_tuser(identity: dict) -> bool:
    return identity.get('type') in ('tuser', 'admin', 'user')

def _get_dtsen_akses(identity: dict) -> TDtsenAkses | None:
    if _is_tuser(identity):
        return None
    return TDtsenAkses.query.filter_by(dtsen_akses_id=identity.get('id')).first()

def _laz_skala(dtsen: TDtsenAkses | None) -> int | None:
    return dtsen.laz_skala if dtsen else None

def _allowed_provinsi_kodes(identity: dict) -> list[str] | None:
    """
    Kembalikan list kode BPS provinsi yang diizinkan untuk identity ini.
    - None  → superadmin / tuser, boleh akses semua provinsi
    - []    → tidak ada akses (dtsen tidak ditemukan)
    - ["32", "33", ...] → list kode BPS 2-digit yang diizinkan

    Frontend mengirim kode BPS (misal "32") sebagai parameter 'provinsi',
    sehingga validasi akses langsung dibandingkan dengan kode BPS.
    """
    if _is_tuser(identity):
        return None
    dtsen = _get_dtsen_akses(identity)
    if dtsen is None:
        return []
    rows = TDtsenWilayah.query.filter_by(dtsen_akses_id=dtsen.dtsen_akses_id).all()
    allowed = []
    for row in rows:
        prov_kode = (row.provinsi_kode or '').strip().zfill(2)
        if prov_kode and prov_kode not in allowed:
            allowed.append(prov_kode)
    return allowed

def _get_allowed_kabkota(identity: dict) -> list[str] | None:
    if _is_tuser(identity):
        return None
    dtsen = _get_dtsen_akses(identity)
    if dtsen is None:
        return []
    if _laz_skala(dtsen) == 1:
        return None
    rows = TDtsenWilayah.query.filter_by(dtsen_akses_id=dtsen.dtsen_akses_id).all()
    return list({r.kabkota_kode for r in rows if r.kabkota_kode})

def _get_allowed_kecamatan(identity: dict) -> list[str] | None:
    if _is_tuser(identity):
        return None
    dtsen = _get_dtsen_akses(identity)
    if dtsen is None:
        return []
    if _laz_skala(dtsen) in (1, 2):
        return None
    rows = TDtsenWilayah.query.filter_by(dtsen_akses_id=dtsen.dtsen_akses_id).all()
    return list({r.kecamatan_kode for r in rows if r.kecamatan_kode})

def _get_wilayah_scope(identity: dict) -> dict:
    if _is_tuser(identity):
        return {
            'skala': 0, 'skala_label': 'superadmin',
            'provinsi': None, 'kabkota': None, 'kecamatan': None,
            'drilldown': ['provinsi', 'kabkota', 'kecamatan'],
        }
    dtsen = _get_dtsen_akses(identity)
    if dtsen is None:
        return {'skala': None, 'drilldown': []}
    skala = _laz_skala(dtsen) or 0
    rows  = TDtsenWilayah.query.filter_by(dtsen_akses_id=dtsen.dtsen_akses_id).all()
    provinsi_list  = list({r.provinsi_kode  for r in rows if r.provinsi_kode})
    kabkota_list   = list({r.kabkota_kode   for r in rows if r.kabkota_kode})
    kecamatan_list = list({r.kecamatan_kode for r in rows if r.kecamatan_kode})
    SKALA_LABEL    = {1: 'nasional', 2: 'provinsi', 3: 'kabkota'}
    SKALA_DRILLDOWN = {
        1: ['provinsi', 'kabkota', 'kecamatan'],
        2: ['kabkota', 'kecamatan'],
        3: ['kecamatan'],
    }
    return {
        'skala':       skala,
        'skala_label': SKALA_LABEL.get(skala, 'unknown'),
        'laz_kode':    dtsen.laz_kode,
        'laz_nama':    dtsen.laz.laz_nama if dtsen.laz else None,
        'provinsi':    provinsi_list,
        'kabkota':     kabkota_list   if skala >= 2 else None,
        'kecamatan':   kecamatan_list if skala >= 3 else None,
        'drilldown':   SKALA_DRILLDOWN.get(skala, []),
    }


# ─── Wilayah scope endpoint ──────────────────────────────

@api_v1_bp.get('/baseline/wilayah-scope')
@jwt_required()
def baseline_wilayah_scope():
    return jsonify(_get_wilayah_scope(_current_identity())), 200


# ─── ZAWA HTTP helpers ──────────────────────────────────

def _zawa_headers() -> dict:
    api_key = os.environ.get("ZAWA_API_KEY", "")
    headers = {"Accept": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key
    else:
        logger.warning("[Baseline] ZAWA_API_KEY tidak di-set!")
    return headers

def _is_numeric_id(s: str) -> bool:
    return bool(re.fullmatch(r'\d{10,}', s.strip()))

def _is_nkk(s: str) -> bool:
    return bool(re.fullmatch(r'\d{16}', s.strip()))

def _row_to_dict(row) -> dict:
    """
    Serializer response DTSEN.

    Field yang dienkripsi:
    - NIK
    - NKK
    - tanggal lahir
    - alamat KTP

    Field yang tetap:
    - nama
    - wilayah kode
    - data statistik
    """

    d = {
        c.name: getattr(row, c.name)
        for c in row.__table__.columns
    }


    for col in _EXCLUDE_COLUMNS:
        d.pop(col, None)


    for field in _ENCRYPT_FIELDS:

        if field in d:

            value = d.pop(field)

            d[f"{field}_encrypt"] = encrypt_identifier(value)


    return d

def _row_to_detail_dict(row) -> dict:
    """
    Serializer detail anggota.

    Berbeda dengan list:
    - tidak melakukan encrypt field
    - dipakai setelah akses melalui hash berhasil
    """

    d = {
        c.name: getattr(row, c.name)
        for c in row.__table__.columns
    }

    for col in _EXCLUDE_COLUMNS:
        d.pop(col, None)

    return d


def _ok_payload(items, label, provinsi, meta_override=None):
    columns = list(items[0].keys()) if items else []
    meta = {
        "provinsi": provinsi, "label": label,
        "totalItems": len(items), "totalPages": 1, "currentPage": 1,
        "hasNextPage": False, "hasPreviousPage": False,
        "nextCursor": None, "limit": max(len(items), 1), "searchMode": "by_id",
    }
    if meta_override:
        meta.update(meta_override)
    return jsonify({"data": items, "columns": columns, "meta": meta}), 200

def _err_200(message: str, label: str, provinsi: str):
    return jsonify({
        "data": [], "columns": [],
        "meta": {
            "provinsi": provinsi, "label": label,
            "totalItems": 0, "totalPages": 1, "currentPage": 1,
            "hasNextPage": False, "hasPreviousPage": False,
            "nextCursor": None, "limit": 0, "searchMode": "by_id",
            "errorMessage": message,
        }
    }), 200

def _fetch_zawa_page(zawa_path: str, params: dict = None):
    cache_key = f"{zawa_path}:{sorted((params or {}).items())}"
    now = time.time()
    cached = _CACHE.get(cache_key)
    if cached and (now - cached["ts"]) < CACHE_TTL:
        return cached["payload"], None
    url = f"{ZAWA_BASE}/{zawa_path}"
    logger.info(f"[Baseline] fetch ZAWA url={url} params={params}")
    try:
        resp = requests.get(url, params=params or {}, timeout=ZAWA_TIMEOUT, headers=_zawa_headers())
        resp.raise_for_status()
        raw = resp.json()
    except requests.exceptions.SSLError as e:
        return None, f"SSL error: {e}"
    except requests.exceptions.ConnectionError as e:
        return None, f"Tidak dapat terhubung ke ZAWA: {e}"
    except requests.exceptions.Timeout:
        return None, "Timeout saat menghubungi ZAWA."
    except requests.exceptions.HTTPError as e:
        return None, f"ZAWA error: {e}"
    except Exception as e:
        logger.error(f"[Baseline] error path={zawa_path}: {e}", exc_info=True)
        return None, f"Error tidak terduga: {e}"
    data_obj = raw.get("data", {})
    if not isinstance(data_obj, dict):
        return None, "Format response ZAWA tidak dikenal."
    items = data_obj.get("items") or []
    payload = {
        "items":           items,
        "totalItems":      data_obj.get("totalItems", 0),
        "totalPages":      data_obj.get("totalPages", 1),
        "currentPage":     data_obj.get("currentPage", 1),
        "hasNextPage":     data_obj.get("hasNextPage", False),
        "hasPreviousPage": data_obj.get("hasPreviousPage", False),
        "nextCursor":      data_obj.get("nextCursor"),
        "limit":           data_obj.get("limit", ZAWA_LIMIT),
        "search_mode":     "list",
    }
    _CACHE[cache_key] = {"payload": payload, "ts": now}
    return payload, None

def _fetch_by_id(zawa_path: str, param_name: str, id_val, cache_prefix: str):
    cache_key = f"{cache_prefix}:{id_val}"
    now = time.time()
    cached = _CACHE.get(cache_key)
    if cached and (now - cached["ts"]) < CACHE_TTL:
        return cached["payload"], None, False
    url = f"{ZAWA_BASE}/{zawa_path}"
    try:
        resp = requests.get(url, params={param_name: id_val},
                            timeout=ZAWA_TIMEOUT, headers=_zawa_headers())
        if resp.status_code == 404:
            return None, None, True
        resp.raise_for_status()
        raw = resp.json()
    except requests.exceptions.Timeout:
        return None, "Timeout saat menghubungi ZAWA.", False
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else 0
        body   = e.response.text[:200] if e.response is not None else ""
        return None, f"ZAWA error {status}: {body}", False
    except Exception as e:
        logger.error(f"[Baseline] by-id error: {e}", exc_info=True)
        return None, f"Error: {e}", False
    data_obj = raw.get("data")
    if isinstance(data_obj, list):
        items = data_obj
    elif isinstance(data_obj, dict):
        items = data_obj.get("items") or data_obj.get("data") or []
        if not items and any(k not in (
            "items", "data", "limit", "currentPage", "totalItems",
            "totalPages", "hasNextPage", "hasPreviousPage", "nextCursor"
        ) for k in data_obj):
            items = [data_obj]
    else:
        items = []
    payload = {
        "items": items, "totalItems": len(items), "totalPages": 1,
        "currentPage": 1, "hasNextPage": False, "hasPreviousPage": False,
        "nextCursor": None, "limit": max(len(items), 1), "search_mode": "by_id",
    }
    _CACHE[cache_key] = {"payload": payload, "ts": now}
    return payload, None, False

def _build_table_response(payload, label, provinsi):
    rows    = payload["items"]
    columns = list(rows[0].keys()) if rows else []
    return jsonify({
        "data": rows, "columns": columns,
        "meta": {
            "provinsi": provinsi, "label": label,
            "totalItems":      payload["totalItems"],
            "totalPages":      payload["totalPages"],
            "currentPage":     payload["currentPage"],
            "hasNextPage":     payload["hasNextPage"],
            "hasPreviousPage": payload["hasPreviousPage"],
            "nextCursor":      payload["nextCursor"],
            "limit":           payload["limit"],
            "searchMode":      payload.get("search_mode", "list"),
        }
    }), 200

def _parse_db_cursor(cursor: str):
    if cursor and cursor.startswith("db:page_"):
        try:
            return int(cursor[len("db:page_"):])
        except ValueError:
            pass
    return None

def _build_db_cursor(page: int) -> str:
    return f"db:page_{page}"


# ─── DB cache helpers ───────────────────────────────────

def _cache_anggota_to_db(items: list, provinsi_slug: str):
    """
    Simpan anggota ke DB. provinsi_slug dipakai sebagai fallback,
    tapi kode_provinsi_ktp selalu menjadi sumber utama untuk menentukan
    provinsi_slug yang benar agar data tidak salah label.
    """
    if not items:
        return 0
    saved = 0
    for row in items:
        nik = str(row.get("nomor_induk_kependudukan", "") or "").strip()
        if not nik:
            continue

        # FIX: Selalu prioritaskan kode_provinsi_ktp sebagai sumber provinsi_slug.
        # Jika tidak tersedia atau tidak dikenal, baru gunakan provinsi_slug parameter.
        kode_prov_ktp = str(row.get("kode_provinsi_ktp") or "").strip().zfill(2)
        correct_slug  = _BPS_TO_SLUG.get(kode_prov_ktp)
        if not correct_slug:
            # Coba dari 2 digit pertama NIK sebagai fallback kedua
            nik_bps = nik[:2].zfill(2)
            correct_slug = _BPS_TO_SLUG.get(nik_bps) or provinsi_slug

        existing = ZawaAnggota.query.filter_by(nomor_induk_kependudukan=nik).first()
        if existing:
            # Perbaiki provinsi_slug jika selama ini salah
            if existing.provinsi_slug != correct_slug and correct_slug:
                existing.provinsi_slug = correct_slug
                db.session.add(existing)
            continue

        db.session.add(ZawaAnggota.from_api(row, correct_slug))
        saved += 1
    db.session.commit()
    return saved


def _upsert_keluarga_from_api_item(item: dict) -> str:
    nkk = str(item.get("nomor_kartu_keluarga") or "").strip()
    if not nkk:
        return 'error'
    try:
        if ZawaKeluarga.query.filter_by(nomor_kartu_keluarga=nkk).first():
            return 'skipped'
        db.session.add(ZawaKeluarga.from_api(item))
        db.session.commit()
        return 'saved'
    except Exception as e:
        db.session.rollback()
        logger.warning(f"[Sync] gagal insert keluarga NKK={nkk}: {e}")
        return 'error'


def _dedupe_by_nik(items: list) -> list:
    seen: set = set()
    result = []
    for item in items or []:
        nik = str(item.get("nomor_induk_kependudukan") or "").strip()
        if not nik or nik in seen:
            continue
        seen.add(nik)
        result.append(item)
    return result


# ---------------------------------------------------------------------------
# Helper: parse nilai range ternak
# "0"   → col == 0
# "1-5" → col BETWEEN 1 AND 5
# ">5"  → col > 5
# ---------------------------------------------------------------------------
def _parse_range_value(val: str):
    """
    Kembalikan tuple (mode, low, high) untuk dipakai di query:
      mode='eq'      → col == low
      mode='between' → col BETWEEN low AND high
      mode='gt'      → col > low
    Jika format tidak dikenal, return None.
    """
    val = val.strip()
    # Format ">N"
    m = re.fullmatch(r'>\s*(\d+)', val)
    if m:
        return ('gt', int(m.group(1)), None)
    # Format "N-M"
    m = re.fullmatch(r'(\d+)\s*-\s*(\d+)', val)
    if m:
        return ('between', int(m.group(1)), int(m.group(2)))
    # Format angka tunggal "0", "1", dst.
    m = re.fullmatch(r'\d+', val)
    if m:
        return ('eq', int(val), None)
    return None


# ---------------------------------------------------------------------------
# Helper: terapkan extra_filters ke SQLAlchemy query
# Mendukung filter range untuk field ternak ("0", "1-5", ">5")
# ---------------------------------------------------------------------------
def _apply_extra_filters(q, model, column_map: dict, extra_filters: dict):
    """Terapkan filter dinamis dari m_tampilan_dtsen ke query SQLAlchemy.

    - Field ternak: nilai range "0" / "1-5" / ">5" dikonversi ke kondisi numerik.
    - Field string: ilike (case-insensitive partial match).
    - Field numerik lain: exact match.
    """
    for field_key, val in extra_filters.items():
        if val is None or val == '':
            continue
        col_name = column_map.get(field_key)
        if not col_name:
            logger.debug(f"[Filter] field_key '{field_key}' tidak ada di column_map, dilewati.")
            continue
        col = getattr(model, col_name, None)
        if col is None:
            logger.debug(f"[Filter] kolom '{col_name}' tidak ada di model, dilewati.")
            continue

        # --- Filter range untuk field ternak ---
        if field_key in _TERNAK_RANGE_FIELDS:
            parsed = _parse_range_value(str(val))
            if parsed is None:
                logger.debug(f"[Filter] nilai range '{val}' untuk '{field_key}' tidak dikenal, dilewati.")
                continue
            mode, low, high = parsed
            if mode == 'eq':
                q = q.filter(col == low)
            elif mode == 'between':
                q = q.filter(col.between(low, high))
            elif mode == 'gt':
                q = q.filter(col > low)
            continue

        # --- Filter non-ternak ---
        col_type = str(col.property.columns[0].type).upper()
        if any(t in col_type for t in ('VARCHAR', 'TEXT', 'CHAR', 'STRING')):
            q = q.filter(col.ilike(f"%{val}%"))
        else:
            try:
                q = q.filter(col == type(col.property.columns[0].type.python_type())(val))
            except Exception:
                q = q.filter(col == val)
    return q


# ---------------------------------------------------------------------------
# Helper: filter usia — konversi usia_min/usia_max ke range tanggal_lahir
#
# tanggal_lahir disimpan sebagai VARCHAR(30) dengan format 'YYYY-MM-DD'.
# Logika konversi:
#   usia >= usia_min  →  tanggal_lahir <= TODAY - usia_min tahun
#   usia <= usia_max  →  tanggal_lahir >= TODAY - usia_max tahun
#
# Contoh: usia_min=20, usia_max=40 pada tanggal 2026-07-23
#   tgl_lahir_max = '2006-07-23'  (usia minimal 20)
#   tgl_lahir_min = '1986-07-23'  (usia maksimal 40)
#   → filter: tanggal_lahir BETWEEN '1986-07-23' AND '2006-07-23'
# ---------------------------------------------------------------------------
def _apply_usia_filter(q, usia_min_raw, usia_max_raw):
    """Terapkan filter rentang usia ke query ZawaAnggota.

    Param:
        usia_min_raw: nilai string/int usia minimum (inklusif), atau None/''.
        usia_max_raw: nilai string/int usia maksimum (inklusif), atau None/''.

    Return:
        Query SQLAlchemy yang sudah ditambah filter tanggal_lahir jika perlu.
    """
    try:
        usia_min = int(usia_min_raw) if usia_min_raw not in (None, '', '0') else None
    except (ValueError, TypeError):
        usia_min = None
    try:
        usia_max = int(usia_max_raw) if usia_max_raw not in (None, '', '100') else None
    except (ValueError, TypeError):
        usia_max = None

    # Jika keduanya default (0-100), tidak perlu filter
    if usia_min is None and usia_max is None:
        return q

    today = date.today()

    def subtract_years(d: date, years: int) -> date:
        """Kurangi tahun dari date, handle 29 Feb dengan aman."""
        try:
            return d.replace(year=d.year - years)
        except ValueError:
            # 29 Feb → 28 Feb di tahun non-kabisat
            return d.replace(year=d.year - years, day=28)

    if usia_min is not None and usia_max is not None:
        # Anggota dengan usia dalam rentang [usia_min, usia_max]
        tgl_lahir_min = subtract_years(today, usia_max).strftime('%Y-%m-%d')
        tgl_lahir_max = subtract_years(today, usia_min).strftime('%Y-%m-%d')
        q = q.filter(ZawaAnggota.tanggal_lahir.between(tgl_lahir_min, tgl_lahir_max))
        logger.debug(
            f"[Filter Usia] usia {usia_min}–{usia_max} → "
            f"tanggal_lahir BETWEEN '{tgl_lahir_min}' AND '{tgl_lahir_max}'"
        )
    elif usia_min is not None:
        # Hanya batas bawah usia: lahir ≤ today - usia_min
        tgl_lahir_max = subtract_years(today, usia_min).strftime('%Y-%m-%d')
        q = q.filter(ZawaAnggota.tanggal_lahir <= tgl_lahir_max)
        logger.debug(f"[Filter Usia] usia >= {usia_min} → tanggal_lahir <= '{tgl_lahir_max}'")
    elif usia_max is not None:
        # Hanya batas atas usia: lahir ≥ today - usia_max
        tgl_lahir_min = subtract_years(today, usia_max).strftime('%Y-%m-%d')
        q = q.filter(ZawaAnggota.tanggal_lahir >= tgl_lahir_min)
        logger.debug(f"[Filter Usia] usia <= {usia_max} → tanggal_lahir >= '{tgl_lahir_min}'")

    return q


# ─── SYNC ENDPOINTS ────────────────────────────────────

@api_v1_bp.get('/baseline/anggota/by-nkk/<string:nkk_hash>')
@jwt_required()
def baseline_anggota_by_nkk_hash(nkk_hash):

    try:
        nkk = decrypt_identifier(nkk_hash)

    except Exception:
        return jsonify({
            "error":"Token NKK tidak valid."
        }),400


    if not nkk:
        return jsonify({
            "error":"NKK kosong."
        }),400

@api_v1_bp.get('/baseline/keluarga/detail/<string:nkk_hash>')
@jwt_required()
def baseline_keluarga_detail_hash(nkk_hash):

    nkk = decrypt_identifier(nkk_hash)

    row = ZawaKeluarga.query.filter_by(
        nomor_kartu_keluarga=nkk
    ).first()

    if not row:
        return jsonify({
            "error":"Data keluarga tidak ditemukan"
        }),404


    return jsonify({
        "data": _row_to_detail_dict(row)
    }),200

@api_v1_bp.post('/baseline/sync/anggota')
@jwt_required()
def baseline_sync_anggota():
    body         = request.get_json(silent=True) or {}
    provinsi_req = (body.get("provinsi") or "").lower().strip()
    targets = {provinsi_req: PROVINSI_MAP[provinsi_req]} if provinsi_req and provinsi_req in PROVINSI_MAP else PROVINSI_MAP
    if provinsi_req and provinsi_req not in PROVINSI_MAP:
        return jsonify({"error": f"Kode provinsi '{provinsi_req}' tidak dikenal."}), 400

    hasil = []
    for slug, info in targets.items():
        log = ZawaSyncLog(
            sync_type=f"anggota:{slug}", provinsi_slug=slug,
            status="running", started_at=datetime.utcnow(),
        )
        db.session.add(log)
        db.session.commit()

        total_fetched = total_saved = 0
        cursor = error_msg = None
        try:
            while total_fetched < SYNC_MAX_ANGGOTA_PER_PROVINSI:
                sisa   = SYNC_MAX_ANGGOTA_PER_PROVINSI - total_fetched
                params = {"cursor": cursor} if cursor else {}
                payload, err = _fetch_zawa_page(f"zawa/{info['slug']}", params)
                if err:
                    error_msg = err
                    break
                items = payload["items"]
                if not items:
                    break
                if len(items) > sisa:
                    items = items[:sisa]
                total_fetched += len(items)
                total_saved   += _cache_anggota_to_db(items, slug)
                if not payload["hasNextPage"] or not payload["nextCursor"]:
                    break
                cursor = payload["nextCursor"]
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[Sync] anggota {slug} error: {e}", exc_info=True)

        log.status        = "failed" if error_msg else "success"
        log.total_fetched = total_fetched
        log.total_saved   = total_saved
        log.error_message = error_msg
        log.finished_at   = datetime.utcnow()
        db.session.commit()

        hasil.append({
            "provinsi": slug, "label": info["label"],
            "total_fetched": total_fetched, "total_saved": total_saved,
            "status": log.status, "error": error_msg,
            "durasi_detik": log.duration_seconds(),
        })

    return jsonify({
        "message": f"Sync anggota selesai. {len(hasil)} provinsi diproses.",
        "batas_per_provinsi": SYNC_MAX_ANGGOTA_PER_PROVINSI,
        "hasil": hasil,
    }), 200


@api_v1_bp.post('/baseline/sync/keluarga')
@jwt_required()
def baseline_sync_keluarga():
    body      = request.get_json(silent=True) or {}
    batch_max = int(body.get("batch", SYNC_MAX_KELUARGA_PER_RUN))

    log = ZawaSyncLog(
        sync_type="keluarga_by_nkk", provinsi_slug=None,
        status="running", started_at=datetime.utcnow(),
    )
    db.session.add(log)
    db.session.commit()

    existing_nkk_subq = select(ZawaKeluarga.nomor_kartu_keluarga).scalar_subquery()
    pending_nkk_rows = (
        db.session.query(distinct(ZawaAnggota.nomor_kartu_keluarga))
        .filter(
            ZawaAnggota.nomor_kartu_keluarga.isnot(None),
            ZawaAnggota.nomor_kartu_keluarga != '',
            ~ZawaAnggota.nomor_kartu_keluarga.in_(existing_nkk_subq)
        )
        .limit(batch_max)
        .all()
    )
    pending_nkk = [row[0] for row in pending_nkk_rows]

    total_fetched = total_saved = total_skipped = total_error = 0
    error_msg = None

    logger.info(f"[Sync] keluarga: {len(pending_nkk)} NKK pending (batch_max={batch_max})")

    for nkk in pending_nkk:
        try:
            payload, err, not_found = _fetch_by_id(
                "zawa/keluarga-by-nik", "nomor_kartu_keluarga", nkk, "keluarga-by-nkk"
            )
            if not_found:
                total_skipped += 1
                continue
            if err:
                logger.warning(f"[Sync] keluarga NKK={nkk} error: {err}")
                total_error += 1
                continue

            total_fetched += 1
            items = payload.get("items", [])
            for item in items:
                result = _upsert_keluarga_from_api_item(item)
                if result == 'saved':
                    total_saved += 1
                elif result == 'skipped':
                    total_skipped += 1
                else:
                    total_error += 1

        except Exception as e:
            logger.error(f"[Sync] keluarga NKK={nkk} exception: {e}", exc_info=True)
            total_error += 1
            error_msg = str(e)

        time.sleep(0.05)

    log.status        = "failed" if (total_error > 0 and total_saved == 0) else "success"
    log.total_fetched = total_fetched
    log.total_saved   = total_saved
    log.total_skipped = total_skipped
    log.total_error   = total_error
    log.error_message = error_msg
    log.finished_at   = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "message":         "Sync keluarga selesai.",
        "total_nkk_pending": len(pending_nkk),
        "total_fetched":   total_fetched,
        "total_saved":     total_saved,
        "total_skipped":   total_skipped,
        "total_error":     total_error,
        "status":          log.status,
        "durasi_detik":    log.duration_seconds(),
    }), 200


@api_v1_bp.get('/baseline/sync/status')
@jwt_required()
def baseline_sync_status():
    logs = ZawaSyncLog.query.order_by(ZawaSyncLog.started_at.desc()).limit(20).all()
    return jsonify({
        "data": [
            {
                "id":            l.id,
                "sync_type":     l.sync_type,
                "provinsi_slug": l.provinsi_slug,
                "status":        l.status,
                "total_fetched": l.total_fetched,
                "total_saved":   l.total_saved,
                "total_skipped": l.total_skipped,
                "total_error":   l.total_error,
                "error_message": l.error_message,
                "started_at":    l.started_at.isoformat() if l.started_at else None,
                "finished_at":   l.finished_at.isoformat() if l.finished_at else None,
                "durasi_detik":  l.duration_seconds(),
            }
            for l in logs
        ]
    }), 200


# ─── READ ENDPOINTS ────────────────────────────────────

@api_v1_bp.get('/baseline/ping')
@jwt_required()
def baseline_ping():
    import socket
    results = {}
    host = "spl-satudata.kemenag.go.id"
    try:
        ip = socket.gethostbyname(host)
        results["dns"] = {"ok": True, "ip": ip}
    except Exception as e:
        results["dns"] = {"ok": False, "error": str(e)}
    try:
        s = socket.create_connection((host, 443), timeout=5)
        s.close()
        results["tcp_443"] = {"ok": True}
    except Exception as e:
        results["tcp_443"] = {"ok": False, "error": str(e)}
    t0 = time.time()
    try:
        resp = requests.get(f"{ZAWA_BASE}/zawa/anggota", timeout=30, headers=_zawa_headers())
        elapsed = round(time.time() - t0, 2)
        results["http_get"] = {"ok": resp.status_code < 400, "status": resp.status_code,
                               "elapsed": f"{elapsed}s", "sample": resp.text[:300]}
    except Exception as e:
        results["http_get"] = {"ok": False, "error": str(e)}
    results["api_key_configured"] = {"ok": bool(os.environ.get("ZAWA_API_KEY")),
                                      "set": bool(os.environ.get("ZAWA_API_KEY"))}
    return jsonify({"ok": all(v.get("ok") for v in results.values()),
                    "checks": results, "target": host}), 200


@api_v1_bp.get('/baseline/provinsi')
@jwt_required()
def baseline_provinsi_list():
    """
    Kembalikan daftar provinsi yang dapat diakses oleh identity ini.
    - value/kode: kode BPS 2-digit (dipakai frontend sebagai parameter 'provinsi')
    - label: nama provinsi (ditampilkan di UI)
    """
    identity = _current_identity()
    allowed  = _allowed_provinsi_kodes(identity)
    if allowed is None:
        # superadmin / tuser: semua provinsi
        items = sorted(
            [{"kode": v["bps"], "label": v["label"]}
             for k, v in PROVINSI_MAP.items()],
            key=lambda x: x["label"]
        )
    else:
        # filter berdasarkan kode BPS yang diizinkan
        bps_to_info = {v["bps"]: v for v in PROVINSI_MAP.values()}
        items = sorted(
            [{"kode": kode, "label": bps_to_info[kode]["label"]}
             for kode in allowed if kode in bps_to_info],
            key=lambda x: x["label"]
        )
    return jsonify({"data": items, "scope": _get_wilayah_scope(identity)}), 200


def _build_anggota_db_query(bps_kode: str,
                             kabkota_filter, kecamatan_filter, search: str,
                             extra_filters: dict = None,
                             usia_min=None, usia_max=None):
    # PERF: JOIN langsung ke zawa_keluarga, filter provinsi dengan satu kondisi
    # (tidak OR ganda) agar optimizer dapat memakai idx_anggota_wilayah_ktp optimal.
    q = ZawaAnggota.query.join(
        ZawaKeluarga,
        db.and_(
            ZawaAnggota.nomor_kartu_keluarga == ZawaKeluarga.nomor_kartu_keluarga,
            ZawaKeluarga.desil_nasional.in_(_DESIL_ALLOWED),
        )
    ).filter(
        ZawaAnggota.kode_provinsi_ktp == bps_kode
    )

    if kabkota_filter:
        q = q.filter(_kode_filter(ZawaAnggota.kode_kabupaten_kota_ktp, kabkota_filter))
    if kecamatan_filter:
        q = q.filter(_kode_filter(ZawaAnggota.kode_kecamatan_ktp, kecamatan_filter))
    if search:
        q_lower = f"%{search.lower()}%"
        q = q.filter(db.or_(
            ZawaAnggota.nama.ilike(q_lower),
            ZawaAnggota.nomor_induk_kependudukan.ilike(q_lower),
        ))
    if extra_filters:
        q = _apply_extra_filters(q, ZawaAnggota, _ANGGOTA_COLUMN_MAP, extra_filters)

    # Filter usia: konversi ke rentang tanggal_lahir
    q = _apply_usia_filter(q, usia_min, usia_max)

    return q


def _count_anggota_db_query(bps_kode: str,
                              kabkota_filter, kecamatan_filter, search: str,
                              extra_filters: dict = None,
                              usia_min=None, usia_max=None) -> int:
    """
    COUNT terpisah dari fetch data — menggunakan func.count() langsung
    tanpa subquery wrapping agar MySQL bisa memanfaatkan index secara optimal.
    Menghasilkan: SELECT COUNT(zawa_anggota.id) FROM ... JOIN ... WHERE ...
    """
    q = db.session.query(func.count(ZawaAnggota.id)).join(
        ZawaKeluarga,
        db.and_(
            ZawaAnggota.nomor_kartu_keluarga == ZawaKeluarga.nomor_kartu_keluarga,
            ZawaKeluarga.desil_nasional.in_(_DESIL_ALLOWED),
        )
    ).filter(
        ZawaAnggota.kode_provinsi_ktp == bps_kode
    )

    if kabkota_filter:
        q = q.filter(_kode_filter(ZawaAnggota.kode_kabupaten_kota_ktp, kabkota_filter))
    if kecamatan_filter:
        q = q.filter(_kode_filter(ZawaAnggota.kode_kecamatan_ktp, kecamatan_filter))
    if search:
        q_lower = f"%{search.lower()}%"
        q = q.filter(db.or_(
            ZawaAnggota.nama.ilike(q_lower),
            ZawaAnggota.nomor_induk_kependudukan.ilike(q_lower),
        ))
    if extra_filters:
        q = _apply_extra_filters(q, ZawaAnggota, _ANGGOTA_COLUMN_MAP, extra_filters)

    q = _apply_usia_filter(q, usia_min, usia_max)

    return q.scalar() or 0


def _count_keluarga_db_query(prov_bps, kabkota_filter, kecamatan_filter, search,
                               extra_filters=None) -> int:
    """
    COUNT untuk zawa_keluarga — func.count() langsung tanpa subquery wrapping.
    """
    q = db.session.query(func.count(ZawaKeluarga.id)).filter(
        ZawaKeluarga.desil_nasional.in_(_DESIL_ALLOWED)
    )
    if prov_bps:
        q = q.filter(ZawaKeluarga.kode_provinsi == prov_bps)
    if kabkota_filter:
        q = q.filter(_kode_filter(ZawaKeluarga.kode_kabupaten_kota, kabkota_filter))
    if kecamatan_filter:
        q = q.filter(_kode_filter(ZawaKeluarga.kode_kecamatan, kecamatan_filter))
    if search:
        q_lower = f"%{search.lower()}%"
        q = q.filter(db.or_(
            ZawaKeluarga.nomor_kartu_keluarga.ilike(q_lower),
            ZawaKeluarga.nama_anggota_keluarga.ilike(q_lower),
            ZawaKeluarga.alamat.ilike(q_lower),
            ZawaKeluarga.kelurahan_desa.ilike(q_lower),
            ZawaKeluarga.kecamatan.ilike(q_lower),
            ZawaKeluarga.kabupaten_kota.ilike(q_lower),
            ZawaKeluarga.provinsi.ilike(q_lower),
        ))
    if extra_filters:
        q = _apply_extra_filters(q, ZawaKeluarga, _KELUARGA_COLUMN_MAP, extra_filters)
    return q.scalar() or 0


@api_v1_bp.get('/baseline/anggota')
@jwt_required()
def baseline_anggota():
    identity = _current_identity()
    # allowed: list kode BPS yang diizinkan, atau None (akses semua)
    allowed  = _allowed_provinsi_kodes(identity)

    provinsi_raw     = request.args.get('provinsi', '').strip()
    cursor           = request.args.get('cursor') or None
    search           = request.args.get('search', '').strip()
    kabkota_filter   = request.args.get('kabkota_kode', '').strip() or None
    kecamatan_filter = request.args.get('kecamatan_kode', '').strip() or None

    # Ambil param usia (ditangani khusus, bukan melalui _apply_extra_filters)
    usia_min_raw = request.args.get('usia_min', '').strip() or None
    usia_max_raw = request.args.get('usia_max', '').strip() or None

    # total_count dari frontend (dipakai saat pagination page > 1 untuk skip re-count)
    total_count_param = request.args.get('total_count', '').strip() or None

    extra_filters = {
        k: v for k, v in request.args.items()
        if k not in _RESERVED_PARAMS and k in _ANGGOTA_COLUMN_MAP and v
    }

    if not provinsi_raw:
        return jsonify({"error": "Parameter 'provinsi' wajib diisi."}), 400

    # _resolve_provinsi menerima kode BPS (misal "32") atau slug ("jabar")
    provinsi, info = _resolve_provinsi(provinsi_raw)
    if not info:
        return jsonify({"error": f"Kode provinsi '{provinsi_raw}' tidak dikenal."}), 400

    bps_kode = info["bps"]

    # Validasi akses: bandingkan kode BPS (bukan slug)
    if allowed is not None and bps_kode not in allowed:
        return jsonify({"error": "Akses ditolak. Provinsi ini tidak termasuk wilayah Anda."}), 403

    kabkota_dotted = kabkota_plain = None
    if kabkota_filter:
        kabkota_dotted, kabkota_plain = _normalize_kode(kabkota_filter)
        allowed_kabkota = _get_allowed_kabkota(identity)
        if allowed_kabkota is not None:
            if kabkota_dotted not in allowed_kabkota and kabkota_plain not in allowed_kabkota:
                return jsonify({"error": "Akses ditolak."}), 403

    kecamatan_dotted = kecamatan_plain = None
    if kecamatan_filter:
        kecamatan_dotted, kecamatan_plain = _normalize_kode(kecamatan_filter)
        allowed_kec = _get_allowed_kecamatan(identity)
        if allowed_kec is not None:
            if kecamatan_dotted not in allowed_kec and kecamatan_plain not in allowed_kec:
                return jsonify({"error": "Akses ditolak."}), 403

    # --- NIK search path: langsung dari DB lokal, filter desil via join ---
    if search and _is_numeric_id(search):
        db_row = ZawaAnggota.query.filter(
            ZawaAnggota.nomor_induk_kependudukan == search.strip(),
            ZawaAnggota.kode_provinsi_ktp == bps_kode,
        ).first()
        if db_row:
            nkk_check = ZawaKeluarga.query.filter(
                ZawaKeluarga.nomor_kartu_keluarga == db_row.nomor_kartu_keluarga,
                ZawaKeluarga.desil_nasional.in_(_DESIL_ALLOWED),
            ).first()
            keluarga_any = ZawaKeluarga.query.filter_by(
                nomor_kartu_keluarga=db_row.nomor_kartu_keluarga
            ).first()
            if keluarga_any and not nkk_check:
                return _err_200(
                    "Data tidak tersedia (desil tidak termasuk 1-4).",
                    info["label"], provinsi_raw
                )
            if nkk_check:
                return _ok_payload([_row_to_dict(db_row)], info["label"], provinsi_raw,
                                   {"searchMode": "db_cache", "source": "local_db"})
        return _err_200(
            f"NIK {search} tidak ditemukan di database lokal.",
            info["label"], provinsi_raw
        )

    db_page = _parse_db_cursor(cursor) if cursor else 1
    if db_page is None:
        db_page = 1

    # PERF: Hanya jalankan COUNT di halaman pertama.
    # Halaman berikutnya mengambil total_count dari query param yang dikirim frontend.
    if db_page == 1 or not total_count_param:
        total_count = _count_anggota_db_query(
            bps_kode=bps_kode,
            kabkota_filter=kabkota_filter, kecamatan_filter=kecamatan_filter,
            search=search, extra_filters=extra_filters,
            usia_min=usia_min_raw, usia_max=usia_max_raw,
        )
    else:
        try:
            total_count = int(total_count_param)
        except (ValueError, TypeError):
            total_count = _count_anggota_db_query(
                bps_kode=bps_kode,
                kabkota_filter=kabkota_filter, kecamatan_filter=kecamatan_filter,
                search=search, extra_filters=extra_filters,
                usia_min=usia_min_raw, usia_max=usia_max_raw,
            )

    if total_count > 0:
        q = _build_anggota_db_query(
            bps_kode=bps_kode,
            kabkota_filter=kabkota_filter, kecamatan_filter=kecamatan_filter,
            search=search, extra_filters=extra_filters,
            usia_min=usia_min_raw, usia_max=usia_max_raw,
        )
        total_pages = max(1, -(-total_count // DB_PAGE_SIZE))
        offset      = (db_page - 1) * DB_PAGE_SIZE
        db_rows     = q.order_by(ZawaAnggota.id).offset(offset).limit(DB_PAGE_SIZE).all()
        items       = [_row_to_dict(r) for r in db_rows]
        has_next    = db_page < total_pages
        next_cur    = _build_db_cursor(db_page + 1) if has_next else None
        columns     = list(items[0].keys()) if items else []
        return jsonify({
            "data": items, "columns": columns,
            "meta": {
                "provinsi": provinsi_raw, "label": info["label"],
                "totalItems": total_count, "totalPages": total_pages,
                "currentPage": db_page, "hasNextPage": has_next,
                "hasPreviousPage": db_page > 1, "nextCursor": next_cur,
                "limit": DB_PAGE_SIZE, "searchMode": "db_cache", "source": "local_db",
            }
        }), 200

    return jsonify({
        "data": [], "columns": [],
        "meta": {
            "provinsi": provinsi_raw, "label": info["label"],
            "totalItems": 0, "totalPages": 1, "currentPage": 1,
            "hasNextPage": False, "hasPreviousPage": False,
            "nextCursor": None, "limit": DB_PAGE_SIZE,
            "searchMode": "db_cache", "source": "local_db",
            "errorMessage": "Tidak ada data yang sesuai. Pastikan sync sudah dilakukan.",
        }
    }), 200


@api_v1_bp.get('/baseline/anggota/detail/<string:nik_hash>')
@jwt_required()
def baseline_anggota_detail_hash(nik_hash):

    try:
        nik = decrypt_identifier(nik_hash)

    except Exception:
        return jsonify({
            "error": "Token NIK tidak valid."
        }), 400


    if not nik:
        return jsonify({
            "error": "NIK kosong."
        }), 400


    row = ZawaAnggota.query.filter_by(
        nomor_induk_kependudukan=nik
    ).first()


    if not row:
        return jsonify({
            "error": "Data anggota tidak ditemukan."
        }), 404


    return jsonify({
        "data": _row_to_detail_dict(row)
    }), 200

@api_v1_bp.get('/baseline/keluarga')
@jwt_required()
def baseline_keluarga():
    identity         = _current_identity()
    # allowed: list kode BPS yang diizinkan, atau None (akses semua)
    allowed          = _allowed_provinsi_kodes(identity)

    cursor           = request.args.get('cursor') or None
    search           = request.args.get('search', '').strip()
    provinsi_raw     = request.args.get('provinsi', '').strip() or None
    kabkota_filter   = request.args.get('kabkota_kode', '').strip() or None
    kecamatan_filter = request.args.get('kecamatan_kode', '').strip() or None

    # total_count dari frontend (dipakai saat pagination page > 1 untuk skip re-count)
    total_count_param = request.args.get('total_count', '').strip() or None

    extra_filters = {
        k: v for k, v in request.args.items()
        if k not in _RESERVED_PARAMS and k in _KELUARGA_COLUMN_MAP and v
    }

    prov_slug = prov_info = prov_bps = None
    if provinsi_raw:
        prov_slug, prov_info = _resolve_provinsi(provinsi_raw)
        if not prov_info:
            return jsonify({"error": f"Kode provinsi '{provinsi_raw}' tidak dikenal."}), 400
        prov_bps = prov_info["bps"]
        # Validasi akses: bandingkan kode BPS (bukan slug)
        if allowed is not None and prov_bps not in allowed:
            return jsonify({"error": "Akses ditolak."}), 403

    label = prov_info["label"] if prov_info else "Keluarga"
    label_provinsi = provinsi_raw or "nasional"

    kabkota_dotted = kabkota_plain = None
    if kabkota_filter:
        kabkota_dotted, kabkota_plain = _normalize_kode(kabkota_filter)
        allowed_kabkota = _get_allowed_kabkota(identity)
        if allowed_kabkota is not None:
            if kabkota_dotted not in allowed_kabkota and kabkota_plain not in allowed_kabkota:
                return jsonify({"error": "Akses ditolak."}), 403

    kecamatan_dotted = kecamatan_plain = None
    if kecamatan_filter:
        kecamatan_dotted, kecamatan_plain = _normalize_kode(kecamatan_filter)
        allowed_kec = _get_allowed_kecamatan(identity)
        if allowed_kec is not None:
            if kecamatan_dotted not in allowed_kec and kecamatan_plain not in allowed_kec:
                return jsonify({"error": "Akses ditolak."}), 403

    # --- NKK search path: langsung dari DB lokal ---
    if search and _is_nkk(search):
        db_row = ZawaKeluarga.query.filter(
            ZawaKeluarga.nomor_kartu_keluarga == search.strip(),
            ZawaKeluarga.desil_nasional.in_(_DESIL_ALLOWED),
        ).first()
        if db_row:
            return _ok_payload([_row_to_dict(db_row)], label, label_provinsi,
                               {"searchMode": "db_cache", "source": "local_db"})
        # Cek apakah ada di DB tapi desil tidak valid
        db_row_any = ZawaKeluarga.query.filter_by(nomor_kartu_keluarga=search.strip()).first()
        if db_row_any:
            return _err_200(
                "Data tidak tersedia (desil tidak termasuk 1-4).",
                label, label_provinsi
            )
        return _err_200(
            f"Nomor KK {search} tidak ditemukan di database lokal.",
            label, label_provinsi
        )

    db_page = _parse_db_cursor(cursor) if cursor else 1
    if db_page is None:
        db_page = 1

    # PERF: Hanya jalankan COUNT di halaman pertama.
    if db_page == 1 or not total_count_param:
        filtered_total = _count_keluarga_db_query(
            prov_bps=prov_bps,
            kabkota_filter=kabkota_filter, kecamatan_filter=kecamatan_filter,
            search=search, extra_filters=extra_filters,
        )
    else:
        try:
            filtered_total = int(total_count_param)
        except (ValueError, TypeError):
            filtered_total = _count_keluarga_db_query(
                prov_bps=prov_bps,
                kabkota_filter=kabkota_filter, kecamatan_filter=kecamatan_filter,
                search=search, extra_filters=extra_filters,
            )

    if filtered_total > 0:
        # Build query untuk fetch data (terpisah dari count)
        q = ZawaKeluarga.query.filter(
            ZawaKeluarga.desil_nasional.in_(_DESIL_ALLOWED)
        )
        if prov_bps:
            q = q.filter(ZawaKeluarga.kode_provinsi == prov_bps)
        if kabkota_dotted:
            q = q.filter(_kode_filter(ZawaKeluarga.kode_kabupaten_kota, kabkota_filter))
        if kecamatan_dotted:
            q = q.filter(_kode_filter(ZawaKeluarga.kode_kecamatan, kecamatan_filter))
        if search:
            q_lower = f"%{search.lower()}%"
            q = q.filter(db.or_(
                ZawaKeluarga.nomor_kartu_keluarga.ilike(q_lower),
                ZawaKeluarga.nama_anggota_keluarga.ilike(q_lower),
                ZawaKeluarga.alamat.ilike(q_lower),
                ZawaKeluarga.kelurahan_desa.ilike(q_lower),
                ZawaKeluarga.kecamatan.ilike(q_lower),
                ZawaKeluarga.kabupaten_kota.ilike(q_lower),
                ZawaKeluarga.provinsi.ilike(q_lower),
            ))
        if extra_filters:
            q = _apply_extra_filters(q, ZawaKeluarga, _KELUARGA_COLUMN_MAP, extra_filters)

        total_pages = max(1, -(-filtered_total // DB_PAGE_SIZE))
        offset      = (db_page - 1) * DB_PAGE_SIZE
        db_rows     = q.order_by(ZawaKeluarga.id).offset(offset).limit(DB_PAGE_SIZE).all()
        items       = [_row_to_dict(r) for r in db_rows]
        has_next    = db_page < total_pages
        next_cur    = _build_db_cursor(db_page + 1) if has_next else None
        columns     = list(items[0].keys()) if items else []
        return jsonify({
            "data": items, "columns": columns,
            "meta": {
                "provinsi": label_provinsi, "label": label,
                "totalItems": filtered_total, "totalPages": total_pages,
                "currentPage": db_page, "hasNextPage": has_next,
                "hasPreviousPage": db_page > 1, "nextCursor": next_cur,
                "limit": DB_PAGE_SIZE, "searchMode": "db_local", "source": "local_db",
            }
        }), 200

    return jsonify({
        "data": [], "columns": [],
        "meta": {
            "provinsi": label_provinsi, "label": label,
            "totalItems": 0, "totalPages": 1, "currentPage": 1,
            "hasNextPage": False, "hasPreviousPage": False,
            "nextCursor": None, "limit": DB_PAGE_SIZE,
            "searchMode": "db_local", "source": "local_db",
            "errorMessage": "Data belum tersedia di cache lokal atau tidak ada yang sesuai filter. Lakukan sync terlebih dahulu.",
        }
    }), 200


@api_v1_bp.get('/baseline')
@jwt_required()
def baseline_data():
    return baseline_anggota()


@api_v1_bp.delete('/baseline/cache')
@jwt_required()
def baseline_clear_cache():
    _CACHE.clear()
    return jsonify({"message": "Cache berhasil dikosongkan."}), 200


# ─── ENDPOINT: Repair provinsi_slug dari kode_provinsi_ktp ───

@api_v1_bp.post('/baseline/repair/provinsi-slug')
@jwt_required()
def baseline_repair_provinsi_slug():
    """
    Perbaiki data lama: update provinsi_slug berdasarkan kode_provinsi_ktp.
    Panggil sekali dari admin untuk migrasi data yang salah label.
    Fallback ke 2 digit pertama NIK jika kode_provinsi_ktp tidak tersedia.
    """
    updated = 0
    rows = ZawaAnggota.query.all()
    for row in rows:
        bps = str(row.kode_provinsi_ktp or '').strip().zfill(2)
        correct = _BPS_TO_SLUG.get(bps)
        if not correct:
            # Fallback: deteksi dari 2 digit pertama NIK
            nik = str(row.nomor_induk_kependudukan or '').strip()
            if nik:
                nik_bps = nik[:2].zfill(2)
                correct = _BPS_TO_SLUG.get(nik_bps)
        if correct and row.provinsi_slug != correct:
            row.provinsi_slug = correct
            updated += 1
    db.session.commit()
    logger.info(f"[Repair] provinsi_slug diperbaiki: {updated} baris")
    return jsonify({
        "message": f"Selesai. {updated} baris provinsi_slug diperbaiki.",
        "updated": updated,
    }), 200


@api_v1_bp.get('/baseline/anggota/detail/<string:nik_hash>/mustahik')
@jwt_required()
def baseline_anggota_mustahik_hash(nik_hash):

    try:
        nik = decrypt_identifier(nik_hash)

    except Exception:
        return jsonify({
            "error": "Token NIK tidak valid."
        }), 400


    if not nik:
        return jsonify({
            "error": "NIK kosong."
        }), 400


    result = MustahikService.get_detail_by_nik(nik)


    if result.get('status_code') == 404:
        return jsonify(result), 404


    return jsonify(result), 200