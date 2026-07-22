FROM python:3.11-slim

WORKDIR /app

# Install dependencies sistem
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements dari backend (pakai yang sama)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode backend
COPY . .

# Buat folder log
RUN mkdir -p /app/logs/sync

# sync_worker dinonaktifkan — ubah CMD ini untuk mengaktifkan kembali
CMD ["sh", "-c", "echo 'sync_worker disabled' && exit 0"]
