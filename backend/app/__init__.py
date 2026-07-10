import logging
import os

from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from pythonjsonlogger import jsonlogger
from .extensions import db, migrate, jwt
from .api.v1 import api_v1_bp
from config import config
from dotenv import load_dotenv

# Load .env sebelum apapun
load_dotenv()

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "DTSEN API",
        "description": "API Documentation for DTSEN Backend",
        "version": "1.0.0",
        "contact": {
            "name": "J Angga Wijaya",
            "url": "https://janggawijaya.com"
        }
    },
    "host": "",
    "basePath": "/",
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header. Format: Bearer <token>"
        }
    },
    "consumes": ["application/json"],
    "produces": ["application/json"]
}


def _setup_json_logging(app: Flask) -> None:
    """Konfigurasi JSON structured logging agar docker logs -f menampilkan JSON."""
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S',
    )
    handler.setFormatter(formatter)
    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False

    # Expose log [WA] juga dari root logger (gunicorn workers)
    root = logging.getLogger()
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        root.addHandler(handler)
    root.setLevel(logging.INFO)


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # JSON Logging (harus sebelum ekstensi lain agar log init juga terbaca)
    _setup_json_logging(app)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=app.config.get('CORS_ORIGINS', '*'))

    # Swagger
    Swagger(app, config=swagger_config, template=swagger_template)

    # Blueprints
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

    return app
