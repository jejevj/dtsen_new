from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from . import api_v1_bp
from ...services.auth_service import AuthService
from ...services.otp_service  import generate_otp, save_otp, verify_otp, send_otp_email


@api_v1_bp.post('/auth/login')
def login():
    """
    Login → kirim OTP ke email, belum kembalikan token.
    Frontend redirect ke /verify-otp setelah ini.
    """
    data       = request.get_json() or {}
    identifier = data.get('identifier') or data.get('email') or data.get('notelp')
    password   = data.get('password')

    result = AuthService.login(identifier, password)
    if result.get('status_code', 200) != 200:
        return jsonify(result), result.get('status_code', 400)

    user = result.get('user', {})
    email = (
        user.get('email') or
        user.get('tuser_email') or
        identifier if '@' in (identifier or '') else None
    )

    otp_code = generate_otp()
    otp_key  = f"otp_email_{user.get('id')}_{user.get('user_type')}"
    save_otp(otp_key, otp_code)

    user_name = (
        user.get('user_fullname') or
        user.get('nama_lengkap') or
        user.get('email') or ''
    )

    sent = False
    if email:
        sent = send_otp_email(email, otp_code, user_name)

    return jsonify({
        'message':   'OTP telah dikirim ke email Anda.',
        'otp_sent':  sent,
        'otp_key':   otp_key,          # diteruskan ke frontend, dipakai saat verify
        'user_hint': {
            'id':        user.get('id'),
            'user_type': user.get('user_type'),
            'email_masked': _mask_email(email),
        }
    }), 200


@api_v1_bp.post('/auth/otp/verify')
def otp_verify():
    """
    Verifikasi OTP email → kembalikan JWT token jika benar.
    """
    data     = request.get_json() or {}
    otp_key  = data.get('otp_key', '')
    code     = data.get('code', '')

    if not otp_key or not code:
        return jsonify({'message': 'otp_key dan code wajib diisi.', 'status_code': 400}), 400

    if not verify_otp(otp_key, code):
        return jsonify({'message': 'Kode OTP salah atau sudah kadaluarsa.', 'status_code': 401}), 401

    # Ambil user dari otp_key: "otp_email_{id}_{user_type}"
    try:
        parts     = otp_key.split('_')
        user_id   = int(parts[2])
        user_type = parts[3]
    except Exception:
        return jsonify({'message': 'OTP key tidak valid.', 'status_code': 400}), 400

    identity = {'id': user_id, 'user_type': user_type}
    access_token  = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    user_data = AuthService.get_current_user(identity)
    user = user_data.get('user', {})

    return jsonify({
        'access_token':  access_token,
        'refresh_token': refresh_token,
        'token_type':    'Bearer',
        'user':          user,
    }), 200


@api_v1_bp.post('/auth/otp/resend')
def otp_resend():
    """Kirim ulang OTP ke email (perlu otp_key dari /login)."""
    data    = request.get_json() or {}
    otp_key = data.get('otp_key', '')

    if not otp_key:
        return jsonify({'message': 'otp_key wajib diisi.'}), 400

    try:
        parts     = otp_key.split('_')
        user_id   = int(parts[2])
        user_type = parts[3]
    except Exception:
        return jsonify({'message': 'OTP key tidak valid.'}), 400

    identity  = {'id': user_id, 'user_type': user_type}
    user_data = AuthService.get_current_user(identity)
    user      = user_data.get('user', {})
    email     = user.get('email') or user.get('tuser_email')

    otp_code  = generate_otp()
    save_otp(otp_key, otp_code)

    user_name = user.get('user_fullname') or user.get('nama_lengkap') or ''
    sent = send_otp_email(email, otp_code, user_name) if email else False

    return jsonify({'message': 'OTP berhasil dikirim ulang.', 'otp_sent': sent}), 200


@api_v1_bp.post('/auth/refresh')
@jwt_required(refresh=True)
def refresh():
    identity     = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token, 'token_type': 'Bearer'}), 200


@api_v1_bp.get('/auth/me')
@jwt_required()
def me():
    identity = get_jwt_identity()
    result   = AuthService.get_current_user(identity)
    return jsonify(result), result.get('status_code', 200)


@api_v1_bp.post('/auth/logout')
@jwt_required()
def logout():
    return jsonify({'message': 'Logout berhasil. Hapus token di sisi client.'}), 200


def _mask_email(email: str) -> str:
    if not email or '@' not in email:
        return ''
    local, domain = email.split('@', 1)
    masked = local[:2] + '***' if len(local) > 2 else '***'
    return f"{masked}@{domain}"
