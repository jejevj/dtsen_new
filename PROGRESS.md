# PROGRESS — DTSEN New Backend

> Terakhir diperbarui: 2026-07-10

---

## Status Flow Login & API Auth

### ✅ Selesai & Berjalan

| # | Item | Keterangan |
|---|------|------------|
| 1 | Model `TUser` — kolom `is_dtsen_user` | Kolom didefinisikan di model SQLAlchemy setelah sebelumnya ter-comment. DB production sudah di-`ALTER TABLE` untuk menambah kolom ini. |
| 2 | `AuthService.login` — validasi `is_dtsen_user` | User `tuser` yang `is_dtsen_user != 'Y'` ditolak dengan `403 DTSEN_ACCESS_DENIED` sebelum pengecekan password. |
| 3 | Login flow 3-step (password → OTP Email → OTP WA) | Seluruh step sudah terintegrasi dan berjalan. |
| 4 | Dual user type (`tuser` / `dtsen`) | Login mendukung dua tipe user dengan logika terpisah pada masing-masing step. |
| 5 | JWT `access_token` + `refresh_token` | Hanya diterbitkan setelah OTP WhatsApp berhasil diverifikasi (step 3). |

---

## Flow API Login (3 Step)

```
Client                          Backend (/api/v1/auth/...)
  │                                        │
  │── POST /auth/login ──────────────────► │
  │   { identifier, password }             │  1. Validasi identifier & password (MD5)
  │                                        │  2. Cek is_dtsen_user == 'Y' (khusus tuser)
  │                                        │  3. Generate OTP → kirim ke Email
  │◄── 200 { otp_key, user_hint } ─────── │
  │                                        │
  │── POST /auth/otp/verify-email ───────► │
  │   { otp_key, code }                    │  4. Verifikasi OTP email (soft delete)
  │                                        │  5. Generate OTP baru → kirim ke WhatsApp
  │◄── 200 { wa_otp_key, user_hint } ───── │
  │                                        │
  │── POST /auth/otp/verify-wa ──────────► │
  │   { wa_otp_key, code }                 │  6. Verifikasi OTP WA (hard delete)
  │                                        │  7. Terbitkan JWT access + refresh token
  │◄── 200 { access_token, user } ──────── │
```

---

## Daftar Endpoint Auth

### Core Login

| Method | Endpoint | Deskripsi | Auth |
|--------|----------|-----------|------|
| `POST` | `/api/v1/auth/login` | Step 1 — validasi password, kirim OTP email | ❌ |
| `POST` | `/api/v1/auth/otp/verify-email` | Step 2 — verifikasi OTP email, kirim OTP WA | ❌ |
| `POST` | `/api/v1/auth/otp/verify-wa` | Step 3 — verifikasi OTP WA, terbitkan JWT | ❌ |

### Resend OTP

| Method | Endpoint | Deskripsi | Auth |
|--------|----------|-----------|------|
| `POST` | `/api/v1/auth/otp/resend-email` | Kirim ulang OTP email | ❌ |
| `POST` | `/api/v1/auth/otp/resend-wa` | Kirim ulang OTP WhatsApp | ❌ |

### Session

| Method | Endpoint | Deskripsi | Auth |
|--------|----------|-----------|------|
| `POST` | `/api/v1/auth/refresh` | Perbarui access token | 🔑 refresh |
| `GET`  | `/api/v1/auth/me` | Profil user aktif | 🔑 access |
| `POST` | `/api/v1/auth/logout` | Logout (hapus token di client) | 🔑 access |

---

## Request & Response Detail

### POST `/api/v1/auth/login`

**Request:**
```json
{
  "identifier": "user@email.com",
  "password": "plaintext_password"
}
```

**Response 200:**
```json
{
  "message": "OTP email telah dikirim.",
  "otp_sent": true,
  "otp_key": "otp_email_{user_id}_{user_type}",
  "user_hint": {
    "id": 1,
    "user_type": "tuser",
    "email_masked": "us***@email.com",
    "phone": "+628xxxxxxxx",
    "phone_masked": "0812****xx"
  }
}
```

**Response Error:**

| Code | error_code | Kondisi |
|------|------------|---------|
| 400 | — | identifier atau password kosong |
| 401 | — | Password salah |
| 403 | `DTSEN_ACCESS_DENIED` | `tuser.is_dtsen_user` bukan `'Y'` |
| 403 | — | Akun kadaluarsa atau belum disetujui |
| 404 | `ACCOUNT_NOT_FOUND` | Email/no. HP tidak ditemukan |

---

### POST `/api/v1/auth/otp/verify-email`

**Request:**
```json
{
  "otp_key": "otp_email_1_tuser",
  "code": "123456"
}
```

**Response 200:**
```json
{
  "message": "OTP email valid. OTP WhatsApp telah dikirim.",
  "wa_otp_sent": true,
  "wa_otp_key": "otp_wa_1_tuser",
  "user_hint": {
    "id": 1,
    "user_type": "tuser",
    "phone_masked": "0812****xx"
  }
}
```

---

### POST `/api/v1/auth/otp/verify-wa`

**Request:**
```json
{
  "wa_otp_key": "otp_wa_1_tuser",
  "code": "654321"
}
```

**Response 200:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "Bearer",
  "user": { "...profil user..." }
}
```

---

## User Types

| `user_type` | Tabel DB | Syarat Login |
|-------------|----------|--------------|
| `tuser` | `tuser` | `is_dtsen_user = 'Y'`, `approve = 1`, `is_expired != 'Y'` |
| `dtsen` | `t_dtsen_akses` | `statuses = 'aktif'`, `deleted_at IS NULL` |

---

## Bug yang Sudah Diperbaiki

### `AttributeError: 'TUser' object has no attribute 'is_dtsen_user'` — ✅ Fixed

- **Tanggal:** 2026-07-10
- **Cause:** Kolom `is_dtsen_user` ter-comment di `backend/app/models/tuser.py` sehingga atribut tidak tersedia di model SQLAlchemy, padahal `auth_service.py` sudah mengaksesnya.
- **Fix:** Kolom di-uncomment di model + DB production di-`ALTER TABLE` untuk menambah kolom.
- **Dampak sebelum fix:** Semua login `tuser` gagal dengan HTTP 500 alih-alih 403.
