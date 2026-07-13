import logging
import os
import re
import time
import requests
from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import distinct
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

_BPS_TO_SLUG: dict[str, str] = {v["bps"]: k for k, v in PROVINSI_MAP.items()}

ZAWA_BASE    = "https://spl-satudata.kemenag.go.id/core/api"
ZAWA_TIMEOUT = 60
ZAWA_LIMIT   = 10
DB_PAGE_SIZE = 50

SYNC_MAX_ANGGOTA_PER_PROVINSI = 10_000
SYNC_MAX_KELUARGA_PER_RUN     = 5_000

_CACHE: dict = {}
CACHE_TTL = 600


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

def _allowed_provinsi_slugs(identity: dict) -> list[str] | None:
    if _is_tuser(identity):
        return None
    dtsen = _get_dtsen_akses(identity)
    if dtsen is None:
        return []
    rows = TDtsenWilayah.query.filter_by(dtsen_akses_id=dtsen.dtsen_akses_id).all()
    allowed = []
    for row in rows:
        prov_kode = (row.provinsi_kode or '').strip().zfill(2)
        slug = _BPS_TO_SLUG.get(prov_kode)
        if slug and slug not in allowed:
            allowed.append(slug)
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


@api_v1_bp.get('/baseline/wilayah-scope')
@jwt_required()
def baseline_wilayah_scope():
    return jsonify(_get_wilayah_scope(_current_identity())), 200


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


def _cache_anggota_to_db(items: list, provinsi_slug: str):
    if not items:
        return 0
    saved = 0
    for row in items:
        nik = str(row.get("nomor_induk_kependudukan", "") or "").strip()
        if not nik:
            continue
        kode_prov_ktp = str(row.get("kode_provinsi_ktp") or "").strip().zfill(2)
        correct_slug  = _BPS_TO_SLUG.get(kode_prov_ktp) or provinsi_slug
        existing = ZawaAnggota.query.filter_by(nomor_induk_kependudukan=nik).first()
        if existing:
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

    existing_nkk_subq = db.session.query(ZawaKeluarga.nomor_kartu_keluarga).subquery()
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
    identity = _current_identity()
    allowed  = _allowed_provinsi_slugs(identity)
    if allowed is None:
        items = sorted(
            [{"kode": v["bps"], "label": v["label"], "slug": k}
             for k, v in PROVINSI_MAP.items()],
            key=lambda x: x["label"]
        )
    else:
        items = sorted(
            [{"kode": PROVINSI_MAP[k]["bps"], "label": PROVINSI_MAP[k]["label"], "slug": k}
             for k in allowed if k in PROVINSI_MAP],
            key=lambda x: x["label"]
        )
    return jsonify({"data": items, "scope": _get_wilayah_scope(identity)}), 200


