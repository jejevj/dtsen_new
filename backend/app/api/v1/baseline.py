import logging
import os
import re
import time
import requests
from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api_v1_bp
from ...extensions import db
from ...models.zawa import ZawaAnggota, ZawaKeluarga, ZawaSyncLog
from ...models.t_dtsen_wilayah import TDtsenWilayah
from ...models.t_dtsen_akses import TDtsenAkses
from ...services.auth_service import parse_identity_str

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

# Lookup cepat: bps_kode -> slug ZAWA
_BPS_TO_SLUG: dict[str, str] = {v["bps"]: k for k, v in PROVINSI_MAP.items()}

ZAWA_BASE    = "https://spl-satudata.kemenag.go.id/core/api"
ZAWA_TIMEOUT = 60
ZAWA_LIMIT   = 10

SYNC_MAX_ANGGOTA_PER_PROVINSI = 10_000
SYNC_MAX_KELUARGA_TOTAL       = 50_000

_CACHE: dict = {}
CACHE_TTL = 600


# ─────────────────────────────────────────────
# Helper: identity & kontrol akses berbasis skala LAZ
# ─────────────────────────────────────────────

def _current_identity() -> dict:
    return parse_identity_str(get_jwt_identity())


def _is_tuser(identity: dict) -> bool:
    return identity.get('type') in ('tuser', 'admin', 'user')


def _get_dtsen_akses(identity: dict) -> TDtsenAkses | None:
    """Ambil row TDtsenAkses beserta relasi laz (eager loaded)."""
    if _is_tuser(identity):
        return None
    return TDtsenAkses.query.filter_by(
        dtsen_akses_id=identity.get('id')
    ).first()


def _laz_skala(dtsen: TDtsenAkses | None) -> int | None:
    """Return skala LAZ (1/2/3) atau None jika tidak ada."""
    if dtsen is None:
        return None
    return dtsen.laz_skala


def _allowed_provinsi_slugs(identity: dict) -> list[str] | None:
    """
    Return daftar slug ZAWA provinsi yang boleh diakses.
    - tuser/admin          : None  (semua provinsi)
    - dtsen skala 1 (Nas.) : list provinsi_kode dari t_dtsen_wilayah -> slug
    - dtsen skala 2 (Prov.): list provinsi unik dari kabkota yang di-assign
    - dtsen skala 3 (Kabko): list provinsi dari kecamatan yang di-assign
    Skala 2 & 3 → provinsi tetap bisa difilter sebagai entry point dropdown,
    drilldown lebih lanjut dikontrol via endpoint wilayah terpisah.
    """
    if _is_tuser(identity):
        return None

    dtsen = _get_dtsen_akses(identity)
    if dtsen is None:
        return []

    skala = _laz_skala(dtsen)
    rows  = TDtsenWilayah.query.filter_by(dtsen_akses_id=dtsen.dtsen_akses_id).all()

    allowed = []
    for row in rows:
        prov_kode = (row.provinsi_kode or '').strip().zfill(2)
        slug = _BPS_TO_SLUG.get(prov_kode)
        if slug and slug not in allowed:
            allowed.append(slug)

    return allowed  # sama untuk skala 1, 2, 3 — provinsi selalu jadi entry point


def _get_allowed_kabkota(identity: dict) -> list[str] | None:
    """
    Return list kabkota_kode yang boleh diakses.
    - tuser/admin          : None (semua)
    - dtsen skala 1 (Nas.) : None (semua kabkota dalam provinsi yang dipilih)
    - dtsen skala 2 (Prov.): list kabkota_kode dari t_dtsen_wilayah
    - dtsen skala 3 (Kabko): list kabkota_kode dari t_dtsen_wilayah
    """
    if _is_tuser(identity):
        return None

    dtsen = _get_dtsen_akses(identity)
    if dtsen is None:
        return []

    skala = _laz_skala(dtsen)
    if skala == 1:
        return None  # nasional: bebas semua kabkota

    # skala 2 & 3: dibatasi oleh kabkota_kode di t_dtsen_wilayah
    rows = TDtsenWilayah.query.filter_by(dtsen_akses_id=dtsen.dtsen_akses_id).all()
    return list({r.kabkota_kode for r in rows if r.kabkota_kode})


