from datetime import datetime

from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from ..extensions import db
from ..models import (
    Assignment,
    AttendanceRecord,
    AttendanceSession,
    Course,
    Grade,
    Enrollment,
    Material,
    Poll,
    PollVote,
    User,
)
from ..authz import ensure_course_member
from ..utils.responses import error, ok
from sqlalchemy import or_
from ..utils.exporter import grades_to_csv

courses_bp = Blueprint("courses", __name__, url_prefix="/courses")


def _json():
    return request.get_json(silent=True) or {}


@courses_bp.get("")
@jwt_required()
def list_courses():
    user_id = int(get_jwt_identity())
    # 作为拥有者或选课成员的课程
    owned = Course.query.filter_by(owner_id=user_id)
    member_course_ids = [e.course_id for e in Enrollment.query.filter_by(user_id=user_id).all()]
    member_courses = Course.query.filter(Course.id.in_(member_course_ids)) if member_course_ids else []
    courses = list(owned) + list(member_courses)
    # 去重
    unique = {c.id: c for c in courses}.values()
    return ok([c.to_dict() for c in unique])


@courses_bp.get("/<int:course_id>/members")
@jwt_required()
def list_members(course_id):
    _, err = ensure_course_member(course_id)
    if err:
        return err
    enrollments = (
        db.session.query(Enrollment, User)
        .join(User, User.id == Enrollment.user_id)
        .filter(Enrollment.course_id == course_id)
        .all()
    )
    payload = []
    for en, user in enrollments:
        payload.append(
            {
                "id": en.id,
                "course_id": en.course_id,
                "user_id": en.user_id,
                "role_in_course": en.role_in_course,
                "status": en.status,
                "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role},
            }
        )
    return ok(payload)


@courses_bp.post("/<int:course_id>/members")
@jwt_required()
def add_member(course_id):
    _, err = ensure_course_member(course_id, as_owner=True)
    if err:
        return err
    data = _json()
    user_id = data.get("user_id")
    role_in_course = data.get("role_in_course") or "student"
    if not user_id:
        return error("user_id required")
    if not User.query.get(user_id):
        return error("user not found", 404)
    exists = Enrollment.query.filter_by(course_id=course_id, user_id=user_id).first()
    if exists:
        return error("already enrolled")
    enrollment = Enrollment(course_id=course_id, user_id=user_id, role_in_course=role_in_course)
    db.session.add(enrollment)
    db.session.commit()
    return ok(enrollment.to_dict(), 201)


@courses_bp.patch("/<int:course_id>/members/<int:member_id>")
@jwt_required()
def update_member(course_id, member_id):
    _, err = ensure_course_member(course_id, as_owner=True)
    if err:
        return err
    data = _json()
    role_in_course = data.get("role_in_course")
    status = data.get("status")
    enrollment = Enrollment.query.filter_by(id=member_id, course_id=course_id).first()
    if not enrollment:
        return error("member not found", 404)
    if role_in_course:
        enrollment.role_in_course = role_in_course
    if status:
        enrollment.status = status
    db.session.commit()
    return ok(enrollment.to_dict())


@courses_bp.delete("/<int:course_id>/members/<int:member_id>")
@jwt_required()
def delete_member(course_id, member_id):
    course, err = ensure_course_member(course_id, as_owner=True)
    if err:
        return err
    enrollment = Enrollment.query.filter_by(id=member_id, course_id=course_id).first()
    if not enrollment:
        return error("member not found", 404)
    # 保护拥有者
    if enrollment.user_id == course.owner_id:
        return error("cannot remove course owner", 403)
    db.session.delete(enrollment)
    db.session.commit()
    return ok({"deleted": member_id})