def _build_anggota_db_query(provinsi_slug: str, bps_kode: str,
                             kabkota_filter, kecamatan_filter, search: str):
    """
    Bangun query ZawaAnggota dengan sumber kebenaran utama = kode_provinsi_ktp.
    Jangan lagi memakai provinsi_slug sebagai OR filter utama karena data historis
    bisa terlanjur salah label akibat hasil sync lintas provinsi dari endpoint ZAWA.
    Fallback ke provinsi_slug hanya dipakai jika kode_provinsi_ktp kosong/null.
    """
    q = ZawaAnggota.query.filter(
        db.or_(
            ZawaAnggota.kode_provinsi_ktp == bps_kode,
            ZawaAnggota.kode_provinsi_ktp == bps_kode.lstrip('0'),
            db.and_(
                db.or_(
                    ZawaAnggota.kode_provinsi_ktp.is_(None),
                    ZawaAnggota.kode_provinsi_ktp == '',
                ),
                ZawaAnggota.provinsi_slug == provinsi_slug,
            )
        )
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
    return q


@api_v1_bp.get('/baseline/anggota')
@jwt_required()
def baseline_anggota():
    identity = _current_identity()
    allowed  = _allowed_provinsi_slugs(identity)

    provinsi_raw     = request.args.get('provinsi', '').strip()
    cursor           = request.args.get('cursor') or None
    search           = request.args.get('search', '').strip()
    kabkota_filter   = request.args.get('kabkota_kode', '').strip() or None
    kecamatan_filter = request.args.get('kecamatan_kode', '').strip() or None

    if not provinsi_raw:
        return jsonify({"error": "Parameter 'provinsi' wajib diisi."}), 400

    provinsi, info = _resolve_provinsi(provinsi_raw)
    if not info:
        return jsonify({"error": f"Kode provinsi '{provinsi_raw}' tidak dikenal."}), 400

    if allowed is not None and provinsi not in allowed:
        return jsonify({"error": "Akses ditolak. Provinsi ini tidak termasuk wilayah Anda."}), 403

    bps_kode = info["bps"]

    kabkota_dotted = kabkota_plain = None
    if kabkota_filter:
        kabkota_dotted, kabkota_plain = _normalize_kode(kabkota_filter)
        allowed_kabkota = _get_allowed_kabkota(identity)
        if allowed_kabkota is not None:
            if kabkota_dotted not in allowed_kabkota and kabkota_plain not in allowed_kabkota:
                return jsonify({"error": "Akses ditolak. Kabupaten/Kota ini tidak termasuk wilayah Anda."}), 403

    kecamatan_dotted = kecamatan_plain = None
    if kecamatan_filter:
        kecamatan_dotted, kecamatan_plain = _normalize_kode(kecamatan_filter)
        allowed_kec = _get_allowed_kecamatan(identity)
        if allowed_kec is not None:
            if kecamatan_dotted not in allowed_kec and kecamatan_plain not in allowed_kec:
                return jsonify({"error": "Akses ditolak. Kecamatan ini tidak termasuk wilayah Anda."}), 403

    if search and _is_numeric_id(search):
        db_row = ZawaAnggota.query.filter_by(nomor_induk_kependudukan=search.strip()).first()
        if db_row:
            return _ok_payload([_row_to_dict(db_row)], info["label"], provinsi,
                               {"searchMode": "db_cache", "source": "local_db"})
        payload, err, not_found = _fetch_by_id(
            "zawa/anggota-by-nik", "nomor_induk_kependudukan", search.strip(), "anggota-by-nik")
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

    db_page = None
    if not cursor:
        db_page = 1
    else:
        db_page = _parse_db_cursor(cursor)

    if db_page is not None:
        q = _build_anggota_db_query(
            provinsi_slug=provinsi,
            bps_kode=bps_kode,
            kabkota_filter=kabkota_filter,
            kecamatan_filter=kecamatan_filter,
            search=search,
        )

        total_count = q.count()
        if total_count > 0:
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
                    "provinsi": provinsi, "label": info["label"],
                    "totalItems":      total_count,
                    "totalPages":      total_pages,
                    "currentPage":     db_page,
                    "hasNextPage":     has_next,
                    "hasPreviousPage": db_page > 1,
                    "nextCursor":      next_cur,
                    "limit":           DB_PAGE_SIZE,
                    "searchMode":      "db_cache",
                    "source":          "local_db",
                }
            }), 200

    params: dict = {}
    if cursor and not cursor.startswith("db:page_"):
        params["cursor"] = cursor
    if kabkota_dotted:
        params["kode_kabupaten_kota"] = kabkota_dotted
    if kecamatan_dotted:
        params["kode_kecamatan"] = kecamatan_dotted

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
    identity         = _current_identity()
    allowed          = _allowed_provinsi_slugs(identity)

    cursor           = request.args.get('cursor') or None
    search           = request.args.get('search', '').strip()
    provinsi_raw     = request.args.get('provinsi', '').strip() or None
    kabkota_filter   = request.args.get('kabkota_kode', '').strip() or None
    kecamatan_filter = request.args.get('kecamatan_kode', '').strip() or None

    prov_slug = prov_info = prov_bps = None
    if provinsi_raw:
        prov_slug, prov_info = _resolve_provinsi(provinsi_raw)
        if not prov_info:
            return jsonify({"error": f"Kode provinsi '{provinsi_raw}' tidak dikenal."}), 400
        if allowed is not None and prov_slug not in allowed:
            return jsonify({"error": "Akses ditolak. Provinsi ini tidak termasuk wilayah Anda."}), 403
        prov_bps = prov_info["bps"]

    label = prov_info["label"] if prov_info else "Keluarga"
    label_provinsi = prov_slug or "nasional"

    kabkota_dotted = kabkota_plain = None
    if kabkota_filter:
        kabkota_dotted, kabkota_plain = _normalize_kode(kabkota_filter)
        allowed_kabkota = _get_allowed_kabkota(identity)
        if allowed_kabkota is not None:
            if kabkota_dotted not in allowed_kabkota and kabkota_plain not in allowed_kabkota:
                return jsonify({"error": "Akses ditolak. Kabupaten/Kota ini tidak termasuk wilayah Anda."}), 403

    kecamatan_dotted = kecamatan_plain = None
    if kecamatan_filter:
        kecamatan_dotted, kecamatan_plain = _normalize_kode(kecamatan_filter)
        allowed_kec = _get_allowed_kecamatan(identity)
        if allowed_kec is not None:
            if kecamatan_dotted not in allowed_kec and kecamatan_plain not in allowed_kec:
                return jsonify({"error": "Akses ditolak. Kecamatan ini tidak termasuk wilayah Anda."}), 403

    if search and _is_nkk(search):
        db_row = ZawaKeluarga.query.filter_by(nomor_kartu_keluarga=search.strip()).first()
        if db_row:
            return _ok_payload([_row_to_dict(db_row)], label, label_provinsi,
                               {"searchMode": "db_cache", "source": "local_db"})
        payload, err, not_found = _fetch_by_id(
            "zawa/keluarga-by-nik", "nomor_kartu_keluarga", search.strip(), "keluarga-by-nkk")
        if not_found:
            return _err_200(f"Nomor KK {search} tidak ditemukan di data ZAWA.", label, label_provinsi)
        if err:
            return _err_200(err, label, label_provinsi)
        if payload["items"]:
            try:
                for item in payload["items"]:
                    _upsert_keluarga_from_api_item(item)
            except Exception as e:
                logger.warning(f"[Baseline] gagal cache keluarga NKK={search}: {e}")
        return _build_table_response(payload, label, label_provinsi)

    db_page = _parse_db_cursor(cursor) if cursor else 1
    if db_page is None:
        db_page = 1

    q = ZawaKeluarga.query

    if prov_bps:
        q = q.filter(db.or_(
            ZawaKeluarga.kode_provinsi == prov_bps,
            ZawaKeluarga.kode_provinsi == prov_bps.lstrip('0'),
        ))

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

    filtered_total = q.count()
    if filtered_total > 0:
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
                "provinsi":      label_provinsi,
                "label":         label,
                "totalItems":    filtered_total,
                "totalPages":    total_pages,
                "currentPage":   db_page,
                "hasNextPage":   has_next,
                "hasPreviousPage": db_page > 1,
                "nextCursor":    next_cur,
                "limit":         DB_PAGE_SIZE,
                "searchMode":    "db_local",
                "source":        "local_db",
            }
        }), 200

    if prov_bps or kabkota_dotted or kecamatan_dotted:
        columns = []
        return jsonify({
            "data": [], "columns": columns,
            "meta": {
                "provinsi": label_provinsi, "label": label,
                "totalItems": 0, "totalPages": 1, "currentPage": 1,
                "hasNextPage": False, "hasPreviousPage": False,
                "nextCursor": None, "limit": DB_PAGE_SIZE,
                "searchMode": "db_local", "source": "local_db",
                "errorMessage": "Data belum tersedia di cache lokal untuk wilayah ini. Lakukan sync terlebih dahulu.",
            }
        }), 200

    payload, err = _fetch_zawa_page("zawa/keluarga", {"cursor": cursor} if cursor and not cursor.startswith("db:page_") else {})
    if err:
        return _err_200(err, label, label_provinsi)
    if search:
        q_str = search.lower()
        payload["items"] = [
            r for r in payload["items"]
            if q_str in " ".join(str(v).lower() for v in r.values() if v)
        ]
    if payload["items"]:
        try:
            for item in payload["items"]:
                _upsert_keluarga_from_api_item(item)
        except Exception as e:
            logger.warning(f"[Baseline] gagal cache keluarga list: {e}")
    return _build_table_response(payload, label, label_provinsi)


