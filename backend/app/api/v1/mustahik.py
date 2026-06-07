from flask import request, jsonify
from flask_jwt_extended import jwt_required
from . import api_v1_bp
from ...services.mustahik_service import MustahikService


@api_v1_bp.get('/mustahik')
@jwt_required()
def list_mustahik():
    """List mustahik with filters and pagination."""
    params = request.args.to_dict()
    result = MustahikService.get_list(params)
    return jsonify(result), 200


@api_v1_bp.get('/mustahik/<string:nik_hashed>')
@jwt_required()
def detail_mustahik(nik_hashed):
    """Get detail mustahik by hashed NIK."""
    result = MustahikService.get_detail(nik_hashed)
    return jsonify(result), 200
