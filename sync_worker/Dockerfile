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

CMD ["python3", "-u", "sync_keluarga_full.py"]
