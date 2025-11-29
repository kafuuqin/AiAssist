from datetime import datetime

from sqlalchemy.dialects.mysql import JSON

from ..extensions import db


class Poll(db.Model):
    __tablename__ = "polls"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    question = db.Column(db.String(255), nullable=False)
    options = db.Column(JSON, default=list)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    course = db.relationship("Course", backref=db.backref("polls", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "question": self.question,
            "options": self.options or [],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PollVote(db.Model):
    __tablename__ = "poll_votes"

    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey("polls.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    option_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    poll = db.relationship("Poll", backref=db.backref("votes", lazy=True))
    user = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "poll_id": self.poll_id,
            "user_id": self.user_id,
            "option_index": self.option_index,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
