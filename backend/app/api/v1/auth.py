from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from . import api_v1_bp
from ...services.auth_service import AuthService, parse_identity_str
from ...services.otp_service  import generate_otp, save_otp, verify_otp, send_otp_email
from ...services.wa_service   import send_wa_otp, normalize_contact
from ...extensions            import db


# ── Helpers ───────────────────────────────────────────────────────────────────
def _mask_email(email: str) -> str:
    if not email or '@' not in email:
        return ''
    local, domain = email.split('@', 1)
    masked = local[:2] + '***' if len(local) > 2 else '***'
    return f'{masked}@{domain}'

def _mask_phone(phone: str) -> str:
    if not phone or len(phone) < 5:
        return phone or ''
    return phone[:4] + '****' + phone[-2:]

def _parse_otp_key(otp_key: str):
    parts     = otp_key.split('_')
    user_id   = int(parts[2])
    user_type = parts[3]
    return user_id, user_type

def _make_identity_str(user_id: int, user_type: str) -> str:
    """Buat identity string 'type:id' untuk JWT subject."""
    return f"{user_type}:{user_id}"

def _get_phone(user: dict) -> str:
    for field in ('notelp', 'tuser_notelp', 'phone', 'handphone', 'no_hp', 'telepon'):
        val = user.get(field)
        if val and str(val).strip():
            return normalize_contact(str(val).strip())
    return ''

def _fetch_phone_from_db(user_id: int, user_type: str) -> str:
    try:
        if user_type == 'tuser':
            row = db.session.execute(
                db.text("SELECT notelp FROM tuser WHERE iduser = :id LIMIT 1"),
                {'id': user_id}
            ).fetchone()
        else:
            row = db.session.execute(
                db.text("SELECT notelp FROM t_dtsen_akses WHERE dtsen_akses_id = :id LIMIT 1"),
                {'id': user_id}
            ).fetchone()
        if row and row[0] and str(row[0]).strip():
            return normalize_contact(str(row[0]).strip())
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f'[AUTH] _fetch_phone_from_db error: {e}')
    return ''

def _fetch_email_from_db(user_id: int, user_type: str) -> str:
    try:
        if user_type == 'tuser':
            row = db.session.execute(
                db.text("SELECT email FROM tuser WHERE iduser = :id LIMIT 1"),
                {'id': user_id}
            ).fetchone()
        else:
            row = db.session.execute(
                db.text("SELECT email FROM t_dtsen_akses WHERE dtsen_akses_id = :id LIMIT 1"),
                {'id': user_id}
            ).fetchone()
        if row and row[0] and str(row[0]).strip():
            return str(row[0]).strip()
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f'[AUTH] _fetch_email_from_db error: {e}')
    return ''


# ── Step 1: Login → kirim OTP Email ──────────────────────────────────────────
@api_v1_bp.post('/auth/login')
def login():
    data       = request.get_json() or {}
    identifier = data.get('identifier') or data.get('email') or data.get('notelp')
    password   = data.get('password')

    result = AuthService.login(identifier, password)
    if result.get('status_code', 200) != 200:
        return jsonify(result), result.get('status_code', 400)

    user      = result.get('user', {})
    user_id   = user.get('id')
    user_type = user.get('user_type', '')
    user_name = user.get('user_fullname') or user.get('nama_lengkap') or ''
    email     = (
        user.get('email') or user.get('tuser_email') or
        (identifier if '@' in (identifier or '') else None)
    )

    phone = _get_phone(user) or _fetch_phone_from_db(user_id, user_type)

    otp_code = generate_otp()
    otp_key  = f'otp_email_{user_id}_{user_type}'
    save_otp(otp_key, otp_code)

    sent = send_otp_email(email, otp_code, user_name, user_id, user_type) if email else False

    return jsonify({
        'message':   'OTP email telah dikirim.',
        'otp_sent':  sent,
        'otp_key':   otp_key,
        'user_hint': {
            'id':           user_id,
            'user_type':    user_type,
            'email_masked': _mask_email(email),
            'phone':        phone,
            'phone_masked': _mask_phone(phone),
            'identifier':   identifier,
        }
    }), 200


# ── Step 2: Verifikasi OTP Email → kirim OTP WA ──────────────────────────
@api_v1_bp.post('/auth/otp/verify-email')
def otp_verify_email():
    from flask import current_app
    data    = request.get_json() or {}
    otp_key = data.get('otp_key', '')
    code    = data.get('code', '')

    if not otp_key or not code:
        return jsonify({'message': 'otp_key dan code wajib diisi.'}), 400

    if not verify_otp(otp_key, code, soft_delete=True):
        return jsonify({'message': 'Kode OTP email salah atau sudah kadaluarsa.'}), 401

    user_id, user_type = _parse_otp_key(otp_key)
    identity_dict = {'type': user_type, 'id': user_id}

    user_data = AuthService.get_current_user(identity_dict)
    user      = user_data.get('user', {})
    phone     = _get_phone(user) or _fetch_phone_from_db(user_id, user_type)

    current_app.logger.info(
        f'[AUTH] verify-email user_id={user_id} user_type={user_type} '
        f'payload_notelp={user.get("notelp")!r} resolved_phone={phone!r}'
    )

    wa_code = generate_otp()
    wa_key  = f'otp_wa_{user_id}_{user_type}'
    save_otp(wa_key, wa_code)

    sent = send_wa_otp(phone, wa_code, user_id, user_type) if phone else False

    return jsonify({
        'message':     'OTP email valid. OTP WhatsApp telah dikirim.' if sent else
                       'OTP email valid. Nomor HP tidak tersedia, WA tidak dikirim.',
        'wa_otp_sent': sent,
        'wa_otp_key':  wa_key,
        'user_hint': {
            'id':           user_id,
            'user_type':    user_type,
            'phone_masked': _mask_phone(phone),
        }
    }), 200


