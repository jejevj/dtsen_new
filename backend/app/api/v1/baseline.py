import requests
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from . import api_v1_bp

# Mapping kode provinsi → slug endpoint ZAWA
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
ZAWA_TIMEOUT = 15


def _safe_int(val, default, min_val=1, max_val=None):
    """Parse integer dengan aman; fallback ke default jika tidak valid."""
    try:
        result = int(str(val).strip())
    except (ValueError, TypeError):
        result = default
    result = max(min_val, result)
    if max_val is not None:
        result = min(max_val, result)
    return result


@api_v1_bp.get('/baseline/provinsi')
@jwt_required()
def baseline_provinsi_list():
    """Kembalikan daftar provinsi yang tersedia beserta kodenya."""
    items = [
        {"kode": k, "label": v["label"]}
        for k, v in sorted(PROVINSI_MAP.items(), key=lambda x: x[1]["label"])
    ]
    return jsonify({"data": items}), 200


@api_v1_bp.get('/baseline')
@jwt_required()
def baseline_data():
    """
    Ambil data baseline ZAWA per provinsi dengan pagination & pencarian.
    Query params:
      - provinsi  : kode provinsi (wajib)
      - page      : halaman (default 1)
      - per_page  : baris per halaman (default 20, max 100)
      - search    : pencarian bebas (nama / NIK)
    """
    provinsi = request.args.get('provinsi', '').lower().strip()
    page     = _safe_int(request.args.get('page',     1),  default=1,  min_val=1)
    per_page = _safe_int(request.args.get('per_page', 20), default=20, min_val=1, max_val=100)
    search   = request.args.get('search', '').lower().strip()

    if not provinsi:
        return jsonify({"error": "Parameter 'provinsi' wajib diisi."}), 400

    info = PROVINSI_MAP.get(provinsi)
    if not info:
        return jsonify({"error": f"Kode provinsi '{provinsi}' tidak dikenal."}), 400

    # Fetch dari ZAWA
    url = f"{ZAWA_BASE}/zawa/{info['slug']}"
    try:
        resp = requests.get(url, timeout=ZAWA_TIMEOUT)
        resp.raise_for_status()
        raw = resp.json()
    except requests.exceptions.Timeout:
        return jsonify({"error": "Timeout saat menghubungi sumber data ZAWA."}), 504
    except Exception as e:
        return jsonify({"error": f"Gagal mengambil data: {str(e)}"}), 502

    rows = raw.get('data') or []
    if not isinstance(rows, list):
        rows = []

    # Filter pencarian
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
