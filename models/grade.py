from models import db

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(100), nullable=False)  # 科目名称
    score = db.Column(db.Float, nullable=False)
    exam_type = db.Column(db.String(50), nullable=True)  # 考试类型
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'subject': self.subject,
            'score': self.score,
            'exam_type': self.exam_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }