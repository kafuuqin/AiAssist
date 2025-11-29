from datetime import datetime

from ..extensions import db


class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    role_in_course = db.Column(db.String(20), default="student")
    status = db.Column(db.String(20), default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    course = db.relationship("Course", backref=db.backref("enrollments", lazy=True))
    user = db.relationship("User", backref=db.backref("enrollments", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "user_id": self.user_id,
            "role_in_course": self.role_in_course,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
