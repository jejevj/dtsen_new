# DTSEN New

**DTSEN** (Data Tunggal Sosial Ekonomi Nasional) — Sistem Informasi Zakat dan Wakaf

Proyek ini menggunakan arsitektur **decoupled (API-first)**:
- **Backend**: Flask (Python) — REST API
- **Frontend**: Vue.js 3 + Vite — Single Page Application (SPA)

---

## Struktur Proyek

```
dtsen_new/
├── backend/     # Flask REST API
└── frontend/    # Vue.js 3 SPA
```

## Cara Menjalankan

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
flask db upgrade
flask run
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## API Documentation
Setelah backend berjalan, akses: `http://localhost:5000/api/docs`
