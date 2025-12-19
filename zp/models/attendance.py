import json
from models import db

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    course_id = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, nullable=False)
    submitted_students = db.Column(db.Text)  # 存储为JSON数组字符串
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    deadline = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'course_id': self.course_id,
            'teacher_id': self.teacher_id,
            'submitted_students': json.loads(self.submitted_students) if self.submitted_students else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'deadline': self.deadline.isoformat() if self.deadline else None
        }