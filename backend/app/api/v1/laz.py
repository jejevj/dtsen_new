from flask import request, jsonify
from . import api_v1_bp
from ...extensions import db
from ...models.laz import Laz


@api_v1_bp.get('/laz')
def list_laz():
    """List LAZ aktif."""
    skala = request.args.get('skala')
    query = Laz.query.filter(Laz.laz_status.in_(['aktif', 'daftar_ulang']))
    if skala:
        query = query.filter_by(skala=skala)
    data = query.all()
    return jsonify([{'laz_kode': l.laz_kode, 'laz_nama': l.laz_nama, 'skala': l.skala} for l in data]), 200
