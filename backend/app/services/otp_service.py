"""
OTP Service
- Generate & store OTP di Redis (jika ada) atau in-memory fallback
- Kirim email via Gmail SMTP (config dari ic_options)
"""
import random
import string
import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from datetime             import datetime, timedelta
from flask                import current_app
from ..extensions         import db

# In-memory store: { otp_key: {code, expires_at} }
_otp_store: dict = {}
_lock = threading.Lock()

OTP_TTL_MINUTES = 10
OTP_LENGTH      = 6


def _get_option(opt_name: str) -> str:
    """Ambil nilai dari ic_options."""
    row = db.session.execute(
        db.text("SELECT opt_values FROM ic_options WHERE opt_name = :n LIMIT 1"),
        {'n': opt_name}
    ).fetchone()
    return row[0] if row else ''


def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=OTP_LENGTH))


def save_otp(key: str, code: str) -> None:
    """Simpan OTP dengan TTL."""
    expires = datetime.utcnow() + timedelta(minutes=OTP_TTL_MINUTES)
    with _lock:
        _otp_store[key] = {'code': code, 'expires_at': expires}


def verify_otp(key: str, code: str) -> bool:
    """Verifikasi OTP; hapus jika benar."""
    with _lock:
        entry = _otp_store.get(key)
        if not entry:
            return False
        if datetime.utcnow() > entry['expires_at']:
            del _otp_store[key]
            return False
        if entry['code'] != code.strip():
            return False
        del _otp_store[key]
        return True


def send_otp_email(to_email: str, otp_code: str, user_name: str = '') -> bool:
    """
    Kirim OTP ke email via SMTP (config dari ic_options).
    Return True jika berhasil.
    """
    try:
        smtp_host   = _get_option('smtp_host')   or 'smtp.gmail.com'
        smtp_port   = int(_get_option('smtp_port') or 587)
        mail_acc    = _get_option('mail_account')
        mail_pass   = _get_option('mail_pass')
        mail_from   = _get_option('mail_content_from') or 'DTSEN Kemenag RI'
        mail_footer = _get_option('mail_content_footer') or 'Admin DTSEN Kemenag RI'
        nm_instansi = _get_option('nm_instansi')   or 'Kementerian Agama RI'

        subject = f'Kode OTP Login DTSEN - {otp_code}'

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
                    <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:700;letter-spacing:0.5px;">DTSEN</h1>
                    <p style="margin:4px 0 0;color:#a7f3d0;font-size:12px;">{nm_instansi}</p>
                  </td>
                </tr>

                <!-- Body -->
                <tr>
                  <td style="padding:36px 40px;">
                    <p style="margin:0 0 8px;font-size:15px;color:#374151;">Halo, <strong>{user_name or 'Pengguna'}</strong></p>
                    <p style="margin:0 0 24px;font-size:14px;color:#6b7280;line-height:1.6;">
                      Kami menerima permintaan login ke sistem <strong>DTSEN — Data Terpadu Sosial Ekonomi Nasional</strong>.
                      Gunakan kode OTP berikut untuk menyelesaikan verifikasi:
                    </p>

                    <!-- OTP Box -->
                    <table width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td align="center" style="padding:16px 0;">
                          <div style="display:inline-block;background:#f0fdf4;border:2px dashed #01696f;border-radius:12px;padding:18px 40px;">
                            <span style="font-size:38px;font-weight:800;letter-spacing:10px;color:#01696f;font-family:'Courier New',monospace;">{otp_code}</span>
                          </div>
                        </td>
                      </tr>
                    </table>

                    <p style="margin:20px 0 8px;font-size:13px;color:#9ca3af;text-align:center;">
                      ⏱ Kode berlaku selama <strong>{OTP_TTL_MINUTES} menit</strong> sejak email ini dikirim.
                    </p>
                    <p style="margin:0 0 24px;font-size:13px;color:#9ca3af;text-align:center;">
                      Jika Anda tidak merasa melakukan login, abaikan email ini.
                    </p>

                    <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
                    <p style="margin:0;font-size:12px;color:#d1d5db;text-align:center;">
                      Jangan bagikan kode OTP ini kepada siapapun, termasuk petugas {nm_instansi}.
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
            server.starttls()
            server.login(mail_acc, mail_pass)
            server.sendmail(mail_acc, [to_email], msg.as_string())

        return True

    except Exception as e:
        current_app.logger.error(f'[OTP] send_otp_email error: {e}')
        return False
