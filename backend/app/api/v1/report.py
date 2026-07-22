from flask import request, jsonify
from flask_jwt_extended import jwt_required
from . import api_v1_bp
from ...services.report_service import ReportService


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC endpoints — landing page, tanpa token
# ─────────────────────────────────────────────────────────────────────────────

@api_v1_bp.get('/public/report/paramtahun')
def public_param_tahun():
    params = request.args.to_dict()
    return jsonify(ReportService.get_by_param_tahun(params)), 200

@api_v1_bp.get('/public/report/summary')
def public_summary():
    tahun = request.args.get('tahun', None)
    return jsonify(ReportService.get_summary({'tahun': tahun})), 200


@api_v1_bp.get('/public/report/gender')
def public_by_gender():
    tahun = request.args.get('tahun', None)
    return jsonify(ReportService.get_by_gender({'tahun': tahun})), 200


@api_v1_bp.get('/public/report/bidang')
def public_by_bidang():
    tahun = request.args.get('tahun', None)
    return jsonify(ReportService.get_by_bidang({'tahun': tahun})), 200


@api_v1_bp.get('/public/report/timeseries')
def public_timeseries():
    tahun = request.args.get('tahun', None)
    return jsonify(ReportService.get_timeseries({'tahun': tahun})), 200


@api_v1_bp.get('/public/report/map')
def public_map():
    """
    Endpoint peta publik.
      ?level=1                              -> agregat per provinsi
      ?level=2&provinsi_kode=32             -> kabkota dalam satu provinsi
      ?level=3&kabkota_kode=3201            -> kecamatan dalam satu kabkota
    """
    
    tahun         = request.args.get('tahun', None)
    provinsi_kode = request.args.get('provinsi_kode', None)
    kabkota_kode  = request.args.get('kabkota_kode',  None)
    return jsonify(ReportService.get_map_data({
        'tahun': tahun,
        'provinsi_kode': provinsi_kode,
        'kabkota_kode': kabkota_kode
    })), 200


# ─────────────────────────────────────────────────────────────────────────────
# PROTECTED endpoints — wajib JWT token
# ─────────────────────────────────────────────────────────────────────────────

@api_v1_bp.get('/report/paramtahun')
@jwt_required()
def paramtahun():
    params = request.args.to_dict()
    return jsonify(ReportService.get_by_param_tahun(params)), 200

@api_v1_bp.get('/report/paramlaz')
@jwt_required()
def paramlaz():
    params = request.args.to_dict()
    return jsonify(ReportService.get_param_laz(params)), 200

@api_v1_bp.get('/report/paramprov')
@jwt_required()
def paramprov():
    params = request.args.to_dict()
    return jsonify(ReportService.get_param_prov(params)), 200

@api_v1_bp.get('/report/paramkab')
@jwt_required()
def paramkab():
    params = request.args.to_dict()
    return jsonify(ReportService.get_param_kab(params)), 200

@api_v1_bp.get('/report/paramkec')
@jwt_required()
def paramkec():
    params = request.args.to_dict()
    return jsonify(ReportService.get_param_kec(params)), 200

@api_v1_bp.get('/report/basewil')
@jwt_required()
def basewil():
    params = request.args.to_dict()
    return jsonify(ReportService.get_baseline_wilayah(params)), 200

@api_v1_bp.get('/report/datawil')
@jwt_required()
def datawil():
    params = request.args.to_dict()
    return jsonify(ReportService.get_data_wilayah(params)), 200

@api_v1_bp.get('/report/basedesil')
@jwt_required()
def basedesil():
    params = request.args.to_dict()
    return jsonify(ReportService.get_baseline_desil(params)), 200

@api_v1_bp.get('/report/datadesil')
@jwt_required()
def datadesil():
    params = request.args.to_dict()
    return jsonify(ReportService.get_data_desil(params)), 200

@api_v1_bp.get('/report/databidang')
@jwt_required()
def databidang():
    params = request.args.to_dict()
    return jsonify(ReportService.get_data_bidang(params)), 200

@api_v1_bp.get('/report/datausia')
@jwt_required()
def datausia():
    params = request.args.to_dict()
    return jsonify(ReportService.get_data_usia(params)), 200

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
