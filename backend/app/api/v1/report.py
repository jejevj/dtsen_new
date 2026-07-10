from flask import request, jsonify
from flask_jwt_extended import jwt_required, verify_jwt_in_request
from . import api_v1_bp
from ...services.report_service import ReportService


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC endpoints — digunakan di landing page (HomeView), tanpa token
# ─────────────────────────────────────────────────────────────────────────────

@api_v1_bp.get('/public/report/summary')
def public_summary():
    return jsonify(ReportService.get_summary({})), 200


@api_v1_bp.get('/public/report/gender')
def public_by_gender():
    return jsonify(ReportService.get_by_gender({})), 200


@api_v1_bp.get('/public/report/bidang')
def public_by_bidang():
    return jsonify(ReportService.get_by_bidang({})), 200


@api_v1_bp.get('/public/report/timeseries')
def public_timeseries():
    return jsonify(ReportService.get_timeseries({})), 200


@api_v1_bp.get('/public/report/map')
def public_map():
    level = request.args.get('level', '1')
    return jsonify(ReportService.get_map_data(level)), 200


# ─────────────────────────────────────────────────────────────────────────────
# PROTECTED endpoints — wajib JWT token
# ─────────────────────────────────────────────────────────────────────────────

@api_v1_bp.get('/report/summary')
@jwt_required()
def summary():
    params = request.args.to_dict()
    return jsonify(ReportService.get_summary(params)), 200


@api_v1_bp.get('/report/gender')
@jwt_required()
def by_gender():
    params = request.args.to_dict()
    return jsonify(ReportService.get_by_gender(params)), 200


@api_v1_bp.get('/report/bidang')
@jwt_required()
def by_bidang():
    params = request.args.to_dict()
    return jsonify(ReportService.get_by_bidang(params)), 200


@api_v1_bp.get('/report/timeseries')
@jwt_required()
def timeseries():
    params = request.args.to_dict()
    return jsonify(ReportService.get_timeseries(params)), 200


@api_v1_bp.get('/report/desil')
@jwt_required()
def desil_summary():
    params = request.args.to_dict()
    return jsonify(ReportService.get_desil_summary(params)), 200


@api_v1_bp.get('/report/tabulate')
@jwt_required()
def tabulate():
    params = request.args.to_dict()
    return jsonify(ReportService.get_tabulate(params)), 200