# ── Step 3: Verifikasi OTP WA → kembalikan JWT ───────────────────────────
@api_v1_bp.post('/auth/otp/verify-wa')
def otp_verify_wa():
    from flask import current_app
    data   = request.get_json() or {}
    wa_key = data.get('wa_otp_key') or data.get('otp_key', '')
    code   = data.get('code', '')

    current_app.logger.info(f'[AUTH] verify-wa wa_key={wa_key!r} code={code!r}')

    if not wa_key or not code:
        return jsonify({'message': 'wa_otp_key dan code wajib diisi.'}), 400

    if not wa_key.startswith('otp_wa_'):
        current_app.logger.warning(f'[AUTH] verify-wa: key bukan WA key: {wa_key!r}')
        return jsonify({'message': 'Key OTP tidak valid untuk verifikasi WhatsApp.'}), 400

    if not verify_otp(wa_key, code, soft_delete=False):
        return jsonify({'message': 'Kode OTP WhatsApp salah atau sudah kadaluarsa.'}), 401

    user_id, user_type = _parse_otp_key(wa_key)

    # Identity sebagai STRING untuk JWT subject (wajib di Flask-JWT-Extended v4+)
    identity_str  = _make_identity_str(user_id, user_type)
    access_token  = create_access_token(identity=identity_str)
    refresh_token = create_refresh_token(identity=identity_str)

    # Ambil payload user dengan dict identity (helper internal)
    identity_dict = {'type': user_type, 'id': user_id}
    user_data = AuthService.get_current_user(identity_dict)
    user      = user_data.get('user', {})

    if not user.get('email'):
        email_from_db = _fetch_email_from_db(user_id, user_type)
        if email_from_db:
            user['email'] = email_from_db
        elif user.get('notelp'):
            user['email'] = user['notelp']

    return jsonify({
        'access_token':  access_token,
        'refresh_token': refresh_token,
        'token_type':    'Bearer',
        'user':          user,
    }), 200


# ── Resend OTP Email ───────────────────────────────────────────────────────
@api_v1_bp.post('/auth/otp/resend-email')
def otp_resend_email():
    data    = request.get_json() or {}
    otp_key = data.get('otp_key', '')
    if not otp_key:
        return jsonify({'message': 'otp_key wajib diisi.'}), 400

    user_id, user_type = _parse_otp_key(otp_key)
    user_data = AuthService.get_current_user({'type': user_type, 'id': user_id})
    user      = user_data.get('user', {})
    email     = user.get('email') or user.get('tuser_email') or ''
    user_name = user.get('user_fullname') or user.get('nama_lengkap') or ''

    otp_code = generate_otp()
    save_otp(otp_key, otp_code)
    sent = send_otp_email(email, otp_code, user_name, user_id, user_type) if email else False
    return jsonify({'message': 'OTP email dikirim ulang.', 'otp_sent': sent}), 200


# ── Resend OTP WA ──────────────────────────────────────────────────────────
@api_v1_bp.post('/auth/otp/resend-wa')
def otp_resend_wa():
    data   = request.get_json() or {}
    wa_key = data.get('wa_otp_key') or data.get('otp_key', '')
    if not wa_key:
        return jsonify({'message': 'wa_otp_key wajib diisi.'}), 400

    user_id, user_type = _parse_otp_key(wa_key)
    user_data = AuthService.get_current_user({'type': user_type, 'id': user_id})
    user      = user_data.get('user', {})
    phone     = _get_phone(user) or _fetch_phone_from_db(user_id, user_type)

    wa_code = generate_otp()
    save_otp(wa_key, wa_code)
    sent = send_wa_otp(phone, wa_code, user_id, user_type) if phone else False
    return jsonify({'message': 'OTP WhatsApp dikirim ulang.', 'wa_otp_sent': sent}), 200


# ── Refresh token ────────────────────────────────────────────────────────────
@api_v1_bp.post('/auth/refresh')
@jwt_required(refresh=True)
def refresh():
    identity_str = get_jwt_identity()          # sudah string 'type:id'
    access_token = create_access_token(identity=identity_str)
    return jsonify({'access_token': access_token, 'token_type': 'Bearer'}), 200


# ── /auth/me ────────────────────────────────────────────────────────────────────
@api_v1_bp.get('/auth/me')
@jwt_required()
def me():
    identity_str = get_jwt_identity()          # string 'type:id'
    identity     = parse_identity_str(identity_str)
    result       = AuthService.get_current_user(identity)

    user = result.get('user', {})
    if isinstance(user, dict) and not user.get('email'):
        user_id   = identity.get('id')
        user_type = identity.get('type')
        email_from_db = _fetch_email_from_db(user_id, user_type)
        if email_from_db:
            user['email'] = email_from_db
        elif user.get('notelp'):
            user['email'] = user['notelp']

    return jsonify(result), result.get('status_code', 200)


# ── Logout ──────────────────────────────────────────────────────────────────────
@api_v1_bp.post('/auth/logout')
@jwt_required()
def logout():
    return jsonify({'message': 'Logout berhasil. Hapus token di sisi client.'}), 200
