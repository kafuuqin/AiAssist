import os

from flask import Flask, jsonify

from .config import get_config
from .extensions import cors, db, jwt, migrate
from .api import api_bp
from .errors import register_error_handlers


def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))
    _ensure_upload_dir(app)

    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_shellcontext(app)

    @app.get("/health")
    def health():
        # 尝试一次数据库连接，失败返回 500
        try:
            db.session.execute(db.text("SELECT 1"))
        except Exception as exc:  # pragma: no cover - 健康检查，简单处理
            return jsonify({"status": "error", "message": str(exc)}), 500
        return jsonify({"status": "ok"})

    return app


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", ["*"])}},
        supports_credentials=True,
    )


def register_blueprints(app):
    app.register_blueprint(api_bp)


def register_shellcontext(app):
    @app.shell_context_processor
    def make_shell_context():
        from .models import (
            AttendanceRecord,
            AttendanceSession,
            Assignment,
            Course,
            Enrollment,
            Grade,
            Material,
            Poll,
            PollVote,
            User,
        )

        return {
            "db": db,
            "User": User,
            "Course": Course,
            "Enrollment": Enrollment,
            "Material": Material,
            "AttendanceSession": AttendanceSession,
            "AttendanceRecord": AttendanceRecord,
            "Assignment": Assignment,
            "Grade": Grade,
            "Poll": Poll,
            "PollVote": PollVote,
        }


def _ensure_upload_dir(app):
    upload_dir = app.config.get("UPLOAD_DIR")
    if upload_dir and not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