@courses_bp.post("")
@jwt_required()
def create_course():
    data = _json()
    name = data.get("name")
    code = data.get("code")
    term = data.get("term")
    description = data.get("description")
    owner_id = int(get_jwt_identity())
    member_ids = data.get("members") or []

    if not name or not code:
        return error("name and code required")

    if Course.query.filter_by(code=code).first():
        return error("course code exists")

    course = Course(name=name, code=code, term=term, description=description, owner_id=owner_id)
    db.session.add(course)
    db.session.flush()
    # 添加成员
    for uid in member_ids:
        enrollment = Enrollment(course_id=course.id, user_id=uid, role_in_course="student")
        db.session.add(enrollment)
    db.session.commit()
    return ok(course.to_dict(), 201)


@courses_bp.get("/<int:course_id>/materials")
@jwt_required()
def list_materials(course_id):
    _, err = ensure_course_member(course_id)
    if err:
        return err
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 10)), 1), 100)
    q = (request.args.get("q") or "").strip()
    tags = [t.strip() for t in (request.args.get("tags") or "").split(",") if t.strip()]
    sort = request.args.get("sort") or "-created_at"

    query = Material.query.filter_by(course_id=course_id)
    if q:
        query = query.filter(or_(Material.title.ilike(f"%{q}%"), Material.description.ilike(f"%{q}%")))
    if tags:
        for t in tags:
            query = query.filter(Material.tags.contains([t]))

    if sort == "created_at":
        query = query.order_by(Material.created_at.asc())
    else:
        query = query.order_by(Material.created_at.desc())
    items = query.limit(page_size).offset((page - 1) * page_size).all()
    total = db.session.query(func.count(Material.id)).filter_by(course_id=course_id).scalar()
    return ok({"items": [m.to_dict() for m in items], "total": total, "page": page, "page_size": page_size})


@courses_bp.post("/<int:course_id>/materials")
@jwt_required()
def create_material(course_id):
    _, err = ensure_course_member(course_id)
    if err:
        return err
    data = _json()
    title = data.get("title")
    if not title:
        return error("title required")
    user_id = int(get_jwt_identity())
    mat = Material(
        course_id=course_id,
        title=title,
        description=data.get("description"),
        path=data.get("path"),
        file_type=data.get("file_type"),
        size=data.get("size") or 0,
        tags=data.get("tags") or [],
        uploader_id=user_id,
    )
    db.session.add(mat)
    db.session.commit()
    return ok(mat.to_dict(), 201)


@courses_bp.get("/<int:course_id>/attendance")
@jwt_required()
def list_attendance(course_id):
    _, err = ensure_course_member(course_id)
    if err:
        return err
    sessions = AttendanceSession.query.filter_by(course_id=course_id).order_by(
        AttendanceSession.start_at.desc()
    )
    return ok([s.to_dict() for s in sessions])


@courses_bp.post("/<int:course_id>/attendance")
@jwt_required()
def create_attendance(course_id):
    _, err = ensure_course_member(course_id)
    if err:
        return err
    data = _json()
    title = data.get("title") or "课堂签到"
    mode = data.get("mode") or "qrcode"
    gesture_pattern = data.get("gesture_pattern")
    
    # 如果是手势模式，必须提供手势图案
    if mode == "gesture" and not gesture_pattern:
        return error("手势模式必须提供手势图案", 400)
    
    session = AttendanceSession(
        course_id=course_id,
        title=title,
        mode=mode,
        gesture_pattern=gesture_pattern,  # 新增：存储手势图案
        start_at=datetime.utcnow(),
        status="open",
    )
    db.session.add(session)
    db.session.commit()
    return ok(session.to_dict(), 201)


@courses_bp.get("/<int:course_id>/attendance/<int:session_id>")
@jwt_required()
def attendance_detail(course_id, session_id):
    _, err = ensure_course_member(course_id)
    if err:
        return err
    session = AttendanceSession.query.filter_by(id=session_id, course_id=course_id).first()
    if not session:
        return error("session not found", 404)
    records = AttendanceRecord.query.filter_by(session_id=session_id).all()
    return ok({"session": session.to_dict(), "records": [r.to_dict() for r in records]})


