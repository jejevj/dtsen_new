import json
import os
from flask import request, jsonify
from . import api_v1_bp

# Path ke file GeoJSON di server (taruh di backend/data/geo/)
# __file__ = backend/app/api/v1/geo.py
# ../../.. = backend/app/api/v1 -> v1 -> api -> app -> backend
GEO_VILLAGES_PATH = os.path.join(
    os.path.dirname(__file__),
    '../../../data/geo/Indonesia_villages.geojson'
)

# Cache in-memory agar tidak baca file berulang kali
_villages_cache = None


def _load_villages():
    global _villages_cache
    if _villages_cache is None:
        if not os.path.exists(GEO_VILLAGES_PATH):
            return None
        with open(GEO_VILLAGES_PATH, 'r', encoding='utf-8') as f:
            _villages_cache = json.load(f)
    return _villages_cache


@api_v1_bp.route('/geo/level3', methods=['GET'])
def get_geojson_level3():
    """
    Get GeoJSON kecamatan (level 3) berdasarkan provinsi dan kabupaten.
    ---
    tags:
      - Geo
    parameters:
      - name: provinsi
        in: query
        type: string
        required: true
        description: Nama provinsi (sesuai NAME_1 di GeoJSON)
      - name: kabupaten
        in: query
        type: string
        required: true
        description: Nama kabupaten/kota (sesuai NAME_2 di GeoJSON)
    responses:
      200:
        description: GeoJSON FeatureCollection kecamatan
      400:
        description: Parameter provinsi atau kabupaten tidak diberikan
      503:
        description: File GeoJSON tidak ditemukan di server
    """
    provinsi = request.args.get('provinsi', '').strip()
    kabupaten = request.args.get('kabupaten', '').strip()

    if not provinsi or not kabupaten:
        return jsonify({
            'error': 'Parameter provinsi dan kabupaten wajib diisi'
        }), 400

    geojson = _load_villages()
    if geojson is None:
        return jsonify({
            'error': 'File GeoJSON tidak ditemukan di server. '
                     'Pastikan Indonesia_villages.geojson ada di backend/data/geo/'
        }), 503

    filtered = [
        f for f in geojson.get('features', [])
        if f.get('properties', {}).get('NAME_1', '').lower() == provinsi.lower()
        and f.get('properties', {}).get('NAME_2', '').lower() == kabupaten.lower()
    ]

    return jsonify({
        'type': 'FeatureCollection',
        'features': filtered
    })
