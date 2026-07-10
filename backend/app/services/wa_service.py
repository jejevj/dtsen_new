"""
WhatsApp OTP Service via Google Apps Script gateway.
Biaya tetap: Rp 650 per hit (dicatat di t_log_wa_dtsen).
"""
import requests
from flask  import current_app
from ..extensions import db

WA_GATEWAY_URL = (
    'https://script.google.com/macros/s/'
    'AKfycbxhGs3fRj7eB-cTIkQgvwz_1UGquheoh11fREdoEdPnVb4kGzS1lxcYb-4HwNp8pXLV/exec'
)
WA_KEY  = '1Z8eo8ByZ1Mw35FWfiT6LUepGaLj5suwDGnG_OcYn3dY'
WA_COST = 650  # Rp per hit


def _normalize_contact(phone: str) -> str:
    """Konversi 08xxx → 628xxx."""
    if not phone:
        return ''
    phone = phone.strip().replace('-', '').replace(' ', '')
    if phone.startswith('0'):
        phone = '62' + phone[1:]
    elif phone.startswith('+'):
        phone = phone[1:]
    return phone


def send_wa_otp(phone: str, otp_code: str, user_id: int, user_type: str) -> bool:
    """
    Kirim OTP via WA gateway. Catat hasilnya ke t_log_wa_dtsen.
    Return True jika berhasil.
    """
    contact = _normalize_contact(phone)
    status  = 'failed'
    error   = None

    try:
        resp = requests.post(
            WA_GATEWAY_URL,
            json={'key': WA_KEY, 'contact': contact, 'code': otp_code},
            timeout=15,
            allow_redirects=True,
        )
        resp.raise_for_status()
        # Gateway mengembalikan JSON; anggap berhasil jika status HTTP 2xx
        status = 'sent'
        return True
    except Exception as e:
        error = str(e)
        current_app.logger.error(f'[WA] send_wa_otp error to {contact}: {e}')
        return False
    finally:
        try:
            db.session.execute(
                db.text(
                    "INSERT INTO t_log_wa_dtsen "
                    "(user_id, user_type, contact, status, cost, error_msg) "
                    "VALUES (:uid, :ut, :ct, :st, :cost, :err)"
                ),
                {'uid': user_id, 'ut': user_type, 'ct': contact,
                 'st': status, 'cost': WA_COST, 'err': error}
            )
            db.session.commit()
        except Exception as db_err:
            current_app.logger.error(f'[WA] log insert error: {db_err}')
            db.session.rollback()