@courses_bp.post("/<int:course_id>/attendance/<int:session_id>/record")
@jwt_required()
def add_attendance_record(course_id, session_id):
    _, err = ensure_course_member(course_id)
    if err:
        return err
    data = _json()
    student_id = data.get("student_id")
    status = data.get("status") or "present"
    if not student_id:
        return error("student_id required")
    session = AttendanceSession.query.filter_by(id=session_id, course_id=course_id).first()
    if not session:
        return error("session not found", 404)
    record = AttendanceRecord(
        session_id=session_id,
        student_id=student_id,
        status=status,
        evidence=data.get("evidence"),
        recognized_face_id=data.get("recognized_face_id"),
    )
    db.session.add(record)
    db.session.commit()
    return ok(record.to_dict(), 201)


@courses_bp.get("/<int:course_id>/grades")
@jwt_required()
def list_grades(course_id):
    _, err = ensure_course_member(course_id)
    if err:
        return err
    export = request.args.get("export")
    assignment_filter = request.args.get("assignment_id")
    grades = (
        db.session.query(Grade)
        .join(Grade.assignment)
.filter_by(course_id=course_id)
    )
    if assignment_filter:
        grades = grades.filter(Grade.assignment_id == assignment_filter)
    grades = grades.order_by(Grade.graded_at.desc()).all()
    if export == "csv":
        csv_data = grades_to_csv(grades)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename=grades_course_{course_id}.csv"},
        )
    return ok([g.to_dict() for g in grades])


@courses_bp.get("/<int:course_id>/assignments")
@jwt_required()
def list_assignments(course_id):
    _, err = ensure_course_member(course_id)
    if err:
        return err
    assignments = Assignment.query.filter_by(course_id=course_id).order_by(Assignment.created_at.desc()).all()
    return ok([a.to_dict() for a in assignments])


@courses_bp.get("/<int:course_id>/grades/template")
@jwt_required()
def grade_template(course_id):
    _, err = ensure_course_member(course_id)
    if err:
        return err
    content = "student_id,score,comment\nS001,95,示例评语\nS002,88,\n"
    return Response(
        content,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=grades_template_course_{course_id}.csv"},
    )


@courses_bp.post("/<int:course_id>/assignments")
@jwt_required()
def create_assignment(course_id):
    _, err = ensure_course_member(course_id, as_owner=True)
    if err:
        return err
    data = _json()
    title = data.get("title")
    if not title:
        return error("title required")
    assignment = Assignment(
        course_id=course_id,
        title=title,
        type=data.get("type"),
        weight=data.get("weight") or 1.0,
        full_score=data.get("full_score") or 100.0,
        due_at=datetime.fromisoformat(data["due_at"]) if data.get("due_at") else None,
    )
    db.session.add(assignment)
    db.session.commit()
    return ok(assignment.to_dict(), 201)


@courses_bp.post("/<int:course_id>/assignments/<int:assignment_id>/grades")
@jwt_required()
def create_grade(course_id, assignment_id):
    _, err = ensure_course_member(course_id)
    if err:
        return err
    data = _json()
    student_id = data.get("student_id")
    score = data.get("score")
    if student_id is None or score is None:
        return error("student_id and score required")
    assignment = Assignment.query.filter_by(id=assignment_id, course_id=course_id).first()
    if not assignment:
        return error("assignment not found", 404)
    grade = Grade(
        assignment_id=assignment_id,
        student_id=student_id,
        score=score,
        comment=data.get("comment"),
        graded_at=datetime.fromisoformat(data["graded_at"]) if data.get("graded_at") else datetime.utcnow(),
    )
    db.session.add(grade)
    db.session.commit()
    return ok(grade.to_dict(), 201)


@courses_bp.get("/<int:course_id>/grades/stats")
@jwt_required()
def grade_stats(course_id):
    _, err = ensure_course_member(course_id)
    if err:
        return err
    # 简易统计，未来可用 Pandas 替换
    grades = (
        db.session.query(Grade.score)
        .join(Grade.assignment)
        .filter_by(course_id=course_id)
        .all()
    )
    scores = [g.score for g in grades]
    if not scores:
        return ok({"avg": None, "max": None, "min": None, "count": 0, "std": None})
    avg = sum(scores) / len(scores)
    variance = sum((s - avg) ** 2 for s in scores) / len(scores)
    std = variance**0.5
    return ok(
        {
            "avg": avg,
            "max": max(scores),
            "min": min(scores),
            "std": std,
            "count": len(scores),
        }
    )


