import logging
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
ZAWA_TIMEOUT = 30

_CACHE: dict = {}
CACHE_TTL = 600


def _safe_int(val, default, min_val=1, max_val=None):
    try:
        result = int(str(val).strip())
    except (ValueError, TypeError):
        result = default
    result = max(min_val, result)
    if max_val is not None:
        result = min(max_val, result)
    return result


def _fetch_zawa(slug: str):
    now = time.time()
    cached = _CACHE.get(slug)
    if cached and (now - cached["ts"]) < CACHE_TTL:
        logger.info(f"[Baseline] cache hit slug={slug}")
        return cached["data"], None

    url = f"{ZAWA_BASE}/zawa/{slug}"
    logger.info(f"[Baseline] fetch ZAWA url={url}")
    try:
        resp = requests.get(url, timeout=ZAWA_TIMEOUT, headers={"Accept": "application/json"})
        logger.info(f"[Baseline] ZAWA response status={resp.status_code} slug={slug}")
        resp.raise_for_status()
        raw = resp.json()
    except requests.exceptions.SSLError as e:
        logger.error(f"[Baseline] SSL error slug={slug}: {e}")
        return None, f"SSL error: {e}"
    except requests.exceptions.ConnectionError as e:
        logger.error(f"[Baseline] Connection error slug={slug}: {e}")
        return None, f"Tidak dapat terhubung ke ZAWA: {e}"
    except requests.exceptions.Timeout:
        logger.error(f"[Baseline] Timeout slug={slug}")
        return None, "Timeout (>30 detik) saat menghubungi ZAWA."
    except requests.exceptions.HTTPError as e:
        logger.error(f"[Baseline] HTTP error slug={slug}: {e}")
        return None, f"ZAWA HTTP error: {e}"
    except Exception as e:
        logger.error(f"[Baseline] Unexpected error slug={slug}: {e}", exc_info=True)
        return None, f"Error tidak terduga: {e}"

    rows = raw.get('data') or []
    if not isinstance(rows, list):
        rows = []

    _CACHE[slug] = {"data": rows, "ts": now}
    logger.info(f"[Baseline] cached {len(rows)} rows slug={slug}")
    return rows, None


# ── Diagnostik ────────────────────────────────────────────────────────────────
@api_v1_bp.get('/baseline/ping')
@jwt_required()
def baseline_ping():
    """
    Test koneksi dari server ke ZAWA.
    Gunakan untuk diagnosa apakah server produksi bisa reach spl-satudata.kemenag.go.id
    """
    import socket
    results = {}

    # 1. DNS resolve
    host = "spl-satudata.kemenag.go.id"
    try:
        ip = socket.gethostbyname(host)
        results["dns"] = {"ok": True, "ip": ip}
    except Exception as e:
        results["dns"] = {"ok": False, "error": str(e)}

    # 2. TCP connect port 443
    try:
        s = socket.create_connection((host, 443), timeout=5)
        s.close()
        results["tcp_443"] = {"ok": True}
    except Exception as e:
        results["tcp_443"] = {"ok": False, "error": str(e)}

    # 3. HTTP GET ke endpoint ZAWA (slug aceh = anggota)
    test_url = f"{ZAWA_BASE}/zawa/anggota"
    t0 = time.time()
    try:
        resp = requests.get(test_url, timeout=15, headers={"Accept": "application/json"})
        elapsed = round(time.time() - t0, 2)
        try:
            body_sample = resp.text[:200]
        except Exception:
            body_sample = "(tidak bisa baca body)"
        results["http_get"] = {
            "ok":      resp.status_code < 400,
            "status":  resp.status_code,
            "elapsed": f"{elapsed}s",
            "sample":  body_sample,
        }
    except requests.exceptions.SSLError as e:
        results["http_get"] = {"ok": False, "error": f"SSLError: {e}"}
    except requests.exceptions.ConnectionError as e:
        results["http_get"] = {"ok": False, "error": f"ConnectionError: {e}"}
    except requests.exceptions.Timeout:
        results["http_get"] = {"ok": False, "error": "Timeout >15s"}
    except Exception as e:
        results["http_get"] = {"ok": False, "error": str(e)}

    overall_ok = all(v.get("ok") for v in results.values())
    logger.info(f"[Baseline] ping results: {results}")
    return jsonify({"ok": overall_ok, "checks": results, "target": host}), 200 if overall_ok else 502


# ── Provinsi list ─────────────────────────────────────────────────────────────
@api_v1_bp.get('/baseline/provinsi')
@jwt_required()
def baseline_provinsi_list():
    items = [
        {"kode": k, "label": v["label"]}
        for k, v in sorted(PROVINSI_MAP.items(), key=lambda x: x[1]["label"])
    ]
    return jsonify({"data": items}), 200


# ── Data baseline ─────────────────────────────────────────────────────────────
@api_v1_bp.get('/baseline')
@jwt_required()
def baseline_data():
    provinsi = request.args.get('provinsi', '').lower().strip()
    page     = _safe_int(request.args.get('page',     1),  default=1,  min_val=1)
    per_page = _safe_int(request.args.get('per_page', 20), default=20, min_val=1, max_val=100)
    search   = request.args.get('search', '').lower().strip()

    if not provinsi:
        return jsonify({"error": "Parameter 'provinsi' wajib diisi."}), 400

    info = PROVINSI_MAP.get(provinsi)
    if not info:
        return jsonify({"error": f"Kode provinsi '{provinsi}' tidak dikenal."}), 400

    rows, err = _fetch_zawa(info['slug'])
    if err:
        return jsonify({"error": err}), 502

    if search:
        rows = [
            r for r in rows
            if search in " ".join(str(v).lower() for v in r.values() if v)
        ]

    total     = len(rows)
    start     = (page - 1) * per_page
    paginated = rows[start: start + per_page]
    columns   = list(paginated[0].keys()) if paginated else (list(rows[0].keys()) if rows else [])

    return jsonify({
        "data":    paginated,
        "columns": columns,
        "meta": {
            "page":     page,
            "per_page": per_page,
            "total":    total,
            "pages":    max(1, -(-total // per_page)),
            "provinsi": provinsi,
            "label":    info["label"],
        }
    }), 200


@api_v1_bp.delete('/baseline/cache')
@jwt_required()
def baseline_clear_cache():
    _CACHE.clear()
    logger.info("[Baseline] cache di-flush manual")
    return jsonify({"message": "Cache berhasil dikosongkan."}), 200
