from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from . import api_v1_bp
from ...services.auth_service import AuthService


@api_v1_bp.post('/auth/login')
def login():
    """
    Login pengguna
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - identifier
            - password
          properties:
            identifier:
              type: string
              example: admin
              description: Email, username, atau NIP
            password:
              type: string
              example: secret123
    responses:
      200:
        description: Login berhasil, mengembalikan access & refresh token
      401:
        description: Kredensial tidak valid
    """
    data       = request.get_json() or {}
    identifier = data.get('identifier') or data.get('email')
    password   = data.get('password')
    result     = AuthService.login(identifier, password)
    return jsonify(result), result.get('status_code', 200)


@api_v1_bp.post('/auth/refresh')
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    responses:
      200:
        description: Access token baru berhasil dibuat
      401:
        description: Refresh token tidak valid atau expired
    """
    identity     = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token}), 200


@api_v1_bp.get('/auth/me')
@jwt_required()
def me():
    """
    Get profil user yang sedang login
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    responses:
      200:
        description: Data profil user
      401:
        description: Token tidak valid atau expired
    """
    identity = get_jwt_identity()
    result   = AuthService.get_user(identity)
    return jsonify(result), 200
