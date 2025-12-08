from datetime import datetime
from ..extensions import db
import json


class FaceEmbedding(db.Model):
    __tablename__ = "face_embeddings"

    id = db.Column(db.Integer, primary_key=True)
    # 关联到 users 表（根据你自己的用户表名来）
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    # 可选：再冗余存一个名字，方便调试和显示
    name = db.Column(db.String(100))

    # 人脸特征向量，存成 JSON（MySQL 原生 JSON 或 TEXT 都可以）
    embedding = db.Column(db.JSON, nullable=False)

    # 记录使用的模型和检测器，方便以后换模型或兼容多个版本
    model_name = db.Column(db.String(50), default="Facenet512")
    detector_backend = db.Column(db.String(50), default="retinaface")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 反向关系：一个用户可以有多条 face_embeddings
    user = db.relationship("User", backref=db.backref("face_embeddings", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "embedding": self.embedding,  # 这里就是 list[float]，可以直接给前端/服务用
            "model_name": self.model_name,
            "detector_backend": self.detector_backend,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
