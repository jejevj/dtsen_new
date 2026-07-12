import logging
import os
import re
import time
import requests
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from . import api_v1_bp

logger = logging.getLogger('app')

PROVINSI_MAP = {
    "aceh":      {"label": "Aceh",               "slug": "anggota"},
    "jambi":     {"label": "Jambi",              "slug": "jambi"},
    "sumbar":    {"label": "Sumatera Barat",     "slug": "sumbar"},
    "riau":      {"label": "Riau",               "slug": "riau"},
    "sumut":     {"label": "Sumatera Utara",     "slug": "sumut"},
    "kepriau":   {"label": "Kepulauan Riau",     "slug": "kepriau"},
    "babel":     {"label": "Bangka Belitung",    "slug": "babel"},
    "lampung":   {"label": "Lampung",            "slug": "lampung"},
    "bengkulu":  {"label": "Bengkulu",           "slug": "bengkulu"},
    "sumsel":    {"label": "Sumatera Selatan",   "slug": "sumsel"},
    "jateng":    {"label": "Jawa Tengah",        "slug": "jateng"},
    "jabar":     {"label": "Jawa Barat",         "slug": "jabar"},
    "dkijakarta":{"label": "DKI Jakarta",        "slug": "dkijakarta"},
    "kaltara":   {"label": "Kalimantan Utara",   "slug": "kaltara"},
    "kaltim":    {"label": "Kalimantan Timur",   "slug": "kaltim"},
    "kalsel":    {"label": "Kalimantan Selatan", "slug": "kalsel"},
    "kalteng":   {"label": "Kalimantan Tengah",  "slug": "kalteng"},
    "kalbar":    {"label": "Kalimantan Barat",   "slug": "kalbar"},
    "ntt":       {"label": "Nusa Tenggara Timur","slug": "ntt"},
    "ntb":       {"label": "Nusa Tenggara Barat","slug": "ntb"},
    "bali":      {"label": "Bali",               "slug": "bali"},
    "banten":    {"label": "Banten",             "slug": "banten"},
    "jatim":     {"label": "Jawa Timur",         "slug": "jatim"},
    "diy":       {"label": "DI Yogyakarta",      "slug": "diy"},
    "sulut":     {"label": "Sulawesi Utara",     "slug": "sulut"},
    "sulteng":   {"label": "Sulawesi Tengah",    "slug": "sulteng"},
    "sulsel":    {"label": "Sulawesi Selatan",   "slug": "sulsel"},
    "sultra":    {"label": "Sulawesi Tenggara",  "slug": "sultra"},
    "papdy":     {"label": "Papua Barat Daya",   "slug": "papdy"},
    "papgu":     {"label": "Papua Pegunungan",   "slug": "papgu"},
    "gorontalo": {"label": "Gorontalo",          "slug": "gorontalo"},
    "sulbar":    {"label": "Sulawesi Barat",     "slug": "sulbar"},
    "maluku":    {"label": "Maluku",             "slug": "maluku"},
    "malut":     {"label": "Maluku Utara",       "slug": "malut"},
    "papua":     {"label": "Papua",              "slug": "papua"},
    "papbar":    {"label": "Papua Barat",        "slug": "papbar"},
    "papsel":    {"label": "Papua Selatan",      "slug": "papsel"},
    "papteng":   {"label": "Papua Tengah",       "slug": "papteng"},
}

ZAWA_BASE    = "https://spl-satudata.kemenag.go.id/core/api"
ZAWA_TIMEOUT = 60
ZAWA_LIMIT   = 10

_CACHE: dict = {}
CACHE_TTL = 600


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


def _ok_payload(items, label, provinsi, meta_override=None):
    """Bangun response 200 sukses."""
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
    """
    Kembalikan HTTP 200 dengan data kosong + pesan error.
    Cloudflare tidak akan memblokir 200.
    """
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


