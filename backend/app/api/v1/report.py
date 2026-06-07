from flask import request, jsonify
from flask_jwt_extended import jwt_required
from . import api_v1_bp
from ...services.report_service import ReportService


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
