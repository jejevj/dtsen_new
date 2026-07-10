from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from .extensions import db, migrate, jwt
from .api.v1 import api_v1_bp
from config import config
from dotenv import load_dotenv
import os

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


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

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
