from flask import Blueprint

from .auth import auth_bp
from .courses import courses_bp
from .uploads import uploads_bp
from .ai import ai_bp
from .imports import imports_bp
from .users import users_bp

api_bp = Blueprint("api", __name__, url_prefix="/api")
api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(courses_bp)
api_bp.register_blueprint(uploads_bp)
api_bp.register_blueprint(ai_bp)
api_bp.register_blueprint(imports_bp)
api_bp.register_blueprint(users_bp)
