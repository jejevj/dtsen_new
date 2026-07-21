from flask import jsonify
from . import api_v1_bp
from ...models.program import Bidang


@api_v1_bp.get('/bidang')
def list_bidang():
    """List seluruh bidang."""

    data = (
        Bidang.query
        .order_by(Bidang.bidang_label.asc())
        .all()
    )

    return jsonify([
        {
            "bidang_kode": b.bidang_kode,
            "bidang_label": b.bidang_label
        }
        for b in data
    ]), 200