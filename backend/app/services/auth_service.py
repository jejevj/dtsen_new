import hashlib
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy import or_
from ..models.tuser import TUser
from ..models.t_dtsen_akses import TDtsenAkses
from ..models.laz import Laz


def md5(plain: str) -> str:
    return hashlib.md5(plain.encode('utf-8')).hexdigest()


def build_identity_str(user) -> str:
    """
    JWT subject HARUS string (Flask-JWT-Extended v4+).
    Format: "tuser:123" atau "dtsen:456"
    """
    uid = user.iduser if user.user_type == 'tuser' else user.dtsen_akses_id
    return f"{user.user_type}:{uid}"


def parse_identity_str(identity: str) -> dict:
    """
    Parse string identity kembali ke dict {'type': ..., 'id': ...}.
    Kompatibel dengan kode lama yang pakai dict identity.
    """
    try:
        user_type, uid = identity.split(':', 1)
        return {'type': user_type, 'id': int(uid)}
    except Exception:
        return {'type': None, 'id': None}


class AuthService:

    @staticmethod
    def login(identifier: str, password: str) -> dict:
        if not identifier or not password:
            return {'message': 'Identifier dan password wajib diisi.', 'status_code': 400}

        hashed = md5(password)

        # --- Cari di tuser ---
        tuser = TUser.query.filter(
            or_(TUser.email == identifier, TUser.notelp == identifier)
        ).first()

        if tuser:
            is_dtsen = (tuser.is_dtsen_user or '').strip().upper()
            if is_dtsen != 'Y':
                return {
                    'message': 'Akun Anda tidak memiliki akses ke aplikasi DTSEN.',
                    'status_code': 403,
                    'error_code': 'DTSEN_ACCESS_DENIED',
                }
            if tuser.is_expired == 'Y':
                return {'message': 'Akun sudah kadaluarsa.', 'status_code': 403}
            if tuser.approve != 1:
                return {'message': 'Akun belum disetujui.', 'status_code': 403}
            if tuser.user_password != hashed:
                return {'message': 'Email/No. HP atau password salah.', 'status_code': 401}

            identity_str  = build_identity_str(tuser)
            access_token  = create_access_token(identity=identity_str)
            refresh_token = create_refresh_token(identity=identity_str)
            return {
                'access_token':  access_token,
                'refresh_token': refresh_token,
                'token_type':    'Bearer',
                'user':          AuthService._tuser_payload(tuser),
            }

        # --- Cari di t_dtsen_akses ---
        dtsen = TDtsenAkses.query.filter(
            or_(TDtsenAkses.email == identifier, TDtsenAkses.notelp == identifier)
        ).first()

        if dtsen:
            if dtsen.deleted_at is not None:
                return {'message': 'Akun telah dihapus.', 'status_code': 403}
            if dtsen.statuses != 'aktif':
                return {
                    'message': f'Akun belum aktif (status: {dtsen.statuses}).',
                    'status_code': 403,
                }
            if dtsen.dtsen_akses_password != hashed:
                return {'message': 'Email/No. HP atau password salah.', 'status_code': 401}

            identity_str  = build_identity_str(dtsen)
            access_token  = create_access_token(identity=identity_str)
            refresh_token = create_refresh_token(identity=identity_str)
            return {
                'access_token':  access_token,
                'refresh_token': refresh_token,
                'token_type':    'Bearer',
                'user':          AuthService._dtsen_payload(dtsen),
            }

        return {
            'message': 'Akun dengan email/nomor HP tersebut tidak ditemukan.',
            'status_code': 404,
            'error_code': 'ACCOUNT_NOT_FOUND',
        }

    @staticmethod
    def get_current_user(identity) -> dict:
        """
        Menerima identity berupa string '"type:id"' (format baru)
        atau dict {'type':..,'id':..} (format lama, auto-convert).
        """
        if isinstance(identity, str):
            identity = parse_identity_str(identity)

        user_type = identity.get('type')
        user_id   = identity.get('id')

        if user_type == 'tuser':
            user = TUser.query.get(user_id)
            if not user:
                return {'message': 'User tidak ditemukan.', 'status_code': 404}
            return {'user': AuthService._tuser_payload(user)}

        if user_type == 'dtsen':
            user = TDtsenAkses.query.get(user_id)
            if not user:
                return {'message': 'User tidak ditemukan.', 'status_code': 404}
            return {'user': AuthService._dtsen_payload(user)}

        return {'message': 'Tipe user tidak dikenali.', 'status_code': 400}

    @staticmethod
    def _tuser_payload(u: TUser) -> dict:
        return {
            'id':            u.iduser,
            'user_type':     'tuser',
            'user_id':       u.user_id,
            'user_fullname': u.user_fullname,
            'email':         u.email,
            'notelp':        u.notelp,
            'user_grup':     u.user_grup,
            'list_office':   u.list_office,
            'profpict':      u.profpict,
            'is_subscribe':  u.is_subscribe,
            'is_expired':    u.is_expired,
            'is_dtsen_user': u.is_dtsen_user,
        }

    @staticmethod
    def _dtsen_payload(u: TDtsenAkses) -> dict:
        # Join ke t_laz untuk ambil laz_nama berdasarkan laz_kode
        laz_nama = None
        if u.laz_kode:
            laz = Laz.query.filter_by(laz_kode=u.laz_kode).first()
            if laz:
                laz_nama = laz.laz_nama

        return {
            'id':           u.dtsen_akses_id,
            'user_type':    'dtsen',
            'nama_lengkap': u.nama_lengkap,
            'nik':          u.nik,
            'email':        u.email,
            'notelp':       u.notelp,
            'laz_kode':     u.laz_kode,
            'laz_nama':     laz_nama,
            'jabatan':      u.jabatan,
            'statuses':     u.statuses,
            'activated_at': u.activated_at.isoformat() if u.activated_at else None,
        }
