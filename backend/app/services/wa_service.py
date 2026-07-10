"""
WhatsApp OTP Service via Google Apps Script gateway.
Menggunakan urllib (built-in) — tidak perlu library tambahan.
Biaya tetap: Rp 650 per hit (dicatat di t_log_wa_dtsen).
"""
import json
import re
import urllib.request
from flask        import current_app
from ..extensions import db

WA_GATEWAY_URL = (
    'https://script.google.com/macros/s/'
    'AKfycbxhGs3fRj7eB-cTIkQgvwz_1UGquheoh11fREdoEdPnVb4kGzS1lxcYb-4HwNp8pXLV/exec'
)
WA_KEY  = '1Z8eo8ByZ1Mw35FWfiT6LUepGaLj5suwDGnG_OcYn3dY'
WA_COST = 650  # Rp per hit


def normalize_contact(phone: str) -> str:
    """
    Normalisasi nomor HP ke format 628xxx.
    Contoh:
      08531234567  → 628531234567
      +628531234567 → 628531234567
      628531234567  → 628531234567
      8531234567    → 628531234567
    """
    if not phone:
        return ''
    # Hapus karakter non-digit kecuali tanda + di depan
    phone = re.sub(r'[\s\-\.\(\)]', '', phone).strip()
    # Hapus tanda +
    phone = phone.lstrip('+')
    # Awalan 0 → 62
    if phone.startswith('0'):
        phone = '62' + phone[1:]
    # Awalan 8 (tanpa kode negara) → 628
    elif phone.startswith('8'):
        phone = '62' + phone
    # Sudah 62xxx, biarkan
    # Validasi minimal 10 digit
    if not re.match(r'^62\d{9,13}$', phone):
        return ''
    return phone


def send_wa_otp(phone: str, otp_code: str, user_id: int, user_type: str) -> bool:
    """
    Kirim OTP via WA gateway. Catat hasilnya ke t_log_wa_dtsen.
    Return True jika berhasil.
    """
    contact = normalize_contact(phone)
    status  = 'failed'
    error   = None

    if not contact:
        error = f'Nomor tidak valid setelah normalisasi: {phone!r}'
        current_app.logger.warning(f'[WA] {error}')
        _log(user_id, user_type, phone or '', status, error)
        return False

    try:
        payload = json.dumps({
            'key':     WA_KEY,
            'contact': contact,
            'code':    otp_code,
        }).encode('utf-8')

        req = urllib.request.Request(
            WA_GATEWAY_URL,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode('utf-8', errors='ignore')
            current_app.logger.info(f'[WA] gateway response: {body[:200]}')

        status = 'sent'
        return True

    except Exception as e:
        error = str(e)
        current_app.logger.error(f'[WA] send_wa_otp error to {contact}: {e}')
        return False

    finally:
        if status == 'sent' or error != f'Nomor tidak valid setelah normalisasi: {phone!r}':
            _log(user_id, user_type, contact, status, error)


def _log(user_id: int, user_type: str, contact: str, status: str, error):
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
