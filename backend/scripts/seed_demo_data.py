"""
Demo data seeder for the Teacher Assistant app.

Usage examples (Windows CMD):
  set FLASK_APP=wsgi.py
  set FLASK_SKIP_DOTENV=1
  set DATABASE_URL=mysql+pymysql://root:pass@127.0.0.1:3307/teacher_assistant
  python scripts\\seed_demo_data.py

You can also run from repo root:
  set FLASK_APP=backend/wsgi.py
  set FLASK_SKIP_DOTENV=1
  set DATABASE_URL=...
  python backend\\scripts\\seed_demo_data.py

The script is idempotent for the predefined demo entities (same codes/emails/titles).
"""

from datetime import datetime, timedelta
import os
import random
import sys

# Ensure backend root is on sys.path so "app" package can be imported
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app import create_app
from app.extensions import db
from app.models import (
    AttendanceRecord,
    AttendanceSession,
    Assignment,
    Course,
    Enrollment,
    Grade,
    Material,
    Poll,
    PollVote,
    User,
)


DEMO_PASSWORD = "Passw0rd!"


def ensure_user(name, email, role="teacher"):
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name=name, email=email, role=role)
        user.set_password(DEMO_PASSWORD)
        db.session.add(user)
    else:
        user.name = name
        user.role = role
        user.set_password(DEMO_PASSWORD)
    return user


def ensure_course(name, code, owner, term=None, description=None):
    course = Course.query.filter_by(code=code).first()
    if not course:
        course = Course(name=name, code=code, owner_id=owner.id, term=term, description=description)
        db.session.add(course)
    else:
        course.name = name
        course.term = term
        course.description = description
        course.owner_id = owner.id
    return course


def ensure_enrollment(course, user, role_in_course="student", status="active"):
    enrollment = Enrollment.query.filter_by(course_id=course.id, user_id=user.id).first()
    if not enrollment:
        enrollment = Enrollment(course_id=course.id, user_id=user.id, role_in_course=role_in_course, status=status)
        db.session.add(enrollment)
    else:
        enrollment.role_in_course = role_in_course
        enrollment.status = status
    return enrollment


def ensure_material(course, uploader, title, filename, description="", tags=None, size=None):
    material = Material.query.filter_by(course_id=course.id, title=title).first()
    if not material:
        material = Material(course_id=course.id, title=title, uploader_id=uploader.id)
        db.session.add(material)
    material.description = description
    material.tags = tags or []
    material.file_type = os.path.splitext(filename)[1].lstrip(".")
    material.size = size or 0
    material.path = f"/api/uploads/{filename}"
    return material


def ensure_file(upload_dir, filename, content):
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, filename)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    return path


def ensure_attendance(course, title, start_at, mode="qrcode", status="open"):
    session = AttendanceSession.query.filter_by(course_id=course.id, title=title).first()
    if not session:
        session = AttendanceSession(course_id=course.id, title=title)
        db.session.add(session)
    session.mode = mode
    session.start_at = start_at
    session.status = status
    return session


def reset_records_for_session(session):
    AttendanceRecord.query.filter_by(session_id=session.id).delete(synchronize_session=False)


def ensure_assignment(course, title, due_at=None, full_score=100, weight=1.0, type_=None):
    assignment = Assignment.query.filter_by(course_id=course.id, title=title).first()
    if not assignment:
        assignment = Assignment(course_id=course.id, title=title)
        db.session.add(assignment)
    assignment.due_at = due_at
    assignment.full_score = full_score
    assignment.weight = weight
    assignment.type = type_
    return assignment


def reset_grades_for_assignment(assignment):
    Grade.query.filter_by(assignment_id=assignment.id).delete(synchronize_session=False)


def ensure_poll(course, question, options):
    poll = Poll.query.filter_by(course_id=course.id, question=question).first()
    if not poll:
        poll = Poll(course_id=course.id, question=question)
        db.session.add(poll)
    poll.options = options
    poll.is_active = True
    return poll


def reset_votes_for_poll(poll):
    PollVote.query.filter_by(poll_id=poll.id).delete(synchronize_session=False)


