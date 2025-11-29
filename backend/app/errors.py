from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_error(err: HTTPException):
        response = {
            "message": err.description or "请求错误",
            "status": err.code,
        }
        return jsonify(response), err.code

    @app.errorhandler(Exception)
    def handle_generic_error(err: Exception):  # pragma: no cover - 全局兜底
        app.logger.exception(err)
        return jsonify({"message": "服务器开小差，请稍后再试"}), 500
