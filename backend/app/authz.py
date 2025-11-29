from flask_jwt_extended import get_jwt_identity

from .models import Course, Enrollment, User
from .utils.responses import error


def ensure_course_member(course_id, as_owner=False, allow_roles=None):
    """
    校验课程权限：
    - admin 全局放行
    - 课程 owner 放行；若 as_owner=True 则必须为 owner（admin 也放行）
    - 若 allow_roles 传入，需满足 enrollment.role_in_course 在允许列表内
    - 否则仅校验是否为课程成员
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    course = Course.query.get(course_id)
    if not course:
        return None, error("course not found", 404)

    # 全局管理员
    if user and user.role == "admin":
        return course, None

    # 课程拥有者
    if course.owner_id == int(user_id):
        return course, None

    member = Enrollment.query.filter_by(course_id=course_id, user_id=user_id).first()
    if not member:
        return None, error("forbidden", 403)

    if allow_roles:
        if member.role_in_course not in allow_roles:
            return None, error("forbidden", 403)
    elif as_owner:
        # 要求拥有者但已不是 owner，也没有允许角色
        return None, error("forbidden", 403)

    return course, None
