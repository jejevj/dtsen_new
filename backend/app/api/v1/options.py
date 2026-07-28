from flask import jsonify
from . import api_v1_bp
from app.models.ic_options import IcOptions

# ── Key names di tabel ic_options ──────────────────────────────────────────
_KEY_MAINTENANCE = "dtsen_maintenance"


@api_v1_bp.get("/options/maintenance")
def get_maintenance():
    """
    GET /api/v1/options/maintenance

    Kembalikan status maintenance aplikasi DTSEN.
    Nilai opt_values '1' = maintenance aktif, '0' = normal.

    Response:
        200  { "maintenance": true|false }
        503  { "maintenance": true, "message": "..." }  — jika sedang maintenance
    """
    is_maintenance = IcOptions.get_value(_KEY_MAINTENANCE, default="0") == "1"

    payload = {
        "maintenance": is_maintenance,
        "message": "Sistem sedang dalam pemeliharaan. Silakan coba beberapa saat lagi."
                   if is_maintenance else None,
    }

    status_code = 503 if is_maintenance else 200
    return jsonify(payload), status_code
