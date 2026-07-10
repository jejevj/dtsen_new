import hashlib
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy import or_
from ..models.tuser import TUser
from ..models.t_dtsen_akses import TDtsenAkses
from ..extensions import db


def md5(plain: str) -> str:
    """Hash plaintext password dengan MD5."""
    return hashlib.md5(plain.encode('utf-8')).hexdigest()


def _make_identity(user_type: str, user_id: int) -> dict:
    """Bungkus identity JWT agar bisa dibedakan tipe user-nya."""
    return {'type': user_type, 'id': user_id}


class AuthService:

    # ------------------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------------------
    @staticmethod
    def login(identifier: str, password: str) -> dict:
        """
        Login fleksibel: cari identifier (email / notelp) di tuser dulu,
        lalu di t_dtsen_akses. Password di-hash MD5 sebelum dibandingkan.
        """
        if not identifier or not password:
            return {'message': 'Identifier dan password wajib diisi.', 'status_code': 400}

        hashed = md5(password)

        # --- 1. Coba tuser (user internal SIMZAT) ---
        tuser = TUser.query.filter(
            or_(
                TUser.email  == identifier,
                TUser.notelp == identifier,
            )
        ).first()

        if tuser:
            if tuser.is_expired == 'Y':
                return {'message': 'Akun sudah kadaluarsa.', 'status_code': 403}
            if tuser.approve != 1:
                return {'message': 'Akun belum disetujui.', 'status_code': 403}
            if tuser.user_password != hashed:
                return {'message': 'Email/No. HP atau password salah.', 'status_code': 401}

            identity      = _make_identity('tuser', tuser.iduser)
            access_token  = create_access_token(identity=identity)
            refresh_token = create_refresh_token(identity=identity)
            return {
                'access_token':  access_token,
                'refresh_token': refresh_token,
                'token_type':    'Bearer',
                'user': {
                    'id':             tuser.iduser,
                    'user_type':      'tuser',
                    'user_id':        tuser.user_id,
                    'user_fullname':  tuser.user_fullname,
                    'email':          tuser.email,
                    'notelp':         tuser.notelp,
                    'user_grup':      tuser.user_grup,
                    'list_office':    tuser.list_office,
                    'is_dtsen_user':  tuser.is_dtsen_user,
                    'is_soal_user':   tuser.is_soal_user,
                    'tipe_organisasi':tuser.tipe_organisasi,
                    'profpict':       tuser.profpict,
                },
            }

        # --- 2. Coba t_dtsen_akses (user eksternal DTSEN) ---
        dtsen = TDtsenAkses.query.filter(
            or_(
                TDtsenAkses.email  == identifier,
                TDtsenAkses.notelp == identifier,
            )
        ).first()

        if dtsen:
            if dtsen.deleted_at is not None:
                return {'message': 'Akun telah dihapus.', 'status_code': 403}
            if dtsen.statuses not in ('aktif',):
                return {
                    'message': f'Akun belum aktif (status: {dtsen.statuses}).',
                    'status_code': 403,
                }
            if dtsen.dtsen_akses_password != hashed:
                return {'message': 'Email/No. HP atau password salah.', 'status_code': 401}

            identity      = _make_identity('dtsen', dtsen.dtsen_akses_id)
            access_token  = create_access_token(identity=identity)
            refresh_token = create_refresh_token(identity=identity)
            return {
                'access_token':  access_token,
                'refresh_token': refresh_token,
                'token_type':    'Bearer',
                'user': {
                    'id':           dtsen.dtsen_akses_id,
                    'user_type':    'dtsen',
                    'nama_lengkap': dtsen.nama_lengkap,
                    'email':        dtsen.email,
                    'notelp':       dtsen.notelp,
                    'laz_kode':     dtsen.laz_kode,
                    'jabatan':      dtsen.jabatan,
                    'statuses':     dtsen.statuses,
                },
            }

        # --- Tidak ditemukan di mana pun ---
        return {'message': 'Email/No. HP atau password salah.', 'status_code': 401}

    # ------------------------------------------------------------------
    # GET CURRENT USER  (dipakai oleh /auth/me)
    # ------------------------------------------------------------------
    @staticmethod
    def get_current_user(identity: dict) -> dict:
        """
        Ambil profil user berdasarkan identity JWT.
        identity = {'type': 'tuser'|'dtsen', 'id': <int>}
        """
        user_type = identity.get('type')
        user_id   = identity.get('id')

        if user_type == 'tuser':
            user = TUser.query.get(user_id)
            if not user:
                return {'message': 'User tidak ditemukan.', 'status_code': 404}
            return {
                'id':             user.iduser,
                'user_type':      'tuser',
                'user_id':        user.user_id,
                'user_fullname':  user.user_fullname,
                'email':          user.email,
                'notelp':         user.notelp,
                'user_grup':      user.user_grup,
                'list_office':    user.list_office,
                'is_dtsen_user':  user.is_dtsen_user,
                'is_soal_user':   user.is_soal_user,
                'tipe_organisasi':user.tipe_organisasi,
                'profpict':       user.profpict,
                'is_expired':     user.is_expired,
            }

        if user_type == 'dtsen':
            user = TDtsenAkses.query.get(user_id)
            if not user:
                return {'message': 'User tidak ditemukan.', 'status_code': 404}
            return {
                'id':           user.dtsen_akses_id,
                'user_type':    'dtsen',
                'nama_lengkap': user.nama_lengkap,
                'nik':          user.nik,
                'email':        user.email,
                'notelp':       user.notelp,
                'laz_kode':     user.laz_kode,
                'jabatan':      user.jabatan,
                'statuses':     user.statuses,
                'activated_at': user.activated_at.isoformat() if user.activated_at else None,
            }

        return {'message': 'Tipe user tidak dikenali.', 'status_code': 400}
