"""
WhatsApp OTP Service via Google Apps Script gateway.
Google Apps Script (GAS) mengeluarkan redirect 302 saat POST —
gunakan `requests` dengan allow_redirects=True agar tetap POST setelah redirect.
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
WA_COST = 650  # Rp per hit


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


def send_wa_otp(phone: str, otp_code: str, user_id: int, user_type: str) -> bool:
    contact = normalize_contact(phone)
    status  = 'failed'
    error   = None

    if not contact:
        error = f'Nomor tidak valid setelah normalisasi: {phone!r}'
        current_app.logger.warning(f'[WA] {error}')
        _log(user_id, user_type, phone or '', status, error)
        return False

    payload = {
        'key':     WA_KEY,
        'contact': contact,
        'code':    str(otp_code),
    }

    try:
        # GAS redirect 302 POST → POST (bukan GET)
        # requests secara default ubah POST redirect jadi GET —
        # pakai session + event hook untuk paksa tetap POST
        session = _requests.Session()

        def force_post_on_redirect(r, *args, **kwargs):
            if r.is_redirect:
                redirected = _requests.Request(
                    method='POST',
                    url=r.headers['Location'],
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                )
                prep = session.prepare_request(redirected)
                return session.send(prep, timeout=15, allow_redirects=False)

        resp = session.post(
            WA_GATEWAY_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=15,
            allow_redirects=True,
            hooks={'response': force_post_on_redirect},
        )

        body = resp.text[:300]
        current_app.logger.info(
            f'[WA] gateway status={resp.status_code} contact={contact} body={body}'
        )

        # GAS sukses biasanya return 200 dengan JSON {"status":"ok"} atau plain text
        if resp.status_code == 200:
            status = 'sent'
            return True
        else:
            error = f'HTTP {resp.status_code}: {body}'
            return False

    except Exception as e:
        error = str(e)
        current_app.logger.error(f'[WA] send_wa_otp error to {contact}: {e}')
        return False

    finally:
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
             'st': status, 'cost': WA_COST if status == 'sent' else 0, 'err': error}
        )
        db.session.commit()
    except Exception as db_err:
        current_app.logger.error(f'[WA] log insert error: {db_err}')
        db.session.rollback()
