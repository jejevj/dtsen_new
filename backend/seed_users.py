"""Seed demo users untuk DTSEN — 3 level Penanggung Jawab.

Hierarki:
  pj_nasional  -> di-assign ke 10 provinsi
  pj_provinsi  -> di-assign ke 4 kab/kota dalam 1 provinsi
  pj_kabkota   -> di-assign ke 1 kab/kota

Aturan laporan:
  - pj_nasional : hanya bisa lihat data dari 10 provinsi yang di-assign
  - pj_provinsi : hanya bisa lihat data dari 4 kab/kota yang di-assign
  - pj_kabkota  : hanya bisa lihat data dari 1 kab/kota yang di-assign
  - Semua level  : bisa memeriksa semua NIK pada pemeriksaan dtsen

Usage:
    cd backend
    python seed_users.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models.user import User, UserWilayah
from app.models.wilayah import Provinsi, KabKota

# ---------------------------------------------------------------------------
# Master wilayah dummy (kode mengikuti format Kemendagri)
# ---------------------------------------------------------------------------
PROVINSI_SEED = [
    ('11', 'Aceh'),
    ('12', 'Sumatera Utara'),
    ('13', 'Sumatera Barat'),
    ('14', 'Riau'),
    ('15', 'Jambi'),
    ('16', 'Sumatera Selatan'),
    ('17', 'Bengkulu'),
    ('18', 'Lampung'),
    ('19', 'Kepulauan Bangka Belitung'),
    ('21', 'Kepulauan Riau'),
    # Provinsi referensi untuk pj_provinsi
    ('31', 'DKI Jakarta'),
    ('32', 'Jawa Barat'),
    ('33', 'Jawa Tengah'),
    ('34', 'DI Yogyakarta'),
]

# Kab/kota yang berada di DKI Jakarta (31) — untuk pj_provinsi
KABKOTA_DKI = [
    ('3171', 'Kota Jakarta Selatan', '31'),
    ('3172', 'Kota Jakarta Timur',   '31'),
    ('3173', 'Kota Jakarta Pusat',   '31'),
    ('3174', 'Kota Jakarta Barat',   '31'),
]

# Kab/kota untuk pj_kabkota (Kota Bogor — Jawa Barat)
KABKOTA_JABAR_SAMPLE = [
    ('3271', 'Kota Bogor',    '32'),
    ('3272', 'Kota Sukabumi', '32'),
    ('3273', 'Kota Bandung',  '32'),
    ('3274', 'Kota Cirebon',  '32'),
]

# ---------------------------------------------------------------------------
# Definisi user demo
# ---------------------------------------------------------------------------
DEMO_USERS = [
    # ----- Admin (akses penuh) -----
    {
        'name':     'Administrator DTSEN',
        'username': 'admin',
        'nip':      '199001012020011001',
        'email':    'admin@dtsen.go.id',
        'password': 'Dtsen@2026!',
        'role':     'admin',
        # Admin tidak butuh assignment wilayah
        'provinsi': [],
        'kabkota':  [],
    },
    # ----- Penanggung Jawab Nasional -----
    {
        'name':     'PJ Nasional - Wilayah Barat',
        'username': 'pj_nasional',
        'nip':      '198501012019011001',
        'email':    'pj.nasional@dtsen.go.id',
        'password': 'Dtsen@2026!',
        'role':     'pj_nasional',
        # Di-assign ke 10 provinsi (Sumatera)
        'provinsi': ['11','12','13','14','15','16','17','18','19','21'],
        'kabkota':  [],  # pj_nasional tidak di-assign per kab/kota
    },
    # ----- Penanggung Jawab Provinsi (DKI Jakarta) -----
    {
        'name':     'PJ Provinsi - DKI Jakarta',
        'username': 'pj_provinsi_dki',
        'nip':      '199001012019011002',
        'email':    'pj.provinsi.dki@dtsen.go.id',
        'password': 'Dtsen@2026!',
        'role':     'pj_provinsi',
        'provinsi': ['31'],  # induk provinsinya
        # Di-assign ke 4 kab/kota dalam DKI Jakarta
        'kabkota':  ['3171','3172','3173','3174'],
    },
    # ----- Penanggung Jawab Kab/Kota (Kota Bogor) -----
    {
        'name':     'PJ Kab/Kota - Kota Bogor',
        'username': 'pj_kabkota_bogor',
        'nip':      '199201012020011003',
        'email':    'pj.kabkota.bogor@dtsen.go.id',
        'password': 'Dtsen@2026!',
        'role':     'pj_kabkota',
        'provinsi': ['32'],  # induk provinsi Jawa Barat
        'kabkota':  ['3271'],  # hanya Kota Bogor
    },
]


def seed_wilayah(app):
    """Seed data wilayah dummy jika belum ada."""
    with app.app_context():
        # Provinsi
        for kode, nama in PROVINSI_SEED:
            if not Provinsi.query.get(kode):
                db.session.add(Provinsi(provinsi_kode=kode, provinsi_nama=nama))
                print(f'  [WILAYAH] + Provinsi {kode} - {nama}')
        db.session.commit()

        # Kab/Kota DKI
        for kode, nama, prov in KABKOTA_DKI:
            if not KabKota.query.get(kode):
                db.session.add(KabKota(kabkota_kode=kode, kabkota_nama=nama, provinsi_kode=prov))
                print(f'  [WILAYAH] + KabKota {kode} - {nama}')

        # Kab/Kota Jabar sample
        for kode, nama, prov in KABKOTA_JABAR_SAMPLE:
            if not KabKota.query.get(kode):
                db.session.add(KabKota(kabkota_kode=kode, kabkota_nama=nama, provinsi_kode=prov))
                print(f'  [WILAYAH] + KabKota {kode} - {nama}')

        db.session.commit()
        print('  Seed wilayah selesai.')


def seed_users(app):
    """Seed demo users dan assignment wilayah."""
    with app.app_context():
        for u in DEMO_USERS:
            user = User.query.filter_by(email=u['email']).first()
            if not user:
                user = User(
                    name     = u['name'],
                    username = u['username'],
                    nip      = u['nip'],
                    email    = u['email'],
                    password = generate_password_hash(u['password']),
                    role     = u['role'],
                )
                db.session.add(user)
                db.session.flush()  # dapat user.id sebelum commit
                print(f'  [USER] + {u["email"]} ({u["role"]})')
            else:
                print(f'  [SKIP] {u["email"]} sudah ada.')

            # Hapus assignment lama agar idempotent
            UserWilayah.query.filter_by(user_id=user.id).delete()

            # Assign provinsi saja (untuk pj_nasional)
            if u['role'] == 'pj_nasional':
                for prov_kode in u['provinsi']:
                    db.session.add(UserWilayah(user_id=user.id, provinsi_kode=prov_kode, kabkota_kode=None))

            # Assign provinsi + kab/kota (untuk pj_provinsi & pj_kabkota)
            elif u['role'] in ('pj_provinsi', 'pj_kabkota'):
                prov_kode = u['provinsi'][0] if u['provinsi'] else None
                for kab_kode in u['kabkota']:
                    db.session.add(UserWilayah(user_id=user.id, provinsi_kode=prov_kode, kabkota_kode=kab_kode))

        db.session.commit()
        print('  Seed user selesai.')


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

    print('\n=== Seed Wilayah ===')
    seed_wilayah(app)

    print('\n=== Seed Users ===')
    seed_users(app)

    print('\n=== Ringkasan Kredensial Demo ===')
    print(f'{"Role":<20} {"Username":<22} {"Email":<35} Password')
    print('-' * 95)
    for u in DEMO_USERS:
        print(f'{u["role"]:<20} {u["username"]:<22} {u["email"]:<35} {u["password"]}')
    print()
    print('Aturan akses laporan:')
    print('  pj_nasional  -> laporan 10 provinsi yang di-assign (Sumatera)')
    print('  pj_provinsi  -> laporan 4 kab/kota DKI Jakarta yang di-assign')
    print('  pj_kabkota   -> laporan Kota Bogor saja')
    print('  Semua level  -> bisa memeriksa NIK manapun (pemeriksaan dtsen)')


if __name__ == '__main__':
    seed()
