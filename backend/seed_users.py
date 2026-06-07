"""Seed demo users for DTSEN.

Usage:
    cd backend
    python seed_users.py
"""
import os
from dotenv import load_dotenv

# Load .env sebelum import app
load_dotenv()

from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models.user import User

DEMO_USERS = [
    {
        'name':     'Administrator DTSEN',
        'username': 'admin',
        'nip':      '199001012020011001',
        'email':    'admin@dtsen.go.id',
        'password': 'Dtsen@2026!',
        'role':     'admin',
    },
    {
        'name':     'Operator Pusat',
        'username': 'operator',
        'nip':      '199501012021011002',
        'email':    'operator@dtsen.go.id',
        'password': 'Dtsen@2026!',
        'role':     'operator',
    },
    {
        'name':     'Analis Data',
        'username': 'analis',
        'nip':      '199801012022011003',
        'email':    'analis@dtsen.go.id',
        'password': 'Dtsen@2026!',
        'role':     'analis',
    },
]


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()
        for u in DEMO_USERS:
            exists = User.query.filter_by(email=u['email']).first()
            if exists:
                print(f'[SKIP] {u["email"]} sudah ada.')
                continue
            user = User(
                name=u['name'],
                username=u['username'],
                nip=u['nip'],
                email=u['email'],
                password=generate_password_hash(u['password']),
                role=u['role'],
            )
            db.session.add(user)
            print(f'[ADD]  {u["email"]} ({u["role"]})')
        db.session.commit()
        print('\nSeed selesai. Kredensial demo:')
        print('  admin    | username: admin    | NIP: 199001012020011001 | admin@dtsen.go.id    | Dtsen@2026!')
        print('  operator | username: operator | NIP: 199501012021011002 | operator@dtsen.go.id | Dtsen@2026!')
        print('  analis   | username: analis   | NIP: 199801012022011003 | analis@dtsen.go.id   | Dtsen@2026!')


if __name__ == '__main__':
    seed()
