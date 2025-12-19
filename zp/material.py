import json
from models import db

class Material(db.Model):
    __tablename__ = 'material'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(200), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    course_id = db.Column(db.Integer)
    tags = db.Column(db.String(500))  # 存储为逗号分隔的字符串
    uploaded_by = db.Column(db.Integer)  # 用户ID
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'filename': self.filename,
            'course_id': self.course_id,
            'tags': self.tags.split(',') if self.tags else [],
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }