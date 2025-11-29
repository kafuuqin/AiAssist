import os

import pandas as pd
from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required

from .uploads import allowed_file
from ..extensions import db
from ..models import Assignment, Grade
from ..authz import ensure_course_member
from ..utils.responses import error, ok

imports_bp = Blueprint("imports", __name__, url_prefix="/courses")


@imports_bp.post("/<int:course_id>/grades/import")
@jwt_required()
def import_grades(course_id):
    """
    导入成绩（CSV/XLSX），严格校验后事务写入。
    payload: {assignment_id, file_path}
    - 必填列：student_id, assignment_id, score
    - score 范围：0~100（可在此处调整）
    - 发现错误时整体回滚并返回错误行信息
    """
    data = request.get_json(silent=True) or {}
    assignment_id = data.get("assignment_id")
    file_path = data.get("file_path")

    if not assignment_id or not file_path:
        return error("assignment_id and file_path required")

    # 权限：课程 owner/teacher/ta/admin
    _, err = ensure_course_member(course_id, allow_roles=["teacher", "ta"], as_owner=True)
    if err:
        return err

    assignment = Assignment.query.filter_by(id=assignment_id, course_id=course_id).first()
    if not assignment:
        return error("assignment not found", 404)

    filename = os.path.basename(file_path)
    upload_dir = current_app.config.get("UPLOAD_DIR")
    full_path = os.path.join(upload_dir, filename)
    if not os.path.exists(full_path):
        return error("file not found", 404)
    if not allowed_file(filename):
        return error("invalid file")

    # 读取文件
    try:
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(full_path)
        else:
            df = pd.read_excel(full_path)
    except Exception as exc:  # pragma: no cover - 文件解析异常
        return error(f"failed to parse file: {exc}")

    required_cols = {"student_id", "assignment_id", "score"}
    if not required_cols.issubset(set(df.columns)):
        return error("missing required columns: student_id, assignment_id, score")

    errors = []
    payload = []
    seen = set()
    MIN_SCORE, MAX_SCORE = 0, 100

    for idx, row in df.iterrows():
        line_no = idx + 2  # header 占一行
        sid = str(row.get("student_id", "")).strip()
        aid = str(row.get("assignment_id", "")).strip()
        score_raw = row.get("score")
        comment = row.get("comment") if "comment" in df.columns else None

        if not sid:
            errors.append({"line": line_no, "message": "student_id required"})
            continue
        if aid and str(aid) != str(assignment_id):
            errors.append({"line": line_no, "message": "assignment_id mismatch"})
            continue
        try:
            score_val = float(score_raw)
        except Exception:
            errors.append({"line": line_no, "message": "score must be number"})
            continue
        if score_val < MIN_SCORE or score_val > MAX_SCORE:
            errors.append({"line": line_no, "message": f"score out of range {MIN_SCORE}-{MAX_SCORE}"})
            continue
        if sid in seen:
            errors.append({"line": line_no, "message": "duplicate student_id in file"})
            continue
        seen.add(sid)
        payload.append({"student_id": sid, "score": score_val, "comment": comment})

    if errors:
        return error({"message": "validation failed", "errors": errors})

    inserted = 0
    updated = 0
    try:
        with db.session.begin():
            for item in payload:
                existing = Grade.query.filter_by(assignment_id=assignment_id, student_id=item["student_id"]).first()
                if existing:
                    existing.score = item["score"]
                    existing.comment = item["comment"]
                    updated += 1
                else:
                    grade = Grade(
                        assignment_id=assignment_id,
                        student_id=item["student_id"],
                        score=item["score"],
                        comment=item["comment"],
                    )
                    db.session.add(grade)
                    inserted += 1
    except Exception as exc:  # pragma: no cover - 事务异常回滚
        db.session.rollback()
        return error(f"import failed: {exc}")

    return ok({"imported": inserted, "updated": updated, "file": filename})
