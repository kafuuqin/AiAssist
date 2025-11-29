from datetime import datetime

from sqlalchemy.dialects.mysql import JSON

from ..extensions import db


class Material(db.Model):
    __tablename__ = "materials"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    path = db.Column(db.String(500))
    file_type = db.Column(db.String(50))
    size = db.Column(db.Integer)
    tags = db.Column(JSON, default=list)
    uploader_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    course = db.relationship("Course", backref=db.backref("materials", lazy=True))
    uploader = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "title": self.title,
            "description": self.description,
            "path": self.path,
            "file_type": self.file_type,
            "size": self.size,
            "tags": self.tags or [],
            "uploader_id": self.uploader_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
