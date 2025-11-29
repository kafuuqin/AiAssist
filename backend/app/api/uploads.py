import os
import uuid

from flask import Blueprint, current_app, request, send_from_directory
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from ..utils.responses import error, ok
from ..models import Material
from ..authz import ensure_course_member

uploads_bp = Blueprint("uploads", __name__, url_prefix="/uploads")


def allowed_file(filename):
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    allowed_exts = set(current_app.config.get("ALLOWED_UPLOAD_EXTS") or [])
    denied_exts = set(current_app.config.get("DISALLOWED_UPLOAD_EXTS") or [])
    if ext in denied_exts:
        return False
    return ext in allowed_exts


def allowed_mime(mimetype):
    # 当未配置白名单时不校验 MIME
    allowed = set(current_app.config.get("ALLOWED_UPLOAD_MIME") or [])
    if not allowed:
        return True
    return mimetype in allowed


@uploads_bp.post("")
@jwt_required()
def upload_file():
    if "file" not in request.files:
        return error("file required")
    file = request.files["file"]
    if file.filename == "":
        return error("empty filename")
    if not allowed_file(file.filename):
        return error("invalid filename or extension")
    if not allowed_mime(file.mimetype):
        return error("invalid mime type")

    # size 校验（优先用 content_length）
    content_length = request.content_length or file.content_length or 0
    max_size = current_app.config.get("MAX_CONTENT_LENGTH")
    if max_size and content_length and content_length > max_size:
        return error("file too large", 413)

    upload_dir = current_app.config.get("UPLOAD_DIR")
    os.makedirs(upload_dir, exist_ok=True)
    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1]
    new_name = f"{uuid.uuid4().hex}{ext}"
    file.save(os.path.join(upload_dir, new_name))
    url = f"/api/uploads/{new_name}"
    return ok({"filename": new_name, "original": filename, "url": url}, 201)


@uploads_bp.get("/<path:filename>")
@jwt_required()
def serve_file(filename):
    upload_dir = current_app.config.get("UPLOAD_DIR")
    # 根据文件名尝试找到对应资料，校验课程成员权限
    material = Material.query.filter(Material.path.ilike(f"%/{filename}")).first()
    if material:
        _, err = ensure_course_member(material.course_id)
        if err:
            return err
    else:
        return error("file not found", 404)

    return send_from_directory(upload_dir, filename, as_attachment=False)