def seed():
    app = create_app()
    with app.app_context():
        upload_dir = app.config.get("UPLOAD_DIR")

        # Users
        teachers = [
            ensure_user("Alice Zhang", "alice.teacher@example.com", role="teacher"),
            ensure_user("Bob Li", "bob.teacher@example.com", role="teacher"),
        ]
        students = [
            ensure_user("Charlie Chen", "charlie.student@example.com", role="student"),
            ensure_user("Diana Wu", "diana.student@example.com", role="student"),
            ensure_user("Eric Sun", "eric.student@example.com", role="student"),
            ensure_user("Fiona Guo", "fiona.student@example.com", role="student"),
        ]
        db.session.flush()

        # Courses
        course_cs = ensure_course(
            "数据结构与算法",
            "CS101-DEMO",
            owner=teachers[0],
            term="2024 秋",
            description="基础数据结构、排序与查找，含课堂练习与作业。",
        )
        course_psy = ensure_course(
            "教育心理学",
            "EDU201-DEMO",
            owner=teachers[1],
            term="2024 秋",
            description="学习动机、课堂管理与评估方法。",
        )
        course_edtech = ensure_course(
            "现代教育技术",
            "EDU301-DEMO",
            owner=teachers[0],
            term="2024 秋",
            description="教学技术、互动工具与案例分析。",
        )
        db.session.flush()

        # Enrollments
        for stu in students:
            ensure_enrollment(course_cs, stu)
        ensure_enrollment(course_cs, teachers[1], role_in_course="ta")

        for stu in students[:3]:
            ensure_enrollment(course_psy, stu)
        ensure_enrollment(course_psy, teachers[0], role_in_course="ta")

        for stu in students[1:]:
            ensure_enrollment(course_edtech, stu)

        db.session.flush()

        # Demo files
        demo_files = {
            "cs101-syllabus.pdf": "数据结构课程大纲与评分标准。",
            "cs101-lab1.pdf": "实验一：数组与链表练习。",
            "psy-reading.pdf": "教育心理学阅读材料摘要。",
            "edtech-tools.pdf": "现代教育技术工具与案例。",
            "edtech-project.pdf": "课程项目说明与评分细则。",
        }
        for fname, content in demo_files.items():
            ensure_file(upload_dir, fname, content)

        # Materials
        ensure_material(
            course_cs,
            teachers[0],
            "课程大纲",
            "cs101-syllabus.pdf",
            "评分占比、周次安排与作业说明",
            tags=["大纲", "必读"],
            size=24 * 1024,
        )
        ensure_material(
            course_cs,
            teachers[0],
            "实验一：数组与链表",
            "cs101-lab1.pdf",
            "配套示例与提交要求",
            tags=["实验", "链表"],
            size=36 * 1024,
        )
        ensure_material(
            course_psy,
            teachers[1],
            "阅读材料：动机与课堂管理",
            "psy-reading.pdf",
            "下周讨论前阅读",
            tags=["阅读", "课堂管理"],
            size=28 * 1024,
        )
        ensure_material(
            course_edtech,
            teachers[0],
            "教学工具与案例",
            "edtech-tools.pdf",
            "数字化教学工具盘点",
            tags=["工具", "案例"],
            size=41 * 1024,
        )
        ensure_material(
            course_edtech,
            teachers[0],
            "项目说明",
            "edtech-project.pdf",
            "小组项目提交规范",
            tags=["项目", "必读"],
            size=30 * 1024,
        )

        # Attendance
        now = datetime.utcnow()
        sessions = [
            (course_cs, "第1周签到", now - timedelta(days=14), [("Charlie", "present"), ("Diana", "present"), ("Eric", "late"), ("Fiona", "absent")]),
            (course_cs, "第2周签到", now - timedelta(days=7), [("Charlie", "present"), ("Diana", "late"), ("Eric", "present"), ("Fiona", "present")]),
            (course_psy, "课堂签到-1", now - timedelta(days=10), [("Charlie", "present"), ("Diana", "present"), ("Eric", "present")]),
            (course_edtech, "课堂签到-工具介绍", now - timedelta(days=3), [("Diana", "present"), ("Eric", "present"), ("Fiona", "late")]),
        ]
        name_to_user = {u.name.split()[0]: u for u in students}
        for course, title, start_at, status_list in sessions:
            sess = ensure_attendance(course, title, start_at=start_at, mode="qrcode", status="closed")
            db.session.flush()
            reset_records_for_session(sess)
            for stu_first, status in status_list:
                student = name_to_user.get(stu_first)
                if student:
                    db.session.add(
                        AttendanceRecord(
                            session_id=sess.id,
                            student_id=student.id,
                            status=status,
                            evidence="demo",
                        )
                    )

        # Assignments and Grades
        assignments_data = {
            course_cs: [
                ("作业1：数组练习", now - timedelta(days=10)),
                ("作业2：链表与栈", now - timedelta(days=3)),
            ],
            course_psy: [("课堂观察报告", now - timedelta(days=5))],
            course_edtech: [("工具体验报告", now - timedelta(days=2))],
        }
        for course, assigns in assignments_data.items():
            for title, due_at in assigns:
                assignment = ensure_assignment(course, title, due_at=due_at, type_="assignment")
                db.session.flush()
                reset_grades_for_assignment(assignment)
                for stu in students:
                    if Enrollment.query.filter_by(course_id=course.id, user_id=stu.id).first():
                        score = random.choice([96, 88, 82, 75, 68])
                        db.session.add(
                            Grade(
                                assignment_id=assignment.id,
                                student_id=stu.id,
                                score=score,
                                comment="演示数据",
                                graded_at=now - timedelta(days=1),
                            )
                        )

        # Polls and votes
        polls_data = [
            (course_cs, "下次实验想安排什么主题？", ["排序", "哈希表", "图论"]),
            (course_psy, "你更关心的课堂话题是？", ["学习动机", "课堂管理", "评价与反馈"]),
            (course_edtech, "最想尝试的教学工具类型？", ["互动投票", "在线白板", "AI 助教"]),
        ]
        for course, question, options in polls_data:
            poll = ensure_poll(course, question, options)
            db.session.flush()
            reset_votes_for_poll(poll)
            for stu in students:
                if Enrollment.query.filter_by(course_id=course.id, user_id=stu.id).first():
                    option_index = random.randint(0, len(options) - 1)
                    db.session.add(PollVote(poll_id=poll.id, user_id=stu.id, option_index=option_index))

        db.session.commit()
        print("Demo data seeded successfully.")


if __name__ == "__main__":
    seed()
