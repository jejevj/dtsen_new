from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from . import api_v1_bp
from ...services.auth_service import AuthService


@api_v1_bp.post('/auth/login')
def login():
    """Login user and return JWT tokens."""
    data = request.get_json()
    result = AuthService.login(data.get('email'), data.get('password'))
    return jsonify(result), result.get('status_code', 200)


@api_v1_bp.post('/auth/refresh')
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token}), 200


@api_v1_bp.get('/auth/me')
@jwt_required()
def me():
    """Get current authenticated user."""
    identity = get_jwt_identity()
    result = AuthService.get_user(identity)
    return jsonify(result), 200
