from flask import jsonify, request
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
    Ambil field yang is_filter=1 dan is_active=1.
    Opsional: filter by kategori (individu / keluarga / keduanya).
    Query param: ?kategori=individu
    ---
    tags:
      - TampilanDtsen
    parameters:
      - in: query
        name: kategori
        type: string
        enum: [individu, keluarga, keduanya]
        description: Filter berdasarkan kategori field
    responses:
      200:
        description: Daftar field filter berhasil diambil
    """
    q = TampilanDtsen.query.filter_by(is_active=1, is_filter=1)

    kategori = request.args.get('kategori')
    if kategori:
        # keduanya cocok untuk individu maupun keluarga
        q = q.filter(
            (TampilanDtsen.kategori == kategori) |
            (TampilanDtsen.kategori == 'keduanya')
        )

    fields = q.order_by(TampilanDtsen.urutan.asc()).all()

    return jsonify({
        'status': 'success',
        'data':   [f.to_dict(with_refs=True) for f in fields],
    }), 200


@api_v1_bp.get('/tampilan-dtsen/detail')
def list_detail_fields():
    """
    Ambil field yang is_detail=1 dan is_active=1.
    Opsional: filter by kategori (individu / keluarga / keduanya).
    Query param: ?kategori=individu
    ---
    tags:
      - TampilanDtsen
    parameters:
      - in: query
        name: kategori
        type: string
        enum: [individu, keluarga, keduanya]
        description: Filter berdasarkan kategori field
    responses:
      200:
        description: Daftar field detail berhasil diambil
    """
    q = TampilanDtsen.query.filter_by(is_active=1, is_detail=1)

    kategori = request.args.get('kategori')
    if kategori:
        q = q.filter(
            (TampilanDtsen.kategori == kategori) |
            (TampilanDtsen.kategori == 'keduanya')
        )

    fields = q.order_by(TampilanDtsen.urutan.asc()).all()

    return jsonify({
        'status': 'success',
        'data':   [f.to_dict(with_refs=True) for f in fields],
    }), 200
