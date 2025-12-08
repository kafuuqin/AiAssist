import json
from typing import Dict, Any, List
from deepface import DeepFace
import numpy as np
import cv2
import os

from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import FaceEmbedding
from ..utils.imagecode import _encode_image_to_base64, _decode_image_file

faces_bp = Blueprint("faces", __name__, url_prefix="/faces")

@faces_bp.post("/register")
@jwt_required()
def register_face_api():
    """
    POST /faces/register

    Content-Type: multipart/form-data
    字段：
        - file     : 要录入的人脸图片
        - user_id  : 对应的用户ID（可选，不传就用当前登录用户ID）
        - name     : 显示用名字（可选）

    返回：
        {
          "success": true,
          "error": null,
          "data": { FaceEmbedding.to_dict() }
        }
    """
    # 取文件
    file = request.files.get("file")
    if file is None or file.filename == "":
        return jsonify({"success": False, "error": "缺少图片文件 file", "data": None}), 400

    user_id_raw = request.form.get("user_id")

    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "无效的 user_id", "data": None}), 400

    name = request.form.get("name")

    #  解析图片
    img = _decode_image_file(file)
    if img is None:
        return jsonify({"success": False, "error": "无法解析图片", "data": None}), 400

    # 调用 DeepFace 的录入函数（提取 embedding）
    res = register_face(
        image=img,
        person_id=str(user_id),
        model_name="Facenet512",
        detector_backend="retinaface",
    )

    if not res.get("success"):
        return jsonify({"success": False, "error": res.get("error") or "提取人脸特征失败", "data": None}), 200

    data = res["data"]
    embedding = data["embedding"]
    model_name = data["model_name"]
    detector_backend = data["detector_backend"]

    # 6. 写入数据库
    face = FaceEmbedding(
        user_id=user_id,
        name=name,
        embedding=embedding,
        model_name=model_name,
        detector_backend=detector_backend,
    )
    db.session.add(face)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "error": None,
            "data": face.to_dict(),
        }
    ), 201


@faces_bp.post("/recognize")
@jwt_required()
def recognize_faces():
    """
    POST /faces/recognize
    Content-Type: multipart/form-data
    字段：
        - file: 要识别的图片

    返回：
        {
          "success": true,
          "error": null,
          "data": {
            "faces": [... 每张脸的识别信息 ...],
            "image_base64": "data:image/jpeg;base64,...."
          }
        }
    """
    # 1. 拿上传文件
    file = request.files.get("file")
    if file is None or file.filename == "":
        return jsonify({"success": False, "error": "缺少图片文件 file", "data": None}), 400

    # 2. 解码为 OpenCV 图像
    img = _decode_image_file(file)
    if img is None:
        return jsonify({"success": False, "error": "无法解析图片", "data": None}), 400

    # 3. 从数据库加载所有已录入人脸特征
    enrolled_faces = _load_enrolled_faces()
    if not enrolled_faces:
        return jsonify({"success": False, "error": "尚未录入任何人脸特征", "data": None}), 200

    # 4. 调用你的 DeepFace 识别函数
    res = recognize_face(
        image=img,
        enrolled_faces=enrolled_faces,
        model_name="Facenet512",
        detector_backend="retinaface",
        distance_metric="cosine",
        threshold=0.4,
        top_k=5,
        draw=True,
    )

    if not res.get("success"):
        return jsonify({"success": False, "error": res.get("error") or "识别失败", "data": None}), 200

    data = res["data"]
    out_img = data.get("image")
    results = data.get("results", [])

    if out_img is None:
        return jsonify({"success": False, "error": "识别结果中未返回图片", "data": None}), 500

    # 5. 图片转 base64，便于前端直接展示
    img_b64 = _encode_image_to_base64(out_img)
    if img_b64 is None:
        return jsonify({"success": False, "error": "图片编码失败", "data": None}), 500

    # 6. 返回数据（results 里已经包含 best_match / matches / region 等）
    return jsonify(
        {
            "success": True,
            "error": None,
            "data": {
                "faces": results,
                "image_base64": img_b64,
            },
        }
    ), 200

def _load_enrolled_faces() -> list[dict]:
    """
    从数据库中加载所有已录入人脸，转换成 recognize_face 需要的结构：
        [
            {
                "person_id": user_id 或其他业务ID,
                "name": "张三",
                "embedding": [...],
                ...
            }
        ]
    """
    faces: list[FaceEmbedding] = FaceEmbedding.query.all()
    enrolled_faces: list[dict] = []

    for f in faces:
        emb = f.embedding
        # 如果你用 Text 存的 JSON，这里要手动 loads
        # if isinstance(emb, str):
        #     emb = json.loads(emb)

        enrolled_faces.append(
            {
                "db_id": f.id,
                "person_id": f.user_id,  # 或者用你自己的业务ID
                "name": f.name,
                "embedding": emb,
            }
        )

    return enrolled_faces


def _compute_distance(emb1, emb2, metric="cosine") -> float:
    """计算两个 embedding 向量间距离"""
    emb1 = np.array(emb1)
    emb2 = np.array(emb2)
    if metric == "cosine":
        return 1 - np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    elif metric == "euclidean":
        return np.linalg.norm(emb1 - emb2)
    elif metric == "euclidean_l2":
        e1 = emb1 / np.linalg.norm(emb1)
        e2 = emb2 / np.linalg.norm(emb2)
        return np.linalg.norm(e1 - e2)
    else:
        return 1 - np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))


