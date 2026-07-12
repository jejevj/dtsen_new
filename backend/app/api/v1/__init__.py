from flask import Blueprint

api_v1_bp = Blueprint('api_v1', __name__)

from . import auth, mustahik, laz, report, home, wilayah, health, geo, tampilan_dtsen  # noqa: F401, E402
