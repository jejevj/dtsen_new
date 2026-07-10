"""
WhatsApp OTP Service via Google Apps Script gateway.
GAS mengeluarkan redirect 302 saat POST — tangani manual tanpa allow_redirects.
Sukses ditentukan dari response body: {"status": "Sukses", ...}
"""
import json
import re
import requests as _requests
from flask        import current_app
from ..extensions import db

WA_GATEWAY_URL = (
    'https://script.google.com/macros/s/'
    'AKfycbxhGs3fRj7eB-cTIkQgvwz_1UGquheoh11fREdoEdPnVb4kGzS1lxcYb-4HwNp8pXLV/exec'
)
WA_KEY  = '1Z8eo8ByZ1Mw35FWfiT6LUepGaLj5suwDGnG_OcYn3dY'
WA_COST = 650  # Rp per hit (selalu dikenakan jika status=Sukses)


def normalize_contact(phone: str) -> str:
    """
    Normalisasi nomor HP ke format 628xxx.
      08531234567   → 628531234567
      8531234567    → 628531234567
      +628531234567 → 628531234567
      628531234567  → 628531234567
    """
    if not phone:
        return ''
    phone = re.sub(r'[\s\-\.\(\)]', '', phone).strip().lstrip('+')
    if phone.startswith('0'):
        phone = '62' + phone[1:]
    elif phone.startswith('8'):
        phone = '62' + phone
    if not re.match(r'^62\d{9,13}$', phone):
        return ''
    return phone


def _is_success(resp_body: str) -> bool:
    """Cek response GAS: sukses jika JSON status == 'Sukses' (case-insensitive)."""
    try:
        data = json.loads(resp_body)
        return str(data.get('status', '')).lower() == 'sukses'
    except Exception:
        # Fallback: cek plain text
        return 'sukses' in resp_body.lower()


def send_wa_otp(phone: str, otp_code: str, user_id: int, user_type: str) -> bool:
    contact = normalize_contact(phone)
    status  = 'failed'
    error   = None
    cost    = 0

    if not contact:
        error = f'Nomor tidak valid setelah normalisasi: {phone!r}'
        current_app.logger.warning('[WA] %s', error)
        _log(user_id, user_type, phone or '', status, cost, error)
        return False

    payload = {
        'key':     WA_KEY,
        'contact': contact,
        'code':    str(otp_code),
    }
    headers = {'Content-Type': 'application/json'}

    try:
        # Step 1: POST awal, jangan ikuti redirect otomatis
        resp = _requests.post(
            WA_GATEWAY_URL,
            json=payload,
            headers=headers,
            timeout=15,
            allow_redirects=False,
        )

        current_app.logger.info(
            '[WA] step1 status=%s contact=%s location=%s',
            resp.status_code, contact,
            resp.headers.get('Location', '-')
        )

        # Step 2: Jika GAS balas 3xx, ikuti redirect dengan POST
        if resp.status_code in (301, 302, 303, 307, 308):
            redirect_url = resp.headers.get('Location')
            if redirect_url:
                resp = _requests.post(
                    redirect_url,
                    json=payload,
                    headers=headers,
                    timeout=15,
                    allow_redirects=False,
                )
                current_app.logger.info(
                    '[WA] step2 (after redirect) status=%s contact=%s',
                    resp.status_code, contact
                )

        body = resp.text
        current_app.logger.info(
            '[WA] FINAL status=%s contact=%s body=%s',
            resp.status_code, contact, body[:500]
        )

        if resp.status_code == 200 and _is_success(body):
            status = 'sent'
            cost   = WA_COST
            return True
        else:
            error = f'HTTP {resp.status_code}: {body[:200]}'
            return False

    except Exception as e:
        error = str(e)
        current_app.logger.error('[WA] send_wa_otp error to %s: %s', contact, e)
        return False

    finally:
        _log(user_id, user_type, contact, status, cost, error)


def _log(user_id: int, user_type: str, contact: str, status: str, cost: int, error):
    try:
        db.session.execute(
            db.text(
                "INSERT INTO t_log_wa_dtsen "
                "(user_id, user_type, contact, status, cost, error_msg) "
                "VALUES (:uid, :ut, :ct, :st, :cost, :err)"
            ),
            {'uid': user_id, 'ut': user_type, 'ct': contact,
             'st': status, 'cost': cost, 'err': error}
        )
        db.session.commit()
    except Exception as db_err:
        current_app.logger.error('[WA] log insert error: %s', db_err)
        db.session.rollback()