def _fetch_by_id(zawa_path: str, param_name: str, id_str: str, cache_prefix: str):
    """
    Hit endpoint by-nik. Mengembalikan (payload|None, error_str|None, not_found: bool).
    404 dari ZAWA = data tidak ditemukan, bukan error server.
    """
    cache_key = f"{cache_prefix}:{id_str}"
    now = time.time()
    cached = _CACHE.get(cache_key)
    if cached and (now - cached["ts"]) < CACHE_TTL:
        return cached["payload"], None, False

    url = f"{ZAWA_BASE}/{zawa_path}"
    logger.info(f"[Baseline] fetch {zawa_path} {param_name}={id_str}")
    try:
        resp = requests.get(url, params={param_name: id_str},
                            timeout=ZAWA_TIMEOUT, headers=_zawa_headers())
        logger.info(f"[Baseline] by-id status={resp.status_code} path={zawa_path}")

        # 404 = data tidak ditemukan, bukan server error
        if resp.status_code == 404:
            logger.info(f"[Baseline] by-id 404 (not found) path={zawa_path} id={id_str}")
            return None, None, True  # not_found=True

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


# ── Diagnostik
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


# ── Provinsi list
@api_v1_bp.get('/baseline/provinsi')
@jwt_required()
def baseline_provinsi_list():
    items = [
        {"kode": k, "label": v["label"]}
        for k, v in sorted(PROVINSI_MAP.items(), key=lambda x: x[1]["label"])
    ]
    return jsonify({"data": items}), 200


# ── Tab Anggota
@api_v1_bp.get('/baseline/anggota')
@jwt_required()
def baseline_anggota():
    provinsi = request.args.get('provinsi', '').lower().strip()
    cursor   = request.args.get('cursor') or None
    search   = request.args.get('search', '').strip()

    if not provinsi:
        return jsonify({"error": "Parameter 'provinsi' wajib diisi."}), 400
    info = PROVINSI_MAP.get(provinsi)
    if not info:
        return jsonify({"error": f"Kode provinsi '{provinsi}' tidak dikenal."}), 400

    if search and _is_numeric_id(search):
        payload, err, not_found = _fetch_by_id(
            "zawa/anggota-by-nik", "nomor_induk_kependudukan",
            search.strip(), "anggota-by-nik"
        )
        if not_found:
            return _err_200(f"NIK {search} tidak ditemukan di data ZAWA.", info["label"], provinsi)
        if err:
            return _err_200(err, info["label"], provinsi)
        return _build_table_response(payload, info["label"], provinsi)

    params = {"cursor": cursor} if cursor else {}
    payload, err = _fetch_zawa_page(f"zawa/{info['slug']}", params)
    if err:
        return _err_200(err, info["label"], provinsi)

    if search:
        q = search.lower()
        payload["items"] = [
            r for r in payload["items"]
            if q in " ".join(str(v).lower() for v in r.values() if v)
        ]

    return _build_table_response(payload, info["label"], provinsi)


# ── Tab Keluarga
@api_v1_bp.get('/baseline/keluarga')
@jwt_required()
def baseline_keluarga():
    cursor = request.args.get('cursor') or None
    search = request.args.get('search', '').strip()

    if search and _is_numeric_id(search):
        payload, err, not_found = _fetch_by_id(
            "zawa/keluarga-by-nik", "nomor_kartu_keluarga",
            search.strip(), "keluarga-by-nkk"
        )
        if not_found:
            return _err_200(
                f"Nomor KK {search} tidak ditemukan di data ZAWA.",
                "Keluarga", "nasional"
            )
        if err:
            return _err_200(err, "Keluarga", "nasional")
        return _build_table_response(payload, "Keluarga", "nasional")

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

    return _build_table_response(payload, "Keluarga", "nasional")


# ── Alias lama
@api_v1_bp.get('/baseline')
@jwt_required()
def baseline_data():
    return baseline_anggota()


# ── Flush cache
@api_v1_bp.delete('/baseline/cache')
@jwt_required()
def baseline_clear_cache():
    _CACHE.clear()
    logger.info("[Baseline] cache di-flush")
    return jsonify({"message": "Cache berhasil dikosongkan."}), 200
