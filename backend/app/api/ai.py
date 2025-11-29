from datetime import datetime
import random

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
import jieba.analyse as jieba_analyse

from ..utils.responses import ok, error
from ..models import Material
from ..extensions import db
from ..authz import ensure_course_member

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")


@ai_bp.post("/materials/classify")
@jwt_required()
def classify_material():
    """
    对资料进行关键词提取并写回 tags。
    支持：
    - 指定 material_id：从 DB 取标题/描述
    - 或直接传 title/description 文本
    - 可传 course_id 进行权限校验
    """
    data = request.get_json(silent=True) or {}
    material_id = data.get("material_id")
    course_id = data.get("course_id")

    material = None
    text = ""
    if material_id:
        material = Material.query.get(material_id)
        if not material:
            return error("material not found", 404)
        course_id = material.course_id
        text = f"{material.title or ''} {material.description or ''}"
    else:
        title = data.get("title") or ""
        desc = data.get("description") or ""
        text = f"{title} {desc}"
        if not text.strip():
            return error("title or description required")

    if not course_id:
        return error("course_id required")

    # 权限：课程成员可用
    _, err = ensure_course_member(course_id)
    if err:
        return err

    # 提取关键词
    tags = jieba_analyse.extract_tags(text, topK=3) or ["通用资料"]

    if material:
        # 合并去重
        existing = set(material.tags or [])
        material.tags = list(existing.union(tags))
        db.session.commit()

    return ok({
        "material_id": material_id,
        "course_id": course_id,
        "tags": tags,
        "updated": bool(material),
    })


@ai_bp.post("/grades/predict")
@jwt_required()
def predict_grades():
    data = request.get_json(silent=True) or {}
    course_id = data.get("course_id")
    if not course_id:
        return error("course_id required")
    # mock: 返回 5 个高风险学生
    results = []
    for sid in range(1, 6):
        score = random.uniform(50, 75)
        results.append(
            {"student_id": f"S{sid:03d}", "predicted_score": round(score, 1), "risk_level": "high"}
        )
    return ok({"course_id": course_id, "model": "mock-regression", "generated_at": datetime.utcnow().isoformat(), "results": results})


@ai_bp.post("/attendance/recognize")
@jwt_required()
def recognize_attendance():
    # mock：返回识别统计
    recognized = random.randint(20, 30)
    total = 32
    return ok(
        {
            "recognized": recognized,
            "total": total,
            "accuracy": round(recognized / total, 2),
            "faces": [{"student_id": f"S{idx:03d}", "confidence": round(random.uniform(0.7, 0.99), 2)} for idx in range(recognized)],
        }
    )


@ai_bp.post("/qa/ask")
@jwt_required()
def ai_qa():
    data = request.get_json(silent=True) or {}
    question = data.get("question")
    if not question:
        return error("question required")
    # 简易回覆
    return ok({"answer": f"这是基于课程资料的示例回答：{question[:20]}...", "source": "mock-faq"})
