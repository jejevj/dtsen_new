from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from . import api_v1_bp
from ...services.auth_service import AuthService, parse_identity_str, md5
from ...services.otp_service  import generate_otp, save_otp, verify_otp, send_otp_email, _get_option, OTP_TTL_MINUTES
from ...services.wa_service   import send_wa_otp, normalize_contact
from ...extensions            import db
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from datetime             import datetime


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


def _send_password_changed_email(
    to_email: str, user_name: str = '',
    user_id: int = 0, user_type: str = ''
) -> bool:
    """Kirim email notifikasi bahwa password berhasil diubah."""
    from flask import current_app

    status  = 'failed'
    error   = None
    subject = 'Notifikasi Perubahan Password - DTSEN'

    try:
        smtp_host   = _get_option('smtp_host')   or 'smtp.gmail.com'
        smtp_port   = int(_get_option('smtp_port') or 587)
        mail_acc    = _get_option('mail_account')
        smtp_secure = _get_option('smtp_secure') or 'TLS'
        mail_pass   = _get_option('mail_pass')
        mail_from   = _get_option('mail_content_from') or 'DTSEN Kemenag RI'
        mail_footer = _get_option('mail_content_footer') or 'Admin DTSEN Kemenag RI'
        nm_instansi = _get_option('nm_instansi') or 'Kementerian Agama RI'

        changed_at = datetime.now().strftime('%d %B %Y, %H:%M WIB')

        html_body = f"""
        <!DOCTYPE html>
        <html lang="id">
        <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
        <body style="margin:0;padding:0;background:#f4f6f8;font-family:Arial,sans-serif;">
          <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:32px 0;">
            <tr><td align="center">
              <table width="540" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">
                <!-- Header -->
                <tr>
                  <td style="background:#01696f;padding:28px 40px;text-align:center;">
                    <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:700;">DTSEN</h1>
                    <p style="margin:4px 0 0;color:#a7f3d0;font-size:12px;">{nm_instansi}</p>
                  </td>
                </tr>
                <!-- Body -->
                <tr>
                  <td style="padding:36px 40px;">
                    <p style="margin:0 0 8px;font-size:15px;color:#374151;">Halo, <strong>{user_name or 'Pengguna'}</strong></p>
                    <p style="margin:0 0 24px;font-size:14px;color:#6b7280;line-height:1.6;">
                      Password akun DTSEN Anda telah berhasil diubah. Semua sesi login sebelumnya
                      telah dihapus dan Anda perlu login kembali.
                    </p>
                    <!-- Info box -->
                    <table width="100%" cellpadding="0" cellspacing="0">
                      <tr><td style="background:#f0fdf4;border-left:4px solid #16a34a;border-radius:0 8px 8px 0;padding:16px 20px;">
                        <p style="margin:0 0 6px;font-size:12px;font-weight:700;color:#15803d;text-transform:uppercase;letter-spacing:0.05em;">&#128274; Detail Perubahan</p>
                        <p style="margin:0;font-size:13px;color:#374151;">Waktu: <strong>{changed_at}</strong></p>
                        <p style="margin:4px 0 0;font-size:13px;color:#374151;">Email: <strong>{to_email}</strong></p>
                      </td></tr>
                    </table>
                    <p style="margin:24px 0 8px;font-size:13px;color:#374151;">
                      <strong>&#9888;&#65039; Bukan Anda yang melakukan perubahan ini?</strong>
                    </p>
                    <p style="margin:0 0 24px;font-size:13px;color:#6b7280;line-height:1.6;">
                      Segera hubungi administrator sistem DTSEN untuk mengamankan akun Anda.
                    </p>
                    <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
                    <p style="margin:0;font-size:12px;color:#d1d5db;text-align:center;">
                      Email ini dikirim otomatis oleh sistem. Jangan balas email ini.
                    </p>
                  </td>
                </tr>
                <!-- Footer -->
                <tr>
                  <td style="background:#f9fafb;padding:20px 40px;border-top:1px solid #f3f4f6;text-align:center;">
                    <p style="margin:0;font-size:12px;color:#9ca3af;">{mail_footer}</p>
                    <p style="margin:4px 0 0;font-size:11px;color:#d1d5db;">{nm_instansi}</p>
                  </td>
                </tr>
              </table>
            </td></tr>
          </table>
        </body>
        </html>
        """

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = f"{mail_from} <{mail_acc}>"
        msg['To']      = to_email
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.ehlo()
            if smtp_secure.upper() == 'TLS':
                server.starttls()
                server.ehlo()
            server.login(mail_acc, mail_pass)
            server.sendmail(mail_acc, [to_email], msg.as_string())

        status = 'sent'
        return True

    except Exception as e:
        error = str(e)
        current_app.logger.error(f'[AUTH] _send_password_changed_email error: {e}')
        return False

    finally:
        if user_id:
            try:
                db.session.execute(
                    db.text(
                        "INSERT INTO t_log_smtp_dtsen "
                        "(user_id, user_type, to_email, subject, status, error_msg) "
                        "VALUES (:uid, :ut, :em, :sub, :st, :err)"
                    ),
                    {'uid': user_id, 'ut': user_type, 'em': to_email,
                     'sub': subject, 'st': status, 'err': error}
                )
                db.session.commit()
            except Exception as db_err:
                current_app.logger.error(f'[AUTH] smtp log error: {db_err}')
                db.session.rollback()


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

    identity_str  = _make_identity_str(user_id, user_type)
    access_token  = create_access_token(identity=identity_str)
    refresh_token = create_refresh_token(identity=identity_str)

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
    identity_str = get_jwt_identity()
    access_token = create_access_token(identity=identity_str)
    return jsonify({'access_token': access_token, 'token_type': 'Bearer'}), 200


