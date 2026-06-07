from flask import Flask
from flask_cors import CORS
from .extensions import db, migrate, jwt
from .api.v1 import api_v1_bp
from config import config
import os


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Blueprints
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

    return app
