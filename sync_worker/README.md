# DTSEN Sync Worker — Keluarga

Container terpisah untuk sync data `zawa_keluarga` dari API ZAWA Kemenag.
Berjalan independen dari `dtsen_api` — aman di-rebuild/restart kapan saja.

## Cara pakai

### 1. Setup `.env`
```bash
cp .env.example .env
# Edit .env sesuai kebutuhan
```

### 2. Build container
```bash
docker compose build
```

### 3. Jalankan sync (sekali jalan, bukan daemon)
```bash
docker compose run --rm sync_keluarga
```

### 4. Monitor log realtime
```bash
tail -f logs/keluarga_full.log
```

### 5. Jalankan background (nohup)
```bash
docker compose run -d --rm sync_keluarga
```

## Environment variables

| Variable | Default | Keterangan |
|---|---|---|
| `DATABASE_URL` | wajib | MySQL connection string |
| `ZAWA_API_KEY` | wajib | API key ZAWA Kemenag |
| `BATCH_SIZE` | `0` | Jumlah NKK per run (0 = semua) |
| `SLEEP_BETWEEN` | `0.1` | Jeda antar request (detik) |
| `LOG_EVERY` | `25` | Progress log setiap N NKK |

## Catatan

- Container ini **tidak mengganggu** `dtsen_api` saat `docker compose up --force-recreate`
- Log tersimpan di `./logs/keluarga_full.log` di host
- Setiap run hanya fetch NKK yang **belum ada** di `zawa_keluarga`
- API ZAWA rate limit 60 req/menit — jangan set `SLEEP_BETWEEN` terlalu kecil
