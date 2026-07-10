from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from . import api_v1_bp
from ...services.auth_service import AuthService


@api_v1_bp.post('/auth/login')
def login():
    """
    Login pengguna (tuser atau dtsen_akses)
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
              description: Email atau No. HP (dicari di tuser & t_dtsen_akses)
              example: user@email.com
            password:
              type: string
              description: Password plaintext, akan di-hash MD5 di server
              example: secret123
    responses:
      200:
        description: |
          Login berhasil. Kembalikan access_token, refresh_token, dan data user.
          Simpan access_token di header Authorization: Bearer <token> untuk setiap request.
        schema:
          type: object
          properties:
            access_token:  { type: string }
            refresh_token: { type: string }
            token_type:    { type: string, example: Bearer }
            user:
              type: object
              properties:
                id:        { type: integer }
                user_type: { type: string, enum: [tuser, dtsen] }
      401:
        description: Kredensial tidak valid
      403:
        description: Akun tidak aktif / kadaluarsa
    """
    data       = request.get_json() or {}
    identifier = data.get('identifier') or data.get('email') or data.get('notelp')
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
        description: Access token baru
      401:
        description: Refresh token tidak valid atau expired
    """
    identity     = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token, 'token_type': 'Bearer'}), 200


@api_v1_bp.get('/auth/me')
@jwt_required()
def me():
    """
    Verifikasi token & ambil profil user yang sedang login
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    description: |
      Frontend memanggil endpoint ini untuk memverifikasi bahwa user sudah login.
      Jika token valid, data profil dikembalikan.
      Jika token tidak valid / expired, JWT middleware otomatis mengembalikan 401.
    responses:
      200:
        description: Token valid, profil user dikembalikan
      401:
        description: Token tidak valid atau expired — user harus login ulang
    """
    identity = get_jwt_identity()
    result   = AuthService.get_current_user(identity)
    return jsonify(result), result.get('status_code', 200)


@api_v1_bp.post('/auth/logout')
@jwt_required()
def logout():
    """
    Logout — instruksi frontend untuk hapus token
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    description: |
      Server tidak menyimpan state token (stateless JWT).
      Response ini memberi sinyal ke frontend untuk menghapus
      access_token dan refresh_token dari storage (localStorage / SecureStorage).
    responses:
      200:
        description: Logout berhasil
      401:
        description: Token tidak valid
    """
    return jsonify({'message': 'Logout berhasil. Hapus token di sisi client.'}), 200
