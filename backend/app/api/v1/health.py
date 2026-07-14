from flask import jsonify
from . import api_v1_bp
from ...extensions import db
from sqlalchemy import text
import datetime


@api_v1_bp.get('/health')
def health_check():
    """
    Health check - cek status API dan koneksi database
    ---
    tags:
      - Health
    responses:
      200:
        description: API dan DB berjalan normal
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
            database:
              type: string
              example: connected
            timestamp:
              type: string
              example: "2026-07-10T08:00:00"
      500:
        description: Koneksi database gagal
    """
    try:
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
        db_message = 'MySQL connection successful'
        status_code = 200
    except Exception as e:
        db_status = 'error'
        db_message = str(e)
        status_code = 500

    return jsonify({
        'status': 'ok' if status_code == 200 else 'error',
        'database': db_status,
        'db_message': db_message,
        'timestamp': datetime.datetime.utcnow().isoformat()
    }), status_code