# ── /auth/me ─────────────────────────────────────────────────────────────────
@api_v1_bp.get('/auth/me')
@jwt_required()
def me():
    identity_str = get_jwt_identity()
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


# ── Logout ────────────────────────────────────────────────────────────────────
@api_v1_bp.post('/auth/logout')
@jwt_required()
def logout():
    return jsonify({'message': 'Logout berhasil. Hapus token di sisi client.'}), 200


# ── Change Password ───────────────────────────────────────────────────────────
@api_v1_bp.post('/auth/change-password')
@jwt_required()
def change_password():
    """
    Ubah password user yang sedang login.
    Alur:
    1. Verifikasi password lama.
    2. Validasi password baru & konfirmasi.
    3. Update hash password di DB.
    4. Hapus semua OTP aktif milik user (reset semua sesi pending).
    5. Kirim email notifikasi perubahan password.
    6. Return 200 + flag `require_relogin=True` supaya frontend logout.
    """
    from flask import current_app

    identity_str = get_jwt_identity()
    identity     = parse_identity_str(identity_str)
    user_id      = identity.get('id')
    user_type    = identity.get('type')

    if not user_id or not user_type:
        return jsonify({'message': 'Token tidak valid.'}), 401

    data             = request.get_json() or {}
    old_password     = data.get('old_password', '').strip()
    new_password     = data.get('new_password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()

    # ── Validasi input ────────────────────────────────────────────────────────
    if not old_password:
        return jsonify({'message': 'Password lama wajib diisi.'}), 400
    if not new_password:
        return jsonify({'message': 'Password baru wajib diisi.'}), 400
    if len(new_password) < 8:
        return jsonify({'message': 'Password baru minimal 8 karakter.'}), 400
    if new_password != confirm_password:
        return jsonify({'message': 'Konfirmasi password tidak cocok.'}), 400
    if old_password == new_password:
        return jsonify({'message': 'Password baru tidak boleh sama dengan password lama.'}), 400

    # ── Ambil data user dari DB ───────────────────────────────────────────────
    if user_type == 'dtsen':
        row = db.session.execute(
            db.text("""
                SELECT dtsen_akses_id, dtsen_akses_password, nama_lengkap, email
                FROM t_dtsen_akses
                WHERE dtsen_akses_id = :uid AND deleted_at IS NULL
                LIMIT 1
            """),
            {'uid': user_id}
        ).fetchone()
    elif user_type == 'tuser':
        row = db.session.execute(
            db.text("""
                SELECT iduser, password, nama_lengkap, email
                FROM tuser
                WHERE iduser = :uid
                LIMIT 1
            """),
            {'uid': user_id}
        ).fetchone()
    else:
        return jsonify({'message': 'User tidak ditemukan.'}), 400

    if not row:
        return jsonify({'message': 'User tidak ditemukan.'}), 404

    db_user_id, stored_hash, user_name, user_email = row

    # ── Verifikasi password lama ──────────────────────────────────────────────
    if md5(old_password) != stored_hash:
        return jsonify({'message': 'Password lama salah.'}), 401

    new_hash = md5(new_password)

    # ── Update password di DB ─────────────────────────────────────────────────
    try:
        if user_type == 'dtsen':
            db.session.execute(
                db.text("""
                    UPDATE t_dtsen_akses
                    SET dtsen_akses_password = :hash
                    WHERE dtsen_akses_id = :uid
                """),
                {'hash': new_hash, 'uid': user_id}
            )
        else:
            db.session.execute(
                db.text("UPDATE tuser SET password = :hash WHERE iduser = :uid"),
                {'hash': new_hash, 'uid': user_id}
            )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'[AUTH] change-password DB error: {e}')
        return jsonify({'message': 'Gagal menyimpan password baru. Coba lagi.'}), 500

    # ── Reset semua sesi: hapus semua OTP aktif user ini ─────────────────────
    # Pattern key: otp_email_{user_id}_{user_type} dan otp_wa_{user_id}_{user_type}
    try:
        db.session.execute(
            db.text("""
                DELETE FROM t_otp_dtsen
                WHERE otp_key LIKE :pattern_email
                   OR otp_key LIKE :pattern_wa
            """),
            {
                'pattern_email': f'otp_email_{user_id}_{user_type}',
                'pattern_wa':    f'otp_wa_{user_id}_{user_type}',
            }
        )
        db.session.commit()
    except Exception as e:
        current_app.logger.warning(f'[AUTH] change-password: gagal hapus OTP: {e}')
        # Tidak fatal, lanjutkan

    # ── Kirim email notifikasi ────────────────────────────────────────────────
    email_to_use = user_email or _fetch_email_from_db(user_id, user_type)
    email_sent   = False
    if email_to_use:
        email_sent = _send_password_changed_email(
            to_email  = email_to_use,
            user_name = user_name or '',
            user_id   = user_id,
            user_type = user_type,
        )
    else:
        current_app.logger.warning(
            f'[AUTH] change-password: user_id={user_id} tidak memiliki email, notifikasi tidak dikirim.'
        )

    current_app.logger.info(
        f'[AUTH] change-password SUCCESS user_id={user_id} user_type={user_type} '
        f'email_sent={email_sent}'
    )

    return jsonify({
        'message':        'Password berhasil diubah. Silakan login kembali.',
        'email_sent':     email_sent,
        'require_relogin': True,   # sinyal ke frontend untuk logout
    }), 200
