from datetime import datetime

from ..extensions import db


class Assignment(db.Model):
    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50))
    weight = db.Column(db.Float, default=1.0)
    full_score = db.Column(db.Float, default=100.0)
    due_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    course = db.relationship("Course", backref=db.backref("assignments", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "title": self.title,
            "type": self.type,
            "weight": self.weight,
            "full_score": self.full_score,
            "due_at": self.due_at.isoformat() if self.due_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Grade(db.Model):
    __tablename__ = "grades"

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignments.id"), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    score = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text)
    graded_at = db.Column(db.DateTime, default=datetime.utcnow)

    assignment = db.relationship("Assignment", backref=db.backref("grades", lazy=True))
    student = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "assignment_id": self.assignment_id,
            "student_id": self.student_id,
            "score": self.score,
            "comment": self.comment,
            "graded_at": self.graded_at.isoformat() if self.graded_at else None,
        }
