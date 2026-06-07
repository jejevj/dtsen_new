from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash
from ..models.user import User


class AuthService:
    @staticmethod
    def login(email: str, password: str) -> dict:
        if not email or not password:
            return {'message': 'Email dan password wajib diisi.', 'status_code': 400}

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return {'message': 'Email atau password salah.', 'status_code': 401}

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {'id': user.id, 'name': user.name, 'email': user.email}
        }

    @staticmethod
    def get_user(user_id: int) -> dict:
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User tidak ditemukan.', 'status_code': 404}
        return {'id': user.id, 'name': user.name, 'email': user.email}
