from datetime import datetime

from ..extensions import db


class AttendanceSession(db.Model):
    __tablename__ = "attendance_sessions"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    mode = db.Column(db.String(50), default="qrcode")
    start_at = db.Column(db.DateTime, default=datetime.utcnow)
    end_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="open")

    course = db.relationship("Course", backref=db.backref("attendance_sessions", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "title": self.title,
            "mode": self.mode,
            "start_at": self.start_at.isoformat() if self.start_at else None,
            "end_at": self.end_at.isoformat() if self.end_at else None,
            "status": self.status,
        }


class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("attendance_sessions.id"), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), default="present")
    evidence = db.Column(db.String(255))
    recognized_face_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    session = db.relationship("AttendanceSession", backref=db.backref("records", lazy=True))
    student = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "student_id": self.student_id,
            "status": self.status,
            "evidence": self.evidence,
            "recognized_face_id": self.recognized_face_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
