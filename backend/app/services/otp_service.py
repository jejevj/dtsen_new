"""
OTP Service
- Generate & store OTP di database (t_otp_dtsen) — persistent across restarts
- Kirim email via Gmail SMTP (config dari ic_options)
- Log ke t_log_smtp_dtsen
"""
import random
import string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from datetime             import datetime, timedelta
from flask                import current_app
from ..extensions         import db

OTP_TTL_MINUTES = 10
OTP_LENGTH      = 6


def _get_option(opt_name: str) -> str:
    row = db.session.execute(
        db.text("SELECT opt_values FROM ic_options WHERE opt_name = :n LIMIT 1"),
        {'n': opt_name}
    ).fetchone()
    return row[0] if row else ''


def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=OTP_LENGTH))


def save_otp(key: str, code: str) -> None:
    """Simpan atau update OTP ke database."""
    expires = datetime.utcnow() + timedelta(minutes=OTP_TTL_MINUTES)
    db.session.execute(
        db.text("""
            INSERT INTO t_otp_dtsen (otp_key, code, expires_at, used)
            VALUES (:key, :code, :exp, 0)
            ON DUPLICATE KEY UPDATE
                code       = VALUES(code),
                expires_at = VALUES(expires_at),
                used       = 0
        """),
        {'key': key, 'code': code, 'exp': expires}
    )
    db.session.commit()


def verify_otp(key: str, code: str, soft_delete: bool = False) -> bool:
    """
    Verifikasi OTP.
    - soft_delete=False (default): hapus row setelah valid (untuk WA step final)
    - soft_delete=True: tandai used=1 tapi JANGAN hapus (untuk Email step tengah)
    """
    row = db.session.execute(
        db.text("""
            SELECT id, code, expires_at, used
            FROM t_otp_dtsen
            WHERE otp_key = :key
            LIMIT 1
        """),
        {'key': key}
    ).fetchone()

    if not row:
        return False

    otp_id, stored_code, expires_at, used = row

    if used:
        return False

    if datetime.utcnow() > expires_at:
        db.session.execute(db.text("DELETE FROM t_otp_dtsen WHERE id = :id"), {'id': otp_id})
        db.session.commit()
        return False

    if stored_code != code.strip():
        return False

    if soft_delete:
        # Tandai used=1, biarkan row ada supaya tidak bisa dipakai ulang
        db.session.execute(
            db.text("UPDATE t_otp_dtsen SET used = 1 WHERE id = :id"),
            {'id': otp_id}
        )
    else:
        # Hapus permanen — dipakai untuk step final (verify-wa)
        db.session.execute(db.text("DELETE FROM t_otp_dtsen WHERE id = :id"), {'id': otp_id})
    db.session.commit()
    return True


def send_otp_email(
    to_email: str, otp_code: str, user_name: str = '',
    user_id: int = 0, user_type: str = ''
) -> bool:
    status = 'failed'
    error  = None
    subject = f'Kode OTP Login DTSEN - {otp_code}'

    try:
        smtp_host   = _get_option('smtp_host')   or 'smtp.gmail.com'
        smtp_port   = int(_get_option('smtp_port') or 587)
        mail_acc    = _get_option('mail_account')
        smtp_secure = _get_option('smtp_secure') or 'TLS'
        mail_pass   = _get_option('sendinblue_key_v3') or _get_option('mail_pass')
        mail_from   = _get_option('mail_content_from') or 'DTSEN Kemenag RI'
        mail_footer = _get_option('mail_content_footer') or 'Admin DTSEN Kemenag RI'
        nm_instansi = _get_option('nm_instansi')   or 'Kementerian Agama RI'

        html_body = f"""
        <!DOCTYPE html>
        <html lang="id">
        <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
        <body style="margin:0;padding:0;background:#f4f6f8;font-family:Arial,sans-serif;">
          <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:32px 0;">
            <tr><td align="center">
              <table width="540" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">
                <tr>
                  <td style="background:#01696f;padding:28px 40px;text-align:center;">
                    <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:700;">DTSEN</h1>
                    <p style="margin:4px 0 0;color:#a7f3d0;font-size:12px;">{nm_instansi}</p>
                  </td>
                </tr>
                <tr>
                  <td style="padding:36px 40px;">
                    <p style="margin:0 0 8px;font-size:15px;color:#374151;">Halo, <strong>{user_name or 'Pengguna'}</strong></p>
                    <p style="margin:0 0 24px;font-size:14px;color:#6b7280;line-height:1.6;">
                      Kami menerima permintaan login ke sistem <strong>DTSEN</strong>.
                      Gunakan kode OTP berikut untuk menyelesaikan verifikasi tahap pertama:
                    </p>
                    <table width="100%" cellpadding="0" cellspacing="0">
                      <tr><td align="center" style="padding:16px 0;">
                        <div style="display:inline-block;background:#f0fdf4;border:2px dashed #01696f;border-radius:12px;padding:18px 40px;">
                          <span style="font-size:38px;font-weight:800;letter-spacing:10px;color:#01696f;font-family:'Courier New',monospace;">{otp_code}</span>
                        </div>
                      </td></tr>
                    </table>
                    <p style="margin:20px 0 8px;font-size:13px;color:#9ca3af;text-align:center;">
                      &#9201; Kode berlaku selama <strong>{OTP_TTL_MINUTES} menit</strong>.
                    </p>
                    <p style="margin:0 0 24px;font-size:13px;color:#9ca3af;text-align:center;">
                      Setelah OTP email, Anda akan diminta memasukkan OTP WhatsApp.
                    </p>
                    <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
                    <p style="margin:0;font-size:12px;color:#d1d5db;text-align:center;">
                      Jangan bagikan kode ini kepada siapapun, termasuk petugas {nm_instansi}.
                    </p>
                  </td>
                </tr>
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
        current_app.logger.info(
            f"""
            SMTP CONFIG:
            host={smtp_host}
            port={smtp_port}
            account={mail_acc}
            secure={smtp_secure}"""
            )

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
        current_app.logger.error(f'[OTP] send_otp_email error: {e}')
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
                current_app.logger.error(f'[OTP] smtp log error: {db_err}')
                db.session.rollback()
