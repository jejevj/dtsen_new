from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash
from sqlalchemy import or_
from ..models.user import User
from ..extensions import db


class AuthService:
    @staticmethod
    def login(identifier: str, password: str) -> dict:
        """Login via email, username, atau NIP."""
        if not identifier or not password:
            return {'message': 'Identifier dan password wajib diisi.', 'status_code': 400}

        user = User.query.filter(
            or_(
                User.email    == identifier,
                User.username == identifier,
                User.nip      == identifier,
            )
        ).first()

        if not user or not check_password_hash(user.password, password):
            return {'message': 'Username/NIP/Email atau password salah.', 'status_code': 401}

        access_token  = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            'access_token':  access_token,
            'refresh_token': refresh_token,
            'user': {
                'id':       user.id,
                'name':     user.name,
                'email':    user.email,
                'username': user.username,
                'nip':      user.nip,
                'role':     user.role,
            }
        }

    @staticmethod
    def get_user(user_id: int) -> dict:
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User tidak ditemukan.', 'status_code': 404}
        return {
            'id':       user.id,
            'name':     user.name,
            'email':    user.email,
            'username': user.username,
            'nip':      user.nip,
            'role':     user.role,
        }
