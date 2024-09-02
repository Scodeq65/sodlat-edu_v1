from flask import Blueprint

bp = Blueprint('main_bp', __name__)

from app.routes import main