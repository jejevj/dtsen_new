import hashlib
from datetime import date
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy import or_
from ..models.t_dtsen_akses import TDtsenAkses
from ..models.laz import Laz
from ..models.m_uker import MUker


def md5(plain: str) -> str:
    return hashlib.md5(plain.encode('utf-8')).hexdigest()


def build_identity_str(user: TDtsenAkses) -> str:
    """
    JWT subject HARUS string (Flask-JWT-Extended v4+).
    Format: "dtsen:456"
    """
    return f"dtsen:{user.dtsen_akses_id}"


def parse_identity_str(identity: str) -> dict:
    """
    Parse string identity kembali ke dict {'type': ..., 'id': ...}.
    """
    try:
        user_type, uid = identity.split(':', 1)
        return {'type': user_type, 'id': int(uid)}
    except Exception:
        return {'type': None, 'id': None}


def _resolve_laz_nama(laz_kode: str) -> str | None:
    """Cari laz_nama dari t_laz, fallback ke m_uker.uker_nama."""
    if not laz_kode:
        return None
    laz = Laz.query.filter_by(laz_kode=laz_kode).first()
    if laz:
        return laz.laz_nama
    uker = MUker.query.filter_by(uker_kode=laz_kode).first()
    if uker:
        return uker.uker_nama
    return None


def _check_laz_status(laz_kode: str) -> dict | None:
    """
    Khusus akun_types='laz': pastikan laz_status di t_laz adalah 'aktif'.
    Return dict error jika gagal, None jika lolos.
    """
    if not laz_kode:
        return {'message': 'laz_kode tidak ditemukan pada akun LAZ.', 'status_code': 403}

    laz = Laz.query.filter_by(laz_kode=laz_kode).first()
    if not laz:
        return {'message': 'Data LAZ tidak ditemukan.', 'status_code': 403}

    if laz.laz_status == 'daftar_ulang':
        return {
            'message': f'LAZ {laz.laz_nama} Dalam Proses Daftar Ulang, tidak dapat login saat ini.',
            'status_code': 403,
            'error_code': 'LAZ_DAFTAR_ULANG',
        }

    if laz.laz_status != 'aktif':
        return {
            'message': f'LAZ {laz.laz_nama} tidak aktif (status: {laz.laz_status}). Silakan hubungi administrator.',
            'status_code': 403,
            'error_code': 'LAZ_NOT_ACTIVE',
        }

    return None