@api_v1_bp.get('/baseline')
@jwt_required()
def baseline_data():
    return baseline_anggota()


@api_v1_bp.delete('/baseline/cache')
@jwt_required()
def baseline_clear_cache():
    _CACHE.clear()
    return jsonify({"message": "Cache berhasil dikosongkan."}), 200


@api_v1_bp.post('/baseline/repair/provinsi-slug')
@jwt_required()
def baseline_repair_provinsi_slug():
    """
    Perbaiki data lama: update provinsi_slug berdasarkan kode_provinsi_ktp.
    Panggil sekali dari admin untuk migrasi data yang salah label.
    """
    updated = 0
    rows = ZawaAnggota.query.filter(
        ZawaAnggota.kode_provinsi_ktp.isnot(None),
        ZawaAnggota.kode_provinsi_ktp != ''
    ).all()
    for row in rows:
        bps = str(row.kode_provinsi_ktp or '').strip().zfill(2)
        correct = _BPS_TO_SLUG.get(bps)
        if correct and row.provinsi_slug != correct:
            row.provinsi_slug = correct
            updated += 1
    db.session.commit()
    logger.info(f"[Repair] provinsi_slug diperbaiki: {updated} baris")
    return jsonify({
        "message": f"Selesai. {updated} baris provinsi_slug diperbaiki.",
        "updated": updated,
    }), 200
