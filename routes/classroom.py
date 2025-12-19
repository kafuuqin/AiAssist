from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
import cv2
import numpy as np
import os

bp = Blueprint('classroom', __name__, url_prefix='/api/classroom')

# 确保 uploads 目录存在
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp.route('/face-recognition', methods=['POST'])
@jwt_required()
def face_recognition():
    # 实现人脸识别逻辑
    
    if 'image' not in request.files:
        return jsonify({'message': '没有图片文件'}), 400
    
    image_file = request.files['image']
    # 保存上传的图片
    image_path = os.path.join(UPLOAD_FOLDER, 'temp_class_image.jpg')
    image_file.save(image_path)
    
    # 使用 OpenCV 进行人脸检测
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # 读取图片
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 检测人脸
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    # 绘制人脸框
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    
    # 保存带有人脸框的图片
    result_path = os.path.join(UPLOAD_FOLDER, 'result_image.jpg')
    cv2.imwrite(result_path, img)
    
    # 返回检测到的人脸数量和详细信息
    return jsonify({
        'message': '人脸识别完成',
        'face_count': len(faces),
        'detected_faces': [{'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)} for (x, y, w, h) in faces],
        'result_image_url': '/uploads/result_image.jpg'
    }), 200

@bp.route('/seating-chart', methods=['POST'])
@jwt_required()
def generate_seating_chart():
    # 实现座位表生成功能
    # 支持自定义行列数和学生名单
    
    data = request.get_json()
    
    # 获取请求参数，如果未提供则使用默认值
    rows = data.get('rows', 5)
    cols = data.get('cols', 6)
    students = data.get('students', [])
    
    # 创建座位表数据
    seating_data = {
        'rows': rows,
        'cols': cols,
        'seats': []
    }
    
    # 生成座位数据
    student_index = 0
    for row in range(rows):
        for col in range(cols):
            seat = {
                'row': row,
                'col': col,
                'student': None,
                'attended': True  # 默认为已出席
            }
            
            # 如果还有学生未分配，则分配给这个座位
            if student_index < len(students):
                seat['student'] = students[student_index]
                student_index += 1
            
            seating_data['seats'].append(seat)
    
    return jsonify(seating_data), 200