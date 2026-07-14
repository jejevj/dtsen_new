from flask import request, jsonify
from flask_jwt_extended import jwt_required
from . import api_v1_bp
from ...services.mustahik_service import MustahikService


@api_v1_bp.get('/mustahik')
@jwt_required()
def list_mustahik():
    """
    List data mustahik dengan filter dan pagination
    ---
    tags:
      - Mustahik
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 20
      - in: query
        name: search
        type: string
        description: Cari berdasarkan nama atau NIK
    responses:
      200:
        description: Daftar mustahik berhasil diambil
      401:
        description: Token tidak valid
    """
    params = request.args.to_dict()
    result = MustahikService.get_list(params)
    return jsonify(result), 200


@api_v1_bp.get('/mustahik/<string:nik_hashed>')
@jwt_required()
def detail_mustahik(nik_hashed):
    """
    Get detail mustahik berdasarkan hashed NIK
    ---
    tags:
      - Mustahik
    security:
      - Bearer: []
    parameters:
      - in: path
        name: nik_hashed
        type: string
        required: true
        description: Hashed NIK mustahik
    responses:
      200:
        description: Detail mustahik berhasil diambil
      404:
        description: Mustahik tidak ditemukan
      401:
        description: Token tidak valid
    """
    result = MustahikService.get_detail(nik_hashed)
    return jsonify(result), 200

@api_v1_bp.get('/mustahik/<string:nik_hashed>/riwayat')
@jwt_required()
def riwayat_mustahik(nik_hashed):
    result = MustahikService.get_riwayat(nik_hashed)
    return jsonify(result), 200

@api_v1_bp.get("/mustahik/<string:nik_hashed>/program")
@jwt_required()
def program(nik_hashed):
    result = MustahikService.get_program(nik_hashed)
    return jsonify(result), 200
    