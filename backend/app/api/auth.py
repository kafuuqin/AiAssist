from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

from ..extensions import db
from ..models import User
from ..utils.responses import error, ok

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _get_json():
    return request.get_json(silent=True) or {}


@auth_bp.post("/register")
def register():
    data = _get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role") or "teacher"

    if not all([name, email, password]):
        return error("name, email, password required")

    if User.query.filter_by(email=email.lower().strip()).first():
        return error("email already registered")

    user = User(name=name.strip(), email=email.lower().strip(), role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return ok({"id": user.id, "name": user.name, "email": user.email, "role": user.role}, 201)


@auth_bp.post("/login")
def login():
    data = _get_json()
    email = (data.get("email") or "").lower().strip()
    password = data.get("password")

    if not email or not password:
        return error("email and password required")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return error("invalid credentials", 401)

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return ok({"access_token": access_token, "refresh_token": refresh_token, "user": user.to_dict()})


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return ok({"access_token": access_token})


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return error("user not found", 404)
    return ok(user.to_dict())
