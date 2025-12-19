from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Attendance, db

bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')

@bp.route('/tasks', methods=['POST'])
@bp.route('/tasks/', methods=['POST'])
@jwt_required()
def create_attendance_task():
    data = request.get_json()
    
    attendance = Attendance(
        title=data['title'],
        course_id=data['course_id'],
        teacher_id=data['teacher_id']
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    return jsonify({'message': '考勤任务创建成功', 'attendance': attendance.to_dict()}), 201

@bp.route('/tasks', methods=['GET'])
@bp.route('/tasks/', methods=['GET'])
@jwt_required()
def get_attendance_tasks():
    attendances = Attendance.query.all()
    return jsonify([attendance.to_dict() for attendance in attendances]), 200

@bp.route('/tasks/<int:id>/submit', methods=['POST'])
@bp.route('/tasks/<int:id>/submit/', methods=['POST'])
@jwt_required()
def submit_attendance(id):
    data = request.get_json()
    attendance = Attendance.query.get_or_404(id)
    
    # 这里应该有更复杂的逻辑来处理学生的考勤提交
    # 比如检查学生是否已经提交过，验证学生身份等
    
    # 更新考勤记录
    if not attendance.submitted_students:
        attendance.submitted_students = []
    
    attendance.submitted_students.append(data['student_id'])
    db.session.commit()
    
    return jsonify({'message': '考勤提交成功'}), 200

@bp.route('/', methods=['POST'])
@bp.route('/<path:subpath>/', methods=['POST'])
@jwt_required()
def add_attendance(subpath=None):
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    status = data.get('status', 'present')  # 默认为出席
    
    # 创建新的考勤记录
    attendance = Attendance(student_id=student_id, course_id=course_id, status=status)
    db.session.add(attendance)
    db.session.commit()
    
    return jsonify({'message': '考勤记录添加成功', 'attendance': attendance.to_dict()}), 201

@bp.route('/', methods=['GET'])
@bp.route('/<path:subpath>/', methods=['GET'])
@jwt_required()
def get_attendance_records(subpath=None):
    # 获取所有考勤记录
    records = Attendance.query.all()
    return jsonify([record.to_dict() for record in records]), 200

@bp.route('/<int:id>', methods=['PUT'])
@bp.route('/<int:id>/', methods=['PUT'])
@jwt_required()
def update_attendance(id):
    data = request.get_json()
    attendance = Attendance.query.get_or_404(id)
    
    # 更新考勤状态
    attendance.status = data.get('status', attendance.status)
    db.session.commit()
    
    return jsonify({'message': '考勤记录更新成功', 'attendance': attendance.to_dict()}), 200

@bp.route('/<int:id>', methods=['DELETE'])
@bp.route('/<int:id>/', methods=['DELETE'])
@jwt_required()
def delete_attendance(id):
    attendance = Attendance.query.get_or_404(id)
    db.session.delete(attendance)
    db.session.commit()
    
    return jsonify({'message': '考勤记录删除成功'}), 200