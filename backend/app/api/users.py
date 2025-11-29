from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from ..models import User
from ..utils.responses import ok

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.get("")
@jwt_required()
def list_users():
    """
    简易用户搜索，用于选择成员。
    支持参数：q（模糊匹配 name/email），page/page_size。
    """
    q = (request.args.get("q") or "").strip().lower()
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 10)), 1), 50)

    query = User.query
    if q:
        like = f"%{q}%"
        query = query.filter((User.name.ilike(like)) | (User.email.ilike(like)))

    total = query.count()
    items = query.order_by(User.created_at.desc()).limit(page_size).offset((page - 1) * page_size).all()
    payload = [
        {"id": u.id, "name": u.name, "email": u.email, "role": u.role, "created_at": u.created_at.isoformat()}
        for u in items
    ]
    return ok({"items": payload, "total": total, "page": page, "page_size": page_size})