def _put_text_chinese(img, text, position, font_size=25, color=(0, 255, 0)):
    """
    在OpenCV图像上绘制中文文字。
    参数：
        img: OpenCV图像 (BGR)
        text: 中文文本
        position: 左上角坐标 (x, y)
        font_size: 字体大小
        color: 字体颜色 (B, G, R)
    """
    from PIL import Image, ImageDraw, ImageFont

    # 将 OpenCV 图像转换为 PIL 图像
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    # 自动加载支持中文的字体
    # Windows 通常有 "simsun.ttc"（宋体），Linux 通常有 "NotoSansCJK-Regular.ttc"
    try:
        font_path = "C:/Windows/Fonts/simsun.ttc" if os.name == "nt" else "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    draw.text(position, text, font=font, fill=color[::-1])  # PIL颜色为RGB
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


def recognize_face(
        image: np.ndarray,
        enrolled_faces: List[Dict[str, Any]],
        model_name: str = "Facenet512",
        detector_backend: str = "retinaface",
        distance_metric: str = "cosine",
        threshold: float = 0.4,
        top_k: int = 5,
        draw: bool = True,
) -> Dict[str, Any]:
    """
    人脸识别函数（返回识别信息与绘制图片）
    ----------------------------------------
    参数：
        image : np.ndarray
            待识别的图像（BGR 或 RGB 格式）
        enrolled_faces : List[Dict]
            数据库中已录入人脸数据列表：
                [{"person_id": "u001", "embedding": [...], "name": "张三"}, ...]
        model_name : str
            DeepFace 模型（与录入时一致）
        detector_backend : str
            人脸检测器（默认 retinaface）
        distance_metric : str
            距离度量方式 ("cosine" / "euclidean" / "euclidean_l2")
        threshold : float
            阈值（越小越相似）
        top_k : int
            返回前 K 个结果
        draw : bool
            是否在图像上绘制识别框和姓名（中文）

    返回：
        {
            "success": True/False,
            "error": None 或 错误信息,
            "data": {
                "face_count": int,
                "matches": [...],
                "best_match": {...},
                "image": 绘制后的 np.ndarray 或 None
            }
        }
    """
    if not enrolled_faces:
        return {"success": False, "error": "enrolled_faces 为空", "data": None}

    try:
        # 使用 DeepFace 检测并提取所有人脸
        reps = DeepFace.represent(
            img_path=image,
            model_name=model_name,
            detector_backend=detector_backend,
            enforce_detection=True
        )

        if not reps:
            return {"success": False, "error": "未检测到人脸", "data": None}

        results = []
        image_out = image.copy()

        for rep in reps:
            query_emb = rep["embedding"]
            region = rep.get("facial_area", None)
            if query_emb is None or region is None:
                continue

            # 计算与所有已录入人脸的距离
            matches = []
            for item in enrolled_faces:
                db_emb = item.get("embedding")
                if db_emb is None:
                    continue
                distance = _compute_distance(query_emb, db_emb, distance_metric)
                matches.append({
                    "person_id": item.get("person_id"),
                    "distance": float(distance),
                    "is_recognized": distance <= threshold,
                    "extra": {k: v for k, v in item.items() if k not in ["embedding", "person_id"]}
                })

            if not matches:
                continue

            matches.sort(key=lambda x: x["distance"])
            top_matches = matches[:top_k]
            best_match = top_matches[0]

            if draw and region:
                x, y, w, h = region["x"], region["y"], region["w"], region["h"]
                name = best_match["extra"].get("name", best_match["person_id"])
                color = (0, 255, 0) if best_match["is_recognized"] else (0, 0, 255)
                cv2.rectangle(image_out, (x, y), (x + w, y + h), color, 2)
                text = f"{name} ({best_match['distance']:.2f})"
                image_out = _put_text_chinese(image_out, text, (x, y - 30), font_size=25, color=color)

            results.append({
                "region": region,
                "best_match": best_match,
                "matches": top_matches
            })

        return {
            "success": True,
            "error": None,
            "data": {
                "face_count": len(results),
                "results": results,
                "image": image_out if draw else None
            }
        }

    except Exception as e:
        return {"success": False, "error": str(e), "data": None}



from typing import Dict, Any
from deepface import DeepFace
import numpy as np


def register_face(
        image: np.ndarray,
        person_id: str,
        model_name: str = "Facenet512",
        detector_backend: str = "retinaface",
) -> Dict[str, Any]:
    """
    人脸录入函数（提取 embedding 特征）
    ----------------------------------------
    参数：
        image : np.ndarray
            待录入的人脸图像（BGR 或 RGB 格式，来自 cv2 或 PIL 转换的数组）
        person_id : str
            该图片对应的人员唯一标识（如用户ID/工号）
        model_name : str
            DeepFace 模型（默认 "Facenet512"）
        detector_backend : str
            人脸检测器（默认 "retinaface"）

    返回：
        dict，形如：
        {
            "success": True/False,
            "error": None 或 错误信息,
            "data": {
                "person_id": str,
                "embedding": [float, ...],
                "embedding_dim": int,
                "model_name": str,
                "detector_backend": str,
                "face_count": int
            }
        }
    """
    try:
        # 提取 embedding 向量
        reps = DeepFace.represent(
            img_path=image,              # 可直接传入 numpy 数组
            model_name=model_name,
            detector_backend=detector_backend,
            enforce_detection=True
        )

        if not reps or len(reps) == 0:
            return {"success": False, "error": "未检测到人脸", "data": None}

        # 取第一张人脸的 embedding
        embedding = reps[0].get("embedding", [])
        if not embedding:
            return {"success": False, "error": "无法提取人脸特征向量", "data": None}

        return {
            "success": True,
            "error": None,
            "data": {
                "person_id": person_id,
                "embedding": embedding,
                "embedding_dim": len(embedding),
                "model_name": model_name,
                "detector_backend": detector_backend,
                "face_count": len(reps)
            }
        }

    except Exception as e:
        return {"success": False, "error": str(e), "data": None}
