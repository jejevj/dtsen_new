from flask import jsonify
from . import api_v1_bp
from ...services.report_service import ReportService


@api_v1_bp.get('/home/summary')
def home_summary():
    """Public dashboard summary (no auth required)."""
    return jsonify(ReportService.get_home_summary()), 200


@api_v1_bp.get('/home/map')
def home_map():
    """Peta penyaluran per provinsi."""
    from flask import request
    params = request.args.get('type', '1')
    return jsonify(ReportService.get_map_data(params)), 200
