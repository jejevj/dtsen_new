# Backend — Flask REST API

## Stack
- Python 3.11+
- Flask 3.x
- Flask-SQLAlchemy (ORM)
- Flask-Migrate (database migrations)
- Flask-JWT-Extended (autentikasi JWT)
- Flask-CORS (cross-origin)
- Marshmallow (serialisasi/validasi)
- Flasgger (Swagger/OpenAPI docs)

## Struktur

```
backend/
├── app/
│   ├── __init__.py          # App factory (create_app)
│   ├── extensions.py        # Inisialisasi ekstensi (db, jwt, migrate)
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── laz.py
│   │   ├── mustahik.py
│   │   ├── program.py
│   │   └── wilayah.py
│   ├── api/                 # Blueprint API
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py      # Login, logout, refresh token
│   │   │   ├── mustahik.py  # CRUD + filter mustahik
│   │   │   ├── laz.py       # Data LAZ
│   │   │   ├── report.py    # Agregat & laporan
│   │   │   ├── home.py      # Dashboard summary
│   │   │   └── wilayah.py   # Master provinsi, kab, kec, kel
│   ├── schemas/             # Marshmallow schemas
│   │   ├── __init__.py
│   │   ├── mustahik.py
│   │   ├── laz.py
│   │   └── user.py
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   ├── mustahik_service.py
│   │   ├── report_service.py
│   │   └── auth_service.py
│   └── utils/               # Helper functions
│       ├── __init__.py
│       ├── pagination.py
│       └── response.py      # Standar format response JSON
├── migrations/              # Flask-Migrate files
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_mustahik.py
│   └── test_report.py
├── .env.example
├── .gitignore
├── config.py                # Config: Development, Production, Testing
├── requirements.txt
├── requirements-dev.txt
└── wsgi.py                  # Entry point produksi (Gunicorn)
```
