from app import create_app
from models import User, Course, CourseEnrollment

app = create_app()

with app.app_context():
    # 检查所有用户
    users = User.query.all()
    print("=== 所有用户 ===")
    for user in users:
        print(f"ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}, 角色: {user.role}")
    
    print("\n=== 所有课程 ===")
    courses = Course.query.all()
    for course in courses:
        print(f"ID: {course.id}, 名称: {course.name}, 教师ID: {course.teacher_id}")
        # 查找教师姓名
        teacher = User.query.get(course.teacher_id)
        if teacher:
            print(f"  教师: {teacher.username}")
        else:
            print("  教师: 未找到")
    
    print("\n=== 课程选课情况 ===")
    enrollments = CourseEnrollment.query.all()
    for enrollment in enrollments:
        student = User.query.get(enrollment.student_id)
        course = Course.query.get(enrollment.course_id)
        print(f"学生: {student.username if student else '未知'} -> 课程: {course.name if course else '未知'}")