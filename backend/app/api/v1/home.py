from flask import jsonify, request
from . import api_v1_bp
from ...services.report_service import ReportService


@api_v1_bp.get('/home/summary')
def home_summary():
    """
    Dashboard summary publik (tanpa autentikasi)
    ---
    tags:
      - Home
    responses:
      200:
        description: Data ringkasan dashboard berhasil diambil
    """
    return jsonify(ReportService.get_home_summary()), 200


@api_v1_bp.get('/home/map')
def home_map():
    """
    Peta penyaluran per provinsi
    ---
    tags:
      - Home
    parameters:
      - in: query
        name: type
        type: string
        default: "1"
        description: Tipe peta penyaluran
    responses:
      200:
        description: Data peta berhasil diambil
    """
    params = request.args.get('type', '1')
    return jsonify(ReportService.get_map_data(params)), 200
