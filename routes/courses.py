from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Course, CourseEnrollment, User
import traceback
import sys

bp = Blueprint('courses', __name__, url_prefix='/api/courses')

@bp.route('/', methods=['POST'])
@jwt_required()
def create_course():
    """创建课程"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 检查用户是否为教师
        teacher = User.query.get(current_user_id)
        if not teacher or teacher.role != 'teacher':
            return jsonify({'message': '只有教师可以创建课程'}), 403
        
        # 创建课程
        course = Course(
            name=data.get('name'),
            description=data.get('description'),
            teacher_id=current_user_id
        )
        
        db.session.add(course)
        db.session.commit()
        
        return jsonify({
            'message': '课程创建成功',
            'course': course.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"创建课程时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'创建课程失败: {str(e)}'}), 500

@bp.route('/', methods=['GET'])
@jwt_required()
def get_courses():
    """获取课程列表"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        if user.role == 'teacher':
            # 教师获取自己创建的课程
            courses = Course.query.filter_by(teacher_id=current_user_id).all()
        else:
            # 学生获取自己加入的课程
            enrollments = CourseEnrollment.query.filter_by(student_id=current_user_id).all()
            course_ids = [e.course_id for e in enrollments]
            courses = Course.query.filter(Course.id.in_(course_ids)).all()
        
        return jsonify([course.to_dict() for course in courses]), 200
    except Exception as e:
        print(f"获取课程列表时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'获取课程列表失败: {str(e)}'}), 500

@bp.route('/<int:course_id>/', methods=['GET'])
@jwt_required()
def get_course(course_id):
    """获取课程详情"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        course = Course.query.get_or_404(course_id)
        
        # 检查权限（教师本人或已加入课程的学生）
        if user.role == 'student':
            enrollment = CourseEnrollment.query.filter_by(
                course_id=course_id, 
                student_id=current_user_id
            ).first()
            if not enrollment:
                return jsonify({'message': '您没有权限查看此课程'}), 403
        
        result = course.to_dict()
        
        # 添加教师信息
        result['teacher_name'] = course.teacher.username if course.teacher else None
        
        return jsonify(result), 200
    except Exception as e:
        print(f"获取课程详情时发生错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': f'获取课程详情失败: {str(e)}'}), 500

@bp.route('/<int:course_id>/students/', methods=['GET'])
@jwt_required()
def get_course_students(course_id):
    """获取课程学生列表"""
    try:
        current_user_id = get_jwt_identity()
        print(f"获取课程学生列表 - 当前用户ID: {current_user_id}, 课程ID: {course_id}")
        
        user = User.query.get(current_user_id)
        print(f"当前用户信息: {user}")
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        course = Course.query.get_or_404(course_id)
        print(f"课程信息: {course}")
        print(f"课程教师ID: {course.teacher_id}")
        
        # 检查权限（只有教师本人可以查看）
        print(f"用户角色: {user.role}, 是否为教师: {user.role == 'teacher'}")
        print(f"课程教师ID: {course.teacher_id}, 当前用户ID: {current_user_id}, 是否匹配: {course.teacher_id == current_user_id}")
        
        if user.role != 'teacher' or course.teacher_id != current_user_id:
            return jsonify({'message': '只有课程教师可以查看学生列表'}), 403
        
        # 获取学生列表
        enrollments = CourseEnrollment.query.filter_by(course_id=course_id).all()
        students = [enrollment.to_dict() for enrollment in enrollments]
        
        return jsonify(students), 200
    except Exception as e:
        print(f"获取课程学生列表时发生错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': f'获取课程学生列表失败: {str(e)}'}), 500

@bp.route('/<int:course_id>/students/', methods=['POST'])
@jwt_required()
def add_student_to_course(course_id):
    """添加学生到课程"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        course = Course.query.get_or_404(course_id)
        
        # 检查权限（只有教师本人可以添加学生）
        if user.role != 'teacher' or course.teacher_id != current_user_id:
            return jsonify({'message': '只有课程教师可以添加学生'}), 403
        
        data = request.get_json()
        student_id = data.get('student_id')
        
        # 检查学生是否存在且角色为学生
        student = User.query.get(student_id)
        if not student or student.role != 'student':
            return jsonify({'message': '学生不存在或角色不正确'}), 400
        
        # 检查学生是否已在课程中
        existing_enrollment = CourseEnrollment.query.filter_by(
            course_id=course_id,
            student_id=student_id
        ).first()
        
        if existing_enrollment:
            return jsonify({'message': '学生已在课程中'}), 400
        
        # 添加学生到课程
        enrollment = CourseEnrollment(
            course_id=course_id,
            student_id=student_id
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        # 获取学生信息
        student = User.query.get(student_id)
        
        return jsonify({
            'message': '学生添加成功',
            'enrollment': {
                'id': enrollment.id,
                'course_id': enrollment.course_id,
                'student_id': enrollment.student_id,
                'student_name': student.username if student else '未知学生',
                'enrolled_at': enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"添加学生到课程时发生错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': f'添加学生到课程失败: {str(e)}'}), 500

@bp.route('/<int:course_id>/students/<int:student_id>/', methods=['DELETE'])
@jwt_required()
def remove_student_from_course(course_id, student_id):
    """从课程中移除学生"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        course = Course.query.get_or_404(course_id)
        
        # 检查权限（只有教师本人可以移除学生）
        if user.role != 'teacher' or course.teacher_id != current_user_id:
            return jsonify({'message': '只有课程教师可以移除学生'}), 403
        
        # 查找并删除学生的选课记录
        enrollment = CourseEnrollment.query.filter_by(
            course_id=course_id,
            student_id=student_id
        ).first_or_404()
        
        db.session.delete(enrollment)
        db.session.commit()
        
        return jsonify({'message': '学生移除成功'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"从课程中移除学生时发生错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': f'从课程中移除学生失败: {str(e)}'}), 500

@bp.route('/<int:course_id>/enroll/', methods=['POST'])
@jwt_required()
def enroll_in_course(course_id):
    """学生加入课程"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        # 检查用户是否为学生
        if user.role != 'student':
            return jsonify({'message': '只有学生可以加入课程'}), 403
        
        course = Course.query.get_or_404(course_id)
        
        # 检查是否已加入课程
        existing_enrollment = CourseEnrollment.query.filter_by(
            course_id=course_id,
            student_id=current_user_id
        ).first()
        
        if existing_enrollment:
            return jsonify({'message': '您已加入此课程'}), 400
        
        # 加入课程
        enrollment = CourseEnrollment(
            course_id=course_id,
            student_id=current_user_id
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({
            'message': '课程加入成功',
            'enrollment': enrollment.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"学生加入课程时发生错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': f'学生加入课程失败: {str(e)}'}), 500