class AuthService:

    @staticmethod
    def login(identifier: str, password: str) -> dict:
        # ── 1. Validasi input ────────────────────────────────────────────────
        if not identifier or not password:
            return {'message': 'Identifier dan password wajib diisi.', 'status_code': 400}

        hashed = md5(password)

        # ── 2. Cari user di t_dtsen_akses ────────────────────────────────────
        dtsen = TDtsenAkses.query.filter(
            or_(TDtsenAkses.email == identifier, TDtsenAkses.notelp == identifier)
        ).first()

        if not dtsen:
            return {
                'message': 'Email/Nomor HP dan Password Tidak Valid.',
                'status_code': 404,
                'error_code': 'ACCOUNT_NOT_FOUND',
            }

        # ── 3. Cek soft-delete ───────────────────────────────────────────────
        if dtsen.deleted_at is not None:
            return {'message': 'Akun telah dihapus.', 'status_code': 403}

        # ── 4. Cek statuses harus 'aktif' ────────────────────────────────────
        if dtsen.statuses != 'aktif':
            return {
                'message': f'Akun belum aktif (status: {dtsen.statuses}).',
                'status_code': 403,
                'error_code': 'ACCOUNT_NOT_ACTIVE',
            }

        # ── 5. Cek masa berlaku akun (valid_from_at & valid_end_at) ──────────
        today = date.today()
        if dtsen.valid_from_at and today < dtsen.valid_from_at:
            return {
                'message': 'Akun belum berlaku. Akses dimulai pada '
                           f'{dtsen.valid_from_at.strftime("%d %B %Y")}.',
                'status_code': 403,
                'error_code': 'ACCOUNT_NOT_YET_VALID',
            }
        if dtsen.valid_end_at and today > dtsen.valid_end_at:
            return {
                'message': 'Masa akses akun Anda telah berakhir sejak '
                           f'{dtsen.valid_end_at.strftime("%d %B %Y")}.',
                'status_code': 403,
                'error_code': 'ACCOUNT_EXPIRED',
            }

        # ── 6. Validasi berdasarkan akun_types ───────────────────────────────
        akun_type = (dtsen.akun_types or '').strip().lower()

        if akun_type == 'laz':
            # Cek status LAZ di t_laz — harus aktif, dan cek SEBELUM password
            laz_err = _check_laz_status(dtsen.laz_kode)
            if laz_err:
                return laz_err

        elif akun_type == 'baznas':
            # Tidak perlu cek laz_status, tapi laz_kode boleh ada/tidak
            pass

        elif akun_type in ('internal', 'external'):
            # laz_kode harus null/kosong
            if dtsen.laz_kode and dtsen.laz_kode.strip():
                return {
                    'message': 'Konfigurasi akun tidak valid (internal/external tidak boleh memiliki laz_kode).',
                    'status_code': 403,
                    'error_code': 'INVALID_ACCOUNT_CONFIG',
                }
        else:
            return {
                'message': f'Tipe akun tidak dikenali: {akun_type}.',
                'status_code': 403,
                'error_code': 'UNKNOWN_ACCOUNT_TYPE',
            }

        # ── 7. Verifikasi password ───────────────────────────────────────────
        if dtsen.dtsen_akses_password != hashed:
            return {'message': 'Email/Nomor HP dan Password Tidak Valid.', 'status_code': 401}

        # ── 8. Semua lolos → buat token ──────────────────────────────────────
        identity_str  = build_identity_str(dtsen)
        access_token  = create_access_token(identity=identity_str)
        refresh_token = create_refresh_token(identity=identity_str)

        return {
            'access_token':  access_token,
            'refresh_token': refresh_token,
            'token_type':    'Bearer',
            'user':          AuthService._dtsen_payload(dtsen),
        }

    @staticmethod
    def get_current_user(identity) -> dict:
        """
        Menerima identity berupa string 'type:id' atau dict {'type':..,'id':..}.
        """
        if isinstance(identity, str):
            identity = parse_identity_str(identity)

        user_type = identity.get('type')
        user_id   = identity.get('id')

        if user_type == 'dtsen':
            user = TDtsenAkses.query.get(user_id)
            if not user:
                return {'message': 'User tidak ditemukan.', 'status_code': 404}
            return {'user': AuthService._dtsen_payload(user)}

        return {'message': 'Tipe user tidak dikenali.', 'status_code': 400}

    @staticmethod
    def _dtsen_payload(u: TDtsenAkses) -> dict:
        laz_nama = None

        akun_type = (u.akun_types or '').strip().lower()

        if akun_type == 'laz' and u.laz_kode:
            laz = Laz.query.filter_by(laz_kode=u.laz_kode).first()
            if laz:
                laz_nama = laz.laz_nama

        elif akun_type == 'baznas' and u.laz_kode:
            # Coba t_laz dulu, fallback ke m_uker
            laz_nama = _resolve_laz_nama(u.laz_kode)

        return {
            'id':             u.dtsen_akses_id,
            'user_type':      'dtsen',
            'akun_types':     u.akun_types,
            'nama_lengkap':   u.nama_lengkap,
            'nik':            u.nik,
            'email':          u.email,
            'notelp':         u.notelp,
            'laz_kode':       u.laz_kode,
            'laz_nama':       laz_nama,
            'jabatan':        u.jabatan,
            'instansi':       u.instansi,
            'statuses':       u.statuses,
            'valid_from_at':  u.valid_from_at.isoformat() if u.valid_from_at else None,
            'valid_end_at':   u.valid_end_at.isoformat() if u.valid_end_at else None,
            'activated_at':   u.activated_at.isoformat() if u.activated_at else None,
        }
