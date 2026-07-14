"""Seed demo users untuk DTSEN — 3 level Penanggung Jawab.

Hierarki wilayah acuan: JAWA BARAT (32)
  Provinsi   : Jawa Barat (32) — satu dari 10 yang di-assign ke pj_nasional
  Kab/Kota   : 4 kab/kota di Jawa Barat — di-assign ke pj_provinsi
  Kab/Kota   : Kota Bandung (3273) saja — di-assign ke pj_kabkota

Rantai yang jelas:
  pj_nasional
    └─ mengawasi 10 provinsi, salah satunya Jawa Barat (32)
         └─ pj_provinsi_jabar
              └─ mengawasi 4 kab/kota di Jawa Barat:
                   3271 Kota Bogor
                   3272 Kota Sukabumi
                   3273 Kota Bandung  ← dijaga oleh pj_kabkota_bandung
                   3274 Kota Cirebon
                        └─ pj_kabkota_bandung
                             └─ hanya Kota Bandung (3273)

Aturan akses laporan:
  pj_nasional      → data dari 10 provinsi yang di-assign
  pj_provinsi_jabar → data dari 4 kab/kota Jawa Barat yang di-assign
  pj_kabkota_bandung → data Kota Bandung saja
  Semua level       → bisa memeriksa semua NIK pada pemeriksaan dtsen

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
# Master wilayah — satu pohon hierarki berpusat di Jawa Barat
# ---------------------------------------------------------------------------

# 10 Provinsi yang di-assign ke pj_nasional
# Jawa Barat (32) masuk di sini agar rantai terhubung
PROVINSI_SEED = [
    ('31', 'DKI Jakarta'),
    ('32', 'Jawa Barat'),          # <-- provinsi acuan hierarki
    ('33', 'Jawa Tengah'),
    ('34', 'DI Yogyakarta'),
    ('35', 'Jawa Timur'),
    ('36', 'Banten'),
    ('51', 'Bali'),
    ('52', 'Nusa Tenggara Barat'),
    ('53', 'Nusa Tenggara Timur'),
    ('61', 'Kalimantan Barat'),
]

# 4 Kab/Kota di Jawa Barat — semua milik provinsi 32
KABKOTA_JABAR = [
    ('3271', 'Kota Bogor',    '32'),
    ('3272', 'Kota Sukabumi', '32'),
    ('3273', 'Kota Bandung',  '32'),   # <-- kab/kota acuan pj_kabkota
    ('3274', 'Kota Cirebon',  '32'),
]

# ---------------------------------------------------------------------------
# Definisi user demo
# ---------------------------------------------------------------------------
DEMO_USERS = [
    # ----- Admin (akses penuh, tidak perlu assignment wilayah) -----
    {
        'name':     'Administrator DTSEN',
        'username': 'admin',
        'nip':      '199001012020011001',
        'email':    'admin@dtsen.go.id',
        'password': 'Dtsen@2026!',
        'role':     'admin',
        'provinsi': [],
        'kabkota':  [],
    },

    # ----- Penanggung Jawab Nasional -----
    # Mengawasi 10 provinsi termasuk Jawa Barat (32)
    {
        'name':     'PJ Nasional - Wilayah Jawa & Bali',
        'username': 'pj_nasional',
        'nip':      '198501012019011001',
        'email':    'pj.nasional@dtsen.go.id',
        'password': 'Dtsen@2026!',
        'role':     'pj_nasional',
        'provinsi': ['31','32','33','34','35','36','51','52','53','61'],
        'kabkota':  [],
    },

    # ----- Penanggung Jawab Provinsi — Jawa Barat -----
    # Di-assign ke 4 kab/kota dalam Jawa Barat, berada di bawah pj_nasional
    {
        'name':     'PJ Provinsi - Jawa Barat',
        'username': 'pj_provinsi_jabar',
        'nip':      '199001012019011002',
        'email':    'pj.provinsi.jabar@dtsen.go.id',
        'password': 'Dtsen@2026!',
        'role':     'pj_provinsi',
        'provinsi': ['32'],
        'kabkota':  ['3271', '3272', '3273', '3274'],
    },

    # ----- Penanggung Jawab Kab/Kota — Kota Bandung -----
    # Hanya mengawasi Kota Bandung (3273), berada di bawah pj_provinsi_jabar
    {
        'name':     'PJ Kab/Kota - Kota Bandung',
        'username': 'pj_kabkota_bandung',
        'nip':      '199201012020011003',
        'email':    'pj.kabkota.bandung@dtsen.go.id',
        'password': 'Dtsen@2026!',
        'role':     'pj_kabkota',
        'provinsi': ['32'],
        'kabkota':  ['3273'],
    },
]


def seed_wilayah(app):
    """Seed data wilayah dummy jika belum ada."""
    with app.app_context():
        for kode, nama in PROVINSI_SEED:
            if not Provinsi.query.get(kode):
                db.session.add(Provinsi(provinsi_kode=kode, provinsi_nama=nama))
                print(f'  [PROV]  + {kode} {nama}')
        db.session.commit()

        for kode, nama, prov in KABKOTA_JABAR:
            if not KabKota.query.get(kode):
                db.session.add(KabKota(kabkota_kode=kode, kabkota_nama=nama, provinsi_kode=prov))
                print(f'  [KAB]   + {kode} {nama} (Prov {prov})')
        db.session.commit()
        print('  Seed wilayah selesai.\n')


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
                db.session.flush()
                print(f'  [USER]  + {u["email"]} ({u["role"]})')
            else:
                # Update role jika berubah
                user.role = u['role']
                print(f'  [UPDATE] {u["email"]} ({u["role"]})')

            # Reset assignment wilayah agar idempotent
            UserWilayah.query.filter_by(user_id=user.id).delete()

            if u['role'] == 'pj_nasional':
                # Nasional: satu baris per provinsi, kabkota_kode NULL
                for prov_kode in u['provinsi']:
                    db.session.add(UserWilayah(
                        user_id       = user.id,
                        provinsi_kode = prov_kode,
                        kabkota_kode  = None,
                    ))
                print(f'           → assign {len(u["provinsi"])} provinsi')

            elif u['role'] in ('pj_provinsi', 'pj_kabkota'):
                # Provinsi / Kab-Kota: satu baris per kab/kota
                prov_kode = u['provinsi'][0] if u['provinsi'] else None
                for kab_kode in u['kabkota']:
                    db.session.add(UserWilayah(
                        user_id       = user.id,
                        provinsi_kode = prov_kode,
                        kabkota_kode  = kab_kode,
                    ))
                print(f'           → assign {len(u["kabkota"])} kab/kota di prov {prov_kode}')

        db.session.commit()
        print('  Seed user selesai.\n')


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

    print('=== Seed Wilayah ===')
    seed_wilayah(app)

    print('=== Seed Users ===')
    seed_users(app)

    print('=== Ringkasan Hierarki ===')
    print("""
  pj_nasional  (pj.nasional@dtsen.go.id)
  └─ 10 provinsi: 31 DKI, 32 Jabar*, 33 Jateng, 34 DIY, 35 Jatim,
                  36 Banten, 51 Bali, 52 NTB, 53 NTT, 61 Kalbar
       └─ pj_provinsi_jabar  (pj.provinsi.jabar@dtsen.go.id)
          └─ 4 kab/kota Jawa Barat:
               3271 Kota Bogor
               3272 Kota Sukabumi
               3273 Kota Bandung  *
               3274 Kota Cirebon
                    └─ pj_kabkota_bandung  (pj.kabkota.bandung@dtsen.go.id)
                       └─ hanya Kota Bandung (3273)

  admin  (admin@dtsen.go.id) — akses penuh, tidak terbatas wilayah
""")
    print('Password semua akun: Dtsen@2026!')
    print()
    print('Aturan akses laporan:')
    print('  pj_nasional       → data 10 provinsi yang di-assign')
    print('  pj_provinsi_jabar → data 4 kab/kota Jawa Barat yang di-assign')
    print('  pj_kabkota_bandung→ data Kota Bandung saja')
    print('  Semua level       → boleh memeriksa NIK manapun (pemeriksaan dtsen)')


if __name__ == '__main__':
    seed()
