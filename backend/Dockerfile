FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Buat folder logs agar tersedia sejak image build
RUN mkdir -p /app/logs/sync

# Copy dan set permission entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose internal port
EXPOSE 5000

# Gunakan entrypoint untuk auto-start sync worker + gunicorn
CMD ["/entrypoint.sh"]