@courses_bp.get("/<int:course_id>/polls")
@jwt_required()
def list_polls(course_id):
    _, err = ensure_course_member(course_id)
    if err:
        return err
    polls = Poll.query.filter_by(course_id=course_id).order_by(Poll.created_at.desc()).all()
    payload = []
    for p in polls:
        votes = [v.option_index for v in p.votes]
        totals = []
        if p.options:
            for idx in range(len(p.options)):
                totals.append(votes.count(idx))
        payload.append({**p.to_dict(), "votes": totals})
    return ok(payload)


@courses_bp.post("/<int:course_id>/polls")
@jwt_required()
def create_poll(course_id):
    _, err = ensure_course_member(course_id)
    if err:
        return err
    data = _json()
    question = data.get("question")
    options = data.get("options") or []
    if not question or len(options) < 2:
        return error("question and at least 2 options required")
    poll = Poll(course_id=course_id, question=question, options=options, is_active=True)
    db.session.add(poll)
    db.session.commit()
    return ok(poll.to_dict(), 201)


@courses_bp.post("/<int:course_id>/polls/<int:poll_id>/vote")
@jwt_required()
def vote_poll(course_id, poll_id):
    _, err = ensure_course_member(course_id)
    if err:
        return err
    data = _json()
    option_index = data.get("option_index")
    if option_index is None:
        return error("option_index required")
    poll = Poll.query.filter_by(id=poll_id, course_id=course_id).first()
    if not poll:
        return error("poll not found", 404)
    vote = PollVote(poll_id=poll.id, user_id=int(get_jwt_identity()), option_index=option_index)
    db.session.add(vote)
    db.session.commit()
    return ok(vote.to_dict(), 201)