def _get_allowed_kecamatan(identity: dict) -> list[str] | None:
    """
    Return list kecamatan_kode yang boleh diakses.
    - tuser/admin          : None (semua)
    - dtsen skala 1 (Nas.) : None (semua kecamatan)
    - dtsen skala 2 (Prov.): None (semua kecamatan dalam kabkota)
    - dtsen skala 3 (Kabko): list kecamatan_kode dari t_dtsen_wilayah
    """
    if _is_tuser(identity):
        return None

    dtsen = _get_dtsen_akses(identity)
    if dtsen is None:
        return []

    skala = _laz_skala(dtsen)
    if skala in (1, 2):
        return None  # nasional & provinsi: bebas semua kecamatan

    # skala 3: dibatasi oleh kecamatan_kode
    rows = TDtsenWilayah.query.filter_by(dtsen_akses_id=dtsen.dtsen_akses_id).all()
    return list({r.kecamatan_kode for r in rows if r.kecamatan_kode})


def _get_wilayah_scope(identity: dict) -> dict:
    """
    Kembalikan scope wilayah lengkap + metadata skala untuk dikirim ke frontend.
    Frontend menggunakan ini untuk menentukan drilldown mana yang aktif.
    """
    if _is_tuser(identity):
        return {
            'skala': 0,
            'skala_label': 'superadmin',
            'provinsi': None,
            'kabkota': None,
            'kecamatan': None,
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

    SKALA_LABEL = {1: 'nasional', 2: 'provinsi', 3: 'kabkota'}
    SKALA_DRILLDOWN = {
        1: ['provinsi', 'kabkota', 'kecamatan'],  # nasional: mulai dari provinsi
        2: ['kabkota', 'kecamatan'],              # provinsi: mulai dari kabkota
        3: ['kecamatan'],                          # kabkota : hanya kecamatan
    }

    return {
        'skala':        skala,
        'skala_label':  SKALA_LABEL.get(skala, 'unknown'),
        'laz_kode':     dtsen.laz_kode,
        'laz_nama':     dtsen.laz.laz_nama if dtsen.laz else None,
        'provinsi':     provinsi_list,
        'kabkota':      kabkota_list   if skala >= 2 else None,
        'kecamatan':    kecamatan_list if skala >= 3 else None,
        'drilldown':    SKALA_DRILLDOWN.get(skala, []),
    }


# ─────────────────────────────────────────────
# Endpoint baru: scope wilayah untuk frontend
# ─────────────────────────────────────────────

@api_v1_bp.get('/baseline/wilayah-scope')
@jwt_required()
def baseline_wilayah_scope():
    """
    Endpoint untuk frontend agar bisa tahu drilldown wilayah apa saja
    yang tersedia untuk user yang sedang login.

    Response contoh (skala 2 - Provinsi LAZ):
    {
      "skala": 2,
      "skala_label": "provinsi",
      "laz_kode": "LAZ-JBR",
      "laz_nama": "LAZ Jawa Barat",
      "provinsi": ["32"],
      "kabkota": ["3201", "3273"],
      "kecamatan": null,
      "drilldown": ["kabkota", "kecamatan"]
    }
    """
    identity = _current_identity()
    scope    = _get_wilayah_scope(identity)
    return jsonify(scope), 200


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
    if row.raw_data and isinstance(row.raw_data, dict):
        return row.raw_data
    d = {c.name: getattr(row, c.name) for c in row.__table__.columns}
    d.pop("raw_data", None)
    d.pop("synced_at", None)
    d.pop("id", None)
    return d


def _ok_payload(items, label, provinsi, meta_override=None):
    columns = list(items[0].keys()) if items else []
    meta = {
        "provinsi":        provinsi,
        "label":           label,
        "totalItems":      len(items),
        "totalPages":      1,
        "currentPage":     1,
        "hasNextPage":     False,
        "hasPreviousPage": False,
        "nextCursor":      None,
        "limit":           max(len(items), 1),
        "searchMode":      "by_id",
    }
    if meta_override:
        meta.update(meta_override)
    return jsonify({"data": items, "columns": columns, "meta": meta}), 200


def _err_200(message: str, label: str, provinsi: str):
    return jsonify({
        "data":    [],
        "columns": [],
        "meta": {
            "provinsi":    provinsi,
            "label":       label,
            "totalItems":  0,
            "totalPages":  1,
            "currentPage": 1,
            "hasNextPage": False,
            "hasPreviousPage": False,
            "nextCursor":  None,
            "limit":       0,
            "searchMode":  "by_id",
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
        logger.info(f"[Baseline] ZAWA status={resp.status_code} path={zawa_path}")
        resp.raise_for_status()
        raw = resp.json()
    except requests.exceptions.SSLError as e:
        return None, f"SSL error: {e}"
    except requests.exceptions.ConnectionError as e:
        return None, f"Tidak dapat terhubung ke ZAWA: {e}"
    except requests.exceptions.Timeout:
        return None, "Timeout saat menghubungi ZAWA. Coba lagi beberapa saat."
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
    logger.info(f"[Baseline] got {len(items)} items, total={payload['totalItems']} path={zawa_path}")
    _CACHE[cache_key] = {"payload": payload, "ts": now}
    return payload, None


def _fetch_by_id(zawa_path: str, param_name: str, id_val, cache_prefix: str):
    cache_key = f"{cache_prefix}:{id_val}"
    now = time.time()
    cached = _CACHE.get(cache_key)
    if cached and (now - cached["ts"]) < CACHE_TTL:
        return cached["payload"], None, False

    url = f"{ZAWA_BASE}/{zawa_path}"
    logger.info(f"[Baseline] fetch {zawa_path} {param_name}={id_val}")
    try:
        resp = requests.get(url, params={param_name: id_val},
                            timeout=ZAWA_TIMEOUT, headers=_zawa_headers())
        logger.info(f"[Baseline] by-id status={resp.status_code} path={zawa_path}")
        if resp.status_code == 404:
            return None, None, True
        resp.raise_for_status()
        raw = resp.json()
    except requests.exceptions.Timeout:
        return None, "Timeout saat menghubungi ZAWA.", False
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else 0
        body   = e.response.text[:200] if e.response is not None else ""
        logger.error(f"[Baseline] by-id HTTP {status} path={zawa_path} body={body}")
        return None, f"ZAWA error {status}: {body}", False
    except Exception as e:
        logger.error(f"[Baseline] by-id error: {e}", exc_info=True)
        return None, f"Error: {e}", False

    data_obj = raw.get("data")
    if isinstance(data_obj, list):
        items = data_obj
    elif isinstance(data_obj, dict):
        items = data_obj.get("items") or data_obj.get("data") or []
        if not items and any(k not in ("items", "data", "limit", "currentPage",
                                       "totalItems", "totalPages", "hasNextPage",
                                       "hasPreviousPage", "nextCursor")
                             for k in data_obj):
            items = [data_obj]
    else:
        items = []

    payload = {
        "items":           items,
        "totalItems":      len(items),
        "totalPages":      1,
        "currentPage":     1,
        "hasNextPage":     False,
        "hasPreviousPage": False,
        "nextCursor":      None,
        "limit":           max(len(items), 1),
        "search_mode":     "by_id",
    }
    _CACHE[cache_key] = {"payload": payload, "ts": now}
    return payload, None, False


def _build_table_response(payload, label, provinsi):
    rows    = payload["items"]
    columns = list(rows[0].keys()) if rows else []
    return jsonify({
        "data":    rows,
        "columns": columns,
        "meta": {
            "provinsi":        provinsi,
            "label":           label,
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


def _cache_anggota_to_db(items: list, provinsi_slug: str):
    if not items:
        return 0
    saved = 0
    for row in items:
        nik = str(row.get("nomor_induk_kependudukan", "") or "").strip()
        if not nik:
            continue
        exists = ZawaAnggota.query.filter_by(nomor_induk_kependudukan=nik).first()
        if exists:
            continue
        tgl = None
        raw_tgl = row.get("tanggal_lahir")
        if raw_tgl:
            try:
                tgl = datetime.fromisoformat(raw_tgl.replace("Z", "+00:00")).date()
            except Exception:
                pass
        obj = ZawaAnggota(
            nomor_induk_kependudukan  = nik,
            nomor_kartu_keluarga      = str(row.get("nomor_kartu_keluarga", "") or "").strip() or None,
            nama                      = row.get("nama"),
            jenis_kelamin             = str(row.get("jenis_kelamin", "") or ""),
            tanggal_lahir             = tgl,
            status_kawin              = str(row.get("status_kawin", "") or "") or None,
            status_hubungan_keluarga  = str(row.get("status_hubungan_keluarga", "") or "") or None,
            alamat_ktp                = row.get("alamat_ktp"),
            dusun_ktp                 = row.get("dusun_ktp"),
            rt_ktp                    = row.get("rt_ktp"),
            rw_ktp                    = row.get("rw_ktp"),
            kelurahan_desa_ktp        = row.get("kelurahan_desa_ktp"),
            kecamatan_ktp             = row.get("kecamatan_ktp"),
            kabupaten_kota_ktp        = row.get("kabupaten_kota_ktp"),
            provinsi_ktp              = row.get("provinsi_ktp"),
            kode_provinsi_ktp         = str(row.get("kode_provinsi_ktp", "") or "") or None,
            kode_kabupaten_kota_ktp   = str(row.get("kode_kabupaten_kota_ktp", "") or "") or None,
            kode_kecamatan_ktp        = str(row.get("kode_kecamatan_ktp", "") or "") or None,
            kode_kelurahan_desa_ktp   = str(row.get("kode_kelurahan_desa_ktp", "") or "") or None,
            partisipasi_sekolah       = str(row.get("partisipasi_sekolah", "") or "") or None,
            jenjang_tertinggi_yang_diduduki   = row.get("jenjang_tertinggi_yang_diduduki"),
            kelas_tertinggi_yang_diduduki     = row.get("kelas_tertinggi_yang_diduduki"),
            ijazah_tertinggi_yang_dimiliki    = row.get("ijazah_tertinggi_yang_dimiliki"),
            status_bekerja                    = str(row.get("status_bekerja", "") or "") or None,
            status_dalam_pekerjaan_utama      = str(row.get("status_dalam_pekerjaan_utama", "") or "") or None,
            lapangan_usaha_dari_pekerjaan_utama = row.get("lapangan_usaha_dari_pekerjaan_utama"),
            lapangan_usaha_dari_usaha_utama     = row.get("lapangan_usaha_dari_usaha_utama"),
            kepemilikan_usaha                   = str(row.get("kepemilikan_usaha", "") or "") or None,
            jumlah_usaha                        = row.get("jumlah_usaha"),
            jumlah_pekerja_yang_dibayar_dari_usaha_utama       = row.get("jumlah_pekerja_yang_dibayar_dari_usaha_utama"),
            jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama = row.get("jumlah_pekerja_yang_tidak_dibayar_dari_usaha_utama"),
            omzet_usaha_utama            = row.get("omzet_usaha_utama"),
            id_pelanggan_pln             = row.get("id_pelanggan_pln"),
            kondisi_gizi                 = str(row.get("kondisi_gizi", "") or "") or None,
            penyakit_kronis              = row.get("penyakit_kronis"),
            penglihatan                  = str(row.get("penglihatan", "") or "") or None,
            pendengaran                  = str(row.get("pendengaran", "") or "") or None,
            berjalan_atau_naik_tangga    = str(row.get("berjalan_atau_naik_tangga", "") or "") or None,
            menggunakan_tangan_jari      = str(row.get("menggunakan_tangan_jari", "") or "") or None,
            mengingat_berkonsentrasi     = str(row.get("mengingat_berkonsentrasi", "") or "") or None,
            berbicara_komunikasi         = str(row.get("berbicara_komunikasi", "") or "") or None,
            belajar_kemampuan_intelektual= str(row.get("belajar_kemampuan_intelektual", "") or "") or None,
            mengurus_diri                = str(row.get("mengurus_diri", "") or "") or None,
            kesedihan_depresi            = str(row.get("kesedihan_depresi", "") or "") or None,
            pengendalian_perilaku        = str(row.get("pengendalian_perilaku", "") or "") or None,
            pbi_nas                      = str(row.get("pbi_nas", "") or "") or None,
            pbi_pemda                    = str(row.get("pbi_pemda", "") or "") or None,
            raw_data                     = row,
            provinsi_slug                = provinsi_slug,
            synced_at                    = datetime.utcnow(),
        )
        db.session.add(obj)
        saved += 1
    db.session.commit()
    return saved


def _cache_keluarga_to_db(items: list):
    if not items:
        return 0
    saved = 0
    for row in items:
        nkk = str(row.get("nomor_kartu_keluarga", "") or "").strip()
        if not nkk:
            continue
        exists = ZawaKeluarga.query.filter_by(nomor_kartu_keluarga=nkk).first()
        if exists:
            continue
        obj = ZawaKeluarga(
            nomor_kartu_keluarga    = nkk,
            nama_anggota_keluarga   = row.get("nama_anggota_keluarga"),
            jumlah_anggota_keluarga = row.get("jumlah_anggota_keluarga"),
            alamat                  = row.get("alamat"),
            kelurahan_desa          = row.get("kelurahan_desa"),
            kecamatan               = row.get("kecamatan"),
            kabupaten_kota          = row.get("kabupaten_kota"),
            provinsi                = row.get("provinsi"),
            kode_provinsi           = str(row.get("kode_provinsi", "") or "") or None,
            kode_kabupaten_kota     = str(row.get("kode_kabupaten_kota", "") or "") or None,
            kode_kecamatan          = str(row.get("kode_kecamatan", "") or "") or None,
            kode_kelurahan_desa     = str(row.get("kode_kelurahan_desa", "") or "") or None,
            luas_lantai             = row.get("luas_lantai"),
            jenis_lantai_terluas    = row.get("jenis_lantai_terluas"),
            jenis_dinding_terluas   = row.get("jenis_dinding_terluas"),
            jenis_atap_terluas      = row.get("jenis_atap_terluas"),
            status_kepemilikan_rumah = str(row.get("status_kepemilikan_rumah", "") or "") or None,
            fasilitas_bab           = str(row.get("fasilitas_bab", "") or "") or None,
            jenis_kloset            = str(row.get("jenis_kloset", "") or "") or None,
            pembuangan_akhir_tinja  = str(row.get("pembuangan_akhir_tinja", "") or "") or None,
            sumber_air_minum_utama  = row.get("sumber_air_minum_utama"),
            sumber_penerangan_utama = str(row.get("sumber_penerangan_utama", "") or "") or None,
            bahan_bakar_utama_memasak = row.get("bahan_bakar_utama_memasak"),
            daya_terpasang          = row.get("daya_terpasang"),
            id_pelanggan_pln        = row.get("id_pelanggan_pln"),
            aset_bergerak_sepeda_motor           = str(row.get("aset_bergerak_sepeda_motor", "") or "") or None,
            aset_bergerak_mobil                  = str(row.get("aset_bergerak_mobil", "") or "") or None,
            aset_bergerak_sepeda                 = str(row.get("aset_bergerak_sepeda", "") or "") or None,
            aset_bergerak_perahu                 = str(row.get("aset_bergerak_perahu", "") or "") or None,
            aset_bergerak_kapal_perahu_motor     = str(row.get("aset_bergerak_kapal_perahu_motor", "") or "") or None,
            aset_bergerak_smartphone             = str(row.get("aset_bergerak_smartphone", "") or "") or None,
            aset_bergerak_komputer_laptop_tablet = str(row.get("aset_bergerak_komputer_laptop_tablet", "") or "") or None,
            aset_bergerak_tv_datar               = str(row.get("aset_bergerak_tv_datar", "") or "") or None,
            aset_bergerak_lemari_es              = str(row.get("aset_bergerak_lemari_es", "") or "") or None,
            aset_bergerak_ac                     = str(row.get("aset_bergerak_ac", "") or "") or None,
            aset_bergerak_pemanas_air            = str(row.get("aset_bergerak_pemanas_air", "") or "") or None,
            aset_bergerak_tabung_gas             = str(row.get("aset_bergerak_tabung_gas", "") or "") or None,
            aset_bergerak_telepon_rumah          = str(row.get("aset_bergerak_telepon_rumah", "") or "") or None,
            aset_bergerak_emas_perhiasan         = str(row.get("aset_bergerak_emas_perhiasan", "") or "") or None,
            aset_tidak_bergerak_rumah_lainnya    = str(row.get("aset_tidak_bergerak_rumah_lainnya", "") or "") or None,
            aset_tidak_bergerak_lahan_lainnya    = str(row.get("aset_tidak_bergerak_lahan_lainnya", "") or "") or None,
            kepemilikan_aset                     = str(row.get("kepemilikan_aset", "") or "") or None,
            jumlah_ternak_sapi          = row.get("jumlah_ternak_sapi"),
            jumlah_ternak_kerbau        = row.get("jumlah_ternak_kerbau"),
            jumlah_ternak_kuda          = row.get("jumlah_ternak_kuda"),
            jumlah_ternak_kambing_domba = row.get("jumlah_ternak_kambing_domba"),
            jumlah_ternak_babi          = row.get("jumlah_ternak_babi"),
            pbi_nas                     = str(row.get("pbi_nas", "") or "") or None,
            pbi_pemda                   = str(row.get("pbi_pemda", "") or "") or None,
            desil_nasional              = str(row.get("desil_nasional", "") or "") or None,
            raw_data                    = row,
            synced_at                   = datetime.utcnow(),
        )
        db.session.add(obj)
        saved += 1
    db.session.commit()
    return saved


# ─────────────────────────────────────────────
# SYNC ENDPOINTS
# ─────────────────────────────────────────────

@api_v1_bp.post('/baseline/sync/anggota')
@jwt_required()
def baseline_sync_anggota():
    body         = request.get_json(silent=True) or {}
    provinsi_req = (body.get("provinsi") or "").lower().strip()

    targets = {}
    if provinsi_req:
        info = PROVINSI_MAP.get(provinsi_req)
        if not info:
            return jsonify({"error": f"Kode provinsi '{provinsi_req}' tidak dikenal."}), 400
        targets = {provinsi_req: info}
    else:
        targets = PROVINSI_MAP

    hasil = []
    for slug, info in targets.items():
        log = ZawaSyncLog(
            sync_type=f"anggota:{slug}",
            provinsi_slug=slug,
            status="running",
            started_at=datetime.utcnow(),
        )
        db.session.add(log)
        db.session.commit()

        total_fetched = 0
        total_saved   = 0
        cursor        = None
        error_msg     = None

        try:
            while total_fetched < SYNC_MAX_ANGGOTA_PER_PROVINSI:
                sisa    = SYNC_MAX_ANGGOTA_PER_PROVINSI - total_fetched
                params  = {"cursor": cursor} if cursor else {}
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
                saved = _cache_anggota_to_db(items, slug)
                total_saved += saved
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
            "provinsi":      slug,
            "label":         info["label"],
            "total_fetched": total_fetched,
            "total_saved":   total_saved,
            "status":        log.status,
            "error":         error_msg,
            "durasi_detik":  log.duration_seconds(),
        })
        logger.info(f"[Sync] anggota {slug}: fetched={total_fetched} saved={total_saved} status={log.status}")

    return jsonify({
        "message": f"Sync anggota selesai. {len(hasil)} provinsi diproses.",
        "batas_per_provinsi": SYNC_MAX_ANGGOTA_PER_PROVINSI,
        "hasil": hasil,
    }), 200


@api_v1_bp.post('/baseline/sync/keluarga')
@jwt_required()
def baseline_sync_keluarga():
    log = ZawaSyncLog(
        sync_type="keluarga",
        provinsi_slug=None,
        status="running",
        started_at=datetime.utcnow(),
    )
    db.session.add(log)
    db.session.commit()

    total_fetched = 0
    total_saved   = 0
    cursor        = None
    error_msg     = None

    try:
        while total_fetched < SYNC_MAX_KELUARGA_TOTAL:
            sisa   = SYNC_MAX_KELUARGA_TOTAL - total_fetched
            params = {"cursor": cursor} if cursor else {}
            payload, err = _fetch_zawa_page("zawa/keluarga", params)
            if err:
                error_msg = err
                break
            items = payload["items"]
            if not items:
                break
            if len(items) > sisa:
                items = items[:sisa]
            total_fetched += len(items)
            saved = _cache_keluarga_to_db(items)
            total_saved += saved
            if not payload["hasNextPage"] or not payload["nextCursor"]:
                break
            cursor = payload["nextCursor"]
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[Sync] keluarga error: {e}", exc_info=True)

    log.status        = "failed" if error_msg else "success"
    log.total_fetched = total_fetched
    log.total_saved   = total_saved
    log.error_message = error_msg
    log.finished_at   = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "message":       "Sync keluarga selesai.",
        "batas_total":   SYNC_MAX_KELUARGA_TOTAL,
        "total_fetched": total_fetched,
        "total_saved":   total_saved,
        "status":        log.status,
        "error":         error_msg,
        "durasi_detik":  log.duration_seconds(),
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
                "error_message": l.error_message,
                "started_at":    l.started_at.isoformat() if l.started_at else None,
                "finished_at":   l.finished_at.isoformat() if l.finished_at else None,
                "durasi_detik":  l.duration_seconds(),
            }
            for l in logs
        ]
    }), 200


# ─────────────────────────────────────────────
# ENDPOINT READ
# ─────────────────────────────────────────────

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
    overall_ok = all(v.get("ok") for v in results.values())
    return jsonify({"ok": overall_ok, "checks": results, "target": host}), 200


@api_v1_bp.get('/baseline/provinsi')
@jwt_required()
def baseline_provinsi_list():
    """
    Return daftar provinsi yang boleh diakses user yang sedang login.
    - tuser/admin          : semua provinsi dari PROVINSI_MAP
    - dtsen (semua skala)  : hanya provinsi sesuai t_dtsen_wilayah
    """
    identity = _current_identity()
    allowed  = _allowed_provinsi_slugs(identity)

    if allowed is None:
        items = [
            {"kode": k, "label": v["label"]}
            for k, v in sorted(PROVINSI_MAP.items(), key=lambda x: x[1]["label"])
        ]
    else:
        items = [
            {"kode": k, "label": PROVINSI_MAP[k]["label"]}
            for k in allowed
            if k in PROVINSI_MAP
        ]
        items.sort(key=lambda x: x["label"])

    # Sertakan scope wilayah agar frontend bisa tahu drilldown yang aktif
    scope = _get_wilayah_scope(identity)
    return jsonify({"data": items, "scope": scope}), 200


@api_v1_bp.get('/baseline/anggota')
@jwt_required()
def baseline_anggota():
    identity = _current_identity()
    allowed  = _allowed_provinsi_slugs(identity)

    provinsi = request.args.get('provinsi', '').lower().strip()
    cursor   = request.args.get('cursor') or None
    search   = request.args.get('search', '').strip()
    # Filter opsional untuk drilldown kabkota & kecamatan
    kabkota_filter   = request.args.get('kabkota_kode', '').strip() or None
    kecamatan_filter = request.args.get('kecamatan_kode', '').strip() or None

    if not provinsi:
        return jsonify({"error": "Parameter 'provinsi' wajib diisi."}), 400
    info = PROVINSI_MAP.get(provinsi)
    if not info:
        return jsonify({"error": f"Kode provinsi '{provinsi}' tidak dikenal."}), 400

    # Guard akses provinsi
    if allowed is not None and provinsi not in allowed:
        return jsonify({"error": "Akses ditolak. Provinsi ini tidak termasuk wilayah Anda."}), 403

    # Guard akses kabkota (skala 2 & 3)
    if kabkota_filter:
        allowed_kabkota = _get_allowed_kabkota(identity)
        if allowed_kabkota is not None and kabkota_filter not in allowed_kabkota:
            return jsonify({"error": "Akses ditolak. Kabupaten/Kota ini tidak termasuk wilayah Anda."}), 403

    # Guard akses kecamatan (skala 3)
    if kecamatan_filter:
        allowed_kec = _get_allowed_kecamatan(identity)
        if allowed_kec is not None and kecamatan_filter not in allowed_kec:
            return jsonify({"error": "Akses ditolak. Kecamatan ini tidak termasuk wilayah Anda."}), 403

    if search and _is_numeric_id(search):
        db_row = ZawaAnggota.query.filter_by(nomor_induk_kependudukan=search.strip()).first()
        if db_row:
            logger.info(f"[Baseline] anggota NIK={search} ditemukan di DB lokal")
            return _ok_payload(
                [_row_to_dict(db_row)], info["label"], provinsi,
                {"searchMode": "db_cache", "source": "local_db"}
            )

        payload, err, not_found = _fetch_by_id(
            "zawa/anggota-by-nik", "nomor_induk_kependudukan",
            search.strip(), "anggota-by-nik"
        )
        if not_found:
            return _err_200(f"NIK {search} tidak ditemukan di data ZAWA.", info["label"], provinsi)
        if err:
            return _err_200(err, info["label"], provinsi)

        if payload["items"]:
            try:
                _cache_anggota_to_db(payload["items"], provinsi)
            except Exception as e:
                logger.warning(f"[Baseline] gagal cache anggota NIK={search}: {e}")

        return _build_table_response(payload, info["label"], provinsi)

    if not cursor:
        q = ZawaAnggota.query.filter_by(provinsi_slug=provinsi)
        if kabkota_filter:
            q = q.filter(ZawaAnggota.kode_kabupaten_kota_ktp == kabkota_filter)
        if kecamatan_filter:
            q = q.filter(ZawaAnggota.kode_kecamatan_ktp == kecamatan_filter)
        db_rows = q.limit(ZAWA_LIMIT).all()
        if db_rows:
            logger.info(f"[Baseline] anggota provinsi={provinsi} dari DB lokal ({len(db_rows)} rows)")
            items = [_row_to_dict(r) for r in db_rows]
            return _ok_payload(
                items, info["label"], provinsi,
                {"searchMode": "db_cache", "source": "local_db",
                 "totalItems": len(items), "limit": ZAWA_LIMIT}
            )

    params = {"cursor": cursor} if cursor else {}
    payload, err = _fetch_zawa_page(f"zawa/{info['slug']}", params)
    if err:
        return _err_200(err, info["label"], provinsi)

    if search:
        q_str = search.lower()
        payload["items"] = [
            r for r in payload["items"]
            if q_str in " ".join(str(v).lower() for v in r.values() if v)
        ]

    if payload["items"]:
        try:
            _cache_anggota_to_db(payload["items"], provinsi)
        except Exception as e:
            logger.warning(f"[Baseline] gagal cache anggota list provinsi={provinsi}: {e}")

    return _build_table_response(payload, info["label"], provinsi)


@api_v1_bp.get('/baseline/keluarga')
@jwt_required()
def baseline_keluarga():
    cursor = request.args.get('cursor') or None
    search = request.args.get('search', '').strip()

    if search and _is_nkk(search):
        db_row = ZawaKeluarga.query.filter_by(nomor_kartu_keluarga=search.strip()).first()
        if db_row:
            logger.info(f"[Baseline] keluarga NKK={search} ditemukan di DB lokal")
            return _ok_payload(
                [_row_to_dict(db_row)], "Keluarga", "nasional",
                {"searchMode": "db_cache", "source": "local_db"}
            )

        logger.info(f"[Baseline] keluarga search by NKK={search} (string)")
        payload, err, not_found = _fetch_by_id(
            "zawa/keluarga-by-nik", "nomor_kartu_keluarga",
            search.strip(), "keluarga-by-nik"
        )
        if not_found:
            return _err_200(
                f"Nomor KK {search} tidak ditemukan di data ZAWA.",
                "Keluarga", "nasional"
            )
        if err:
            return _err_200(err, "Keluarga", "nasional")

        if payload["items"]:
            try:
                _cache_keluarga_to_db(payload["items"])
            except Exception as e:
                logger.warning(f"[Baseline] gagal cache keluarga NKK={search}: {e}")

        return _build_table_response(payload, "Keluarga", "nasional")

    db_total = ZawaKeluarga.query.count()

    if db_total > 0:
        db_page = _parse_db_cursor(cursor) if cursor else 1
        if db_page is None:
            db_page = 1

        offset = (db_page - 1) * ZAWA_LIMIT

        q_obj = ZawaKeluarga.query
        if search:
            q_lower = f"%{search.lower()}%"
            q_obj = q_obj.filter(
                db.or_(
                    ZawaKeluarga.nomor_kartu_keluarga.ilike(q_lower),
                    ZawaKeluarga.nama_anggota_keluarga.ilike(q_lower),
                    ZawaKeluarga.alamat.ilike(q_lower),
                    ZawaKeluarga.kelurahan_desa.ilike(q_lower),
                    ZawaKeluarga.kecamatan.ilike(q_lower),
                    ZawaKeluarga.kabupaten_kota.ilike(q_lower),
                    ZawaKeluarga.provinsi.ilike(q_lower),
                )
            )

        filtered_total = q_obj.count()
        total_pages    = max(1, -(-filtered_total // ZAWA_LIMIT))
        db_rows        = q_obj.order_by(ZawaKeluarga.id).offset(offset).limit(ZAWA_LIMIT).all()
        items          = [_row_to_dict(r) for r in db_rows]

        has_next = db_page < total_pages
        has_prev = db_page > 1
        next_cur = _build_db_cursor(db_page + 1) if has_next else None

        logger.info(
            f"[Baseline] keluarga dari DB lokal: page={db_page}/{total_pages} "
            f"rows={len(items)} total={filtered_total} search={search!r}"
        )

        columns = list(items[0].keys()) if items else []
        return jsonify({
            "data":    items,
            "columns": columns,
            "meta": {
                "provinsi":        "nasional",
                "label":           "Keluarga",
                "totalItems":      filtered_total,
                "totalPages":      total_pages,
                "currentPage":     db_page,
                "hasNextPage":     has_next,
                "hasPreviousPage": has_prev,
                "nextCursor":      next_cur,
                "limit":           ZAWA_LIMIT,
                "searchMode":      "db_local",
                "source":          "local_db",
            }
        }), 200

    logger.info("[Baseline] keluarga DB kosong, fallback ke ZAWA API")
    params = {"cursor": cursor} if cursor else {}
    payload, err = _fetch_zawa_page("zawa/keluarga", params)
    if err:
        return _err_200(err, "Keluarga", "nasional")

    if search:
        q = search.lower()
        payload["items"] = [
            r for r in payload["items"]
            if q in " ".join(str(v).lower() for v in r.values() if v)
        ]

    if payload["items"]:
        try:
            _cache_keluarga_to_db(payload["items"])
        except Exception as e:
            logger.warning(f"[Baseline] gagal cache keluarga list: {e}")

    return _build_table_response(payload, "Keluarga", "nasional")


@api_v1_bp.get('/baseline')
@jwt_required()
def baseline_data():
    return baseline_anggota()


@api_v1_bp.delete('/baseline/cache')
@jwt_required()
def baseline_clear_cache():
    _CACHE.clear()
    logger.info("[Baseline] cache di-flush")
    return jsonify({"message": "Cache berhasil dikosongkan."}), 200
