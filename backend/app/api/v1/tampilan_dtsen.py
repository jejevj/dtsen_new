from flask import jsonify
from flask_jwt_extended import jwt_required
from . import api_v1_bp
from ...models.tampilan_dtsen import TampilanDtsen


@api_v1_bp.get('/tampilan-dtsen')
@jwt_required()
def list_tampilan_dtsen():
    """
    Ambil semua field aktif beserta referensi kode-nya.
    Field dengan is_filter=1 digunakan sebagai opsi filter pencarian mustahik.
    ---
    tags:
      - TampilanDtsen
    security:
      - Bearer: []
    responses:
      200:
        description: Daftar field aktif berhasil diambil
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: array
              items:
                type: object
                properties:
                  id:          { type: integer }
                  field_key:   { type: string }
                  field_label: { type: string }
                  field_group: { type: string }
                  kategori:    { type: string }
                  field_type:  { type: string }
                  is_filter:   { type: integer }
                  is_detail:   { type: integer }
                  urutan:      { type: integer }
                  refs:
                    type: array
                    items:
                      type: object
                      properties:
                        id:        { type: integer }
                        ref_value: { type: string }
                        ref_label: { type: string }
                        urutan:    { type: integer }
      401:
        description: Token tidak valid
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
@jwt_required()
def list_filter_fields():
    """
    Ambil hanya field yang is_filter=1 dan is_active=1.
    Digunakan oleh frontend untuk membangun panel filter dinamis.
    ---
    tags:
      - TampilanDtsen
    security:
      - Bearer: []
    responses:
      200:
        description: Daftar field filter berhasil diambil
      401:
        description: Token tidak valid
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