@courses_bp.get("/<int:course_id>/student/dashboard")
@jwt_required()
def student_dashboard(course_id):
    """学生仪表板数据"""
    _, err = ensure_course_member(course_id, allow_roles=["student"])
    if err:
        return err
    
    user_id = int(get_jwt_identity())
    
    # 获取学生基本信息
    student = User.query.get(user_id)
    
    # 获取课程信息
    course = Course.query.get(course_id)
    
    # 计算平均成绩
    avg_score = db.session.query(db.func.avg(Grade.score)).join(Assignment).filter(
        Assignment.course_id == course_id,
        Grade.student_id == user_id
    ).scalar()
    
    # 获取待完成作业数量
    pending_assignments = db.session.query(Assignment).filter(
        Assignment.course_id == course_id,
        ~db.session.query(Grade).filter(
            Grade.assignment_id == Assignment.id,
            Grade.student_id == user_id
        ).exists()
    ).count()
    
    # 计算出勤率
    total_sessions = AttendanceSession.query.filter_by(course_id=course_id).count()
    attended_sessions = db.session.query(AttendanceRecord).join(AttendanceSession).filter(
        AttendanceSession.course_id == course_id,
        AttendanceRecord.student_id == user_id,
        AttendanceRecord.status == "present"
    ).count()
    
    attendance_rate = (attended_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    # 获取最近活动
    recent_activities = []
    
    # 最近材料
    recent_materials = Material.query.filter_by(course_id=course_id).order_by(
        Material.created_at.desc()
    ).limit(3).all()
    for material in recent_materials:
        recent_activities.append({
            "type": "material",
            "title": f"新资料: {material.title}",
            "created_at": material.created_at
        })
    
    # 最近作业
    recent_assignments = Assignment.query.filter_by(course_id=course_id).order_by(
        Assignment.created_at.desc()
    ).limit(3).all()
    for assignment in recent_assignments:
        recent_activities.append({
            "type": "assignment",
            "title": f"新作业: {assignment.title}",
            "created_at": assignment.created_at
        })
    
    # 按时间排序
    recent_activities.sort(key=lambda x: x["created_at"], reverse=True)
    recent_activities = recent_activities[:5]  # 只取最近5个
    return ok({
        "student": student.to_dict(),
        "course": course.to_dict(),
        "avg_score": round(avg_score, 2) if avg_score else None,
        "pending_assignments": pending_assignments,
        "attendance_rate": round(attendance_rate, 2),
        "recent_activities": recent_activities
    })


@courses_bp.get("/<int:course_id>/student/materials")
@jwt_required()
def student_materials(course_id):
    """学生资料列表"""
    _, err = ensure_course_member(course_id, allow_roles=["student"])
    if err:
        return err
    
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 10)), 1), 100)
    q = (request.args.get("q") or "").strip()
    
    query = Material.query.filter_by(course_id=course_id)
    if q:
        query = query.filter(db.or_(
            Material.title.ilike(f"%{q}%"),
            Material.description.ilike(f"%{q}%")
        ))
    
    query = query.order_by(Material.created_at.desc())
    items = query.limit(page_size).offset((page - 1) * page_size).all()
    total = db.session.query(db.func.count(Material.id)).filter_by(course_id=course_id).scalar()
    
    return ok({
        "items": [m.to_dict() for m in items],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@courses_bp.get("/<int:course_id>/student/attendance")
@jwt_required()
def student_attendance(course_id):
    """学生考勤记录"""
    _, err = ensure_course_member(course_id, allow_roles=["student"])
    if err:
        return err
    
    user_id = int(get_jwt_identity())
    
    # 获取所有考勤会话
    sessions = AttendanceSession.query.filter_by(course_id=course_id).order_by(
        AttendanceSession.start_at.desc()
    ).all()
    
    attendance_records = []
    for session in sessions:
        record = AttendanceRecord.query.filter_by(
            session_id=session.id,
            student_id=user_id
        ).first()
        
        attendance_records.append({
            "session": session.to_dict(),
            "record": record.to_dict() if record else None,
            "status": record.status if record else "absent"
        })
    
    return ok(attendance_records)


@courses_bp.post("/<int:course_id>/student/attendance/<int:session_id>/checkin")
@jwt_required()
def student_checkin(course_id, session_id):
    """学生签到"""
    _, err = ensure_course_member(course_id, allow_roles=["student"])
    if err:
        return err
    
    user_id = int(get_jwt_identity())
    data = _json()
    
    # 检查会话是否存在
    session = AttendanceSession.query.filter_by(id=session_id, course_id=course_id).first()
    if not session:
        return error("考勤会话不存在", 404)
    
    # 检查是否已经签到
    existing_record = AttendanceRecord.query.filter_by(
        session_id=session_id,
        student_id=user_id
    ).first()
    
    if existing_record:
        return error("已经签到过", 400)
    
    # 创建签到记录
    record = AttendanceRecord(
        session_id=session_id,
        student_id=user_id,
        status="present",
        evidence=data.get("evidence"),
        recognized_face_id=data.get("recognized_face_id"),
    )
    
    db.session.add(record)
    db.session.commit()
    
    return ok(record.to_dict(), 201)


@courses_bp.get("/<int:course_id>/student/grades")
@jwt_required()
def student_grades(course_id):
    """学生成绩查询"""
    _, err = ensure_course_member(course_id, allow_roles=["student"])
    if err:
        return err
    
    user_id = int(get_jwt_identity())
    
    grades = db.session.query(Grade).join(Assignment).filter(
        Assignment.course_id == course_id,
        Grade.student_id == user_id
    ).order_by(Grade.graded_at.desc()).all()
    
    return ok([g.to_dict() for g in grades])


@courses_bp.get("/<int:course_id>/student/assignments")
@jwt_required()
def student_assignments(course_id):
    """学生作业列表"""
    _, err = ensure_course_member(course_id, allow_roles=["student"])
    if err:
        return err
    
    user_id = int(get_jwt_identity())
    
    assignments = Assignment.query.filter_by(course_id=course_id).order_by(
        Assignment.created_at.desc()
    ).all()
    
    assignments_with_status = []
    for assignment in assignments:
        grade = Grade.query.filter_by(
            assignment_id=assignment.id,
            student_id=user_id
        ).first()
        
        assignments_with_status.append({
            **assignment.to_dict(),
            "submitted": grade is not None,
            "score": grade.score if grade else None,
            "graded_at": grade.graded_at if grade else None
        })
    
    return ok(assignments_with_status)


@courses_bp.get("/<int:course_id>/student/polls")
@jwt_required()
def student_polls(course_id):
    """学生投票列表"""
    _, err = ensure_course_member(course_id, allow_roles=["student"])
    if err:
        return err
    
    user_id = int(get_jwt_identity())
    
    polls = Poll.query.filter_by(course_id=course_id).order_by(
        Poll.created_at.desc()
    ).all()
    
    polls_with_vote = []
    for poll in polls:
        user_vote = PollVote.query.filter_by(
            poll_id=poll.id,
            user_id=user_id
        ).first()
        
        # 计算投票统计
        votes = [v.option_index for v in poll.votes]
        totals = []
        if poll.options:
            for idx in range(len(poll.options)):
                totals.append(votes.count(idx))
        
        polls_with_vote.append({
            **poll.to_dict(),
            "user_vote": user_vote.option_index if user_vote else None,
            "votes": totals
        })
    
    return ok(polls_with_vote)


@courses_bp.post("/<int:course_id>/student/polls/<int:poll_id>/vote")
@jwt_required()
def student_vote(course_id, poll_id):
    """学生投票"""
    _, err = ensure_course_member(course_id, allow_roles=["student"])
    if err:
        return err
    
    user_id = int(get_jwt_identity())
    data = _json()
    option_index = data.get("option_index")
    
    if option_index is None:
        return error("option_index required")
    
    poll = Poll.query.filter_by(id=poll_id, course_id=course_id).first()
    if not poll:
        return error("投票不存在", 404)
    
    # 检查是否已经投票
    existing_vote = PollVote.query.filter_by(poll_id=poll_id, user_id=user_id).first()
    if existing_vote:
        return error("已经投过票了", 400)
    
    # 检查选项索引是否有效
    if option_index < 0 or option_index >= len(poll.options):
        return error("无效的选项", 400)
    
    vote = PollVote(poll_id=poll_id, user_id=user_id, option_index=option_index)
    db.session.add(vote)
    db.session.commit()
    
    return ok(vote.to_dict(), 201)


@courses_bp.get("/<int:course_id>/student/interactions")
@jwt_required()
def student_interactions(course_id):
    """学生课堂互动数据"""
    _, err = ensure_course_member(course_id, allow_roles=["student"])
    if err:
        return err
    
    user_id = int(get_jwt_identity())
    
    # 获取学生的投票记录
    votes = PollVote.query.join(Poll).filter(
        Poll.course_id == course_id,
        PollVote.user_id == user_id
    ).all()
    
    # 获取学生的考勤记录
    attendance_records = db.session.query(AttendanceRecord).join(AttendanceSession).filter(
        AttendanceSession.course_id == course_id,
        AttendanceRecord.student_id == user_id
    ).all()
    
    return ok({
        "votes": [v.to_dict() for v in votes],
        "attendance": [r.to_dict() for r in attendance_records]
    })


@courses_bp.get("/student/courses")
@jwt_required()
def student_courses():
    """学生课程列表"""
    user_id = int(get_jwt_identity())
    
    # 获取学生选课的课程
    enrollments = Enrollment.query.filter_by(
        user_id=user_id,
        role_in_course="student"
    ).all()
    
    courses = []
    for enrollment in enrollments:
        course = Course.query.get(enrollment.course_id)
        if course:
            courses.append(course.to_dict())
    
    return ok(courses)