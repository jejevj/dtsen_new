from flask import jsonify
from . import api_v1_bp
from ...models.tampilan_dtsen import TampilanDtsen


@api_v1_bp.get('/tampilan-dtsen')
def list_tampilan_dtsen():
    """
    Ambil semua field aktif beserta referensi kode-nya.
    ---
    tags:
      - TampilanDtsen
    responses:
      200:
        description: Daftar field aktif berhasil diambil
    """
    fields = (
        TampilanDtsen.query
        .filter_by(is_active=1)
        .order_by(TampilanDtsen.urutan.asc())
        .all()
    )
    return jsonify({
        'status': 'success',
        'data':   [f.to_dict(with_refs=True) for f in fields],
    }), 200


@api_v1_bp.get('/tampilan-dtsen/filter')
def list_filter_fields():
    """
    Ambil hanya field yang is_filter=1 dan is_active=1.
    Digunakan frontend untuk membangun panel filter dinamis.
    ---
    tags:
      - TampilanDtsen
    responses:
      200:
        description: Daftar field filter berhasil diambil
    """
    fields = (
        TampilanDtsen.query
        .filter_by(is_active=1, is_filter=1)
        .order_by(TampilanDtsen.urutan.asc())
        .all()
    )
    return jsonify({
        'status': 'success',
        'data':   [f.to_dict(with_refs=True) for f in fields],
    }), 200
