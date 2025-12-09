from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Grade, db
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import io
import os
from werkzeug.utils import secure_filename

bp = Blueprint('grades', __name__, url_prefix='/api/grades')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_grades():
    # 获取查询参数
    student_id = request.args.get('student_id', type=int)
    subject = request.args.get('subject', type=str)
    
    # 构造查询
    query = Grade.query
    
    if student_id:
        query = query.filter_by(student_id=student_id)
    
    if subject:
        query = query.filter_by(subject=subject)
    
    # 执行查询
    grades = query.all()
    
    return jsonify([grade.to_dict() for grade in grades]), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def add_grade():
    data = request.get_json()
    student_id = data.get('student_id')
    subject = data.get('subject')
    score = data.get('score')
    
    # 创建新成绩记录
    grade = Grade(student_id=student_id, subject=subject, score=score)
    db.session.add(grade)
    db.session.commit()
    
    return jsonify({'message': '成绩添加成功', 'grade': grade.to_dict()}), 201

@bp.route('/batch', methods=['POST'])
@bp.route('/batch/', methods=['POST'])
@jwt_required()
def batch_import_grades():
    try:
        # 处理文件上传
        if 'file' not in request.files:
            return jsonify({'message': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': '没有选择文件'}), 400
        
        print(f"接收到文件: {file.filename}")
        
        # 读取文件内容
        filename = secure_filename(file.filename)
        _, ext = os.path.splitext(filename)
        
        if ext.lower() in ['.xlsx', '.xls']:
            # 读取Excel文件
            df = pd.read_excel(file)
            print(f"读取Excel文件，列名: {list(df.columns)}")
        elif ext.lower() == '.csv':
            # 读取CSV文件
            df = pd.read_csv(file)
            print(f"读取CSV文件，列名: {list(df.columns)}")
        else:
            return jsonify({'message': '不支持的文件格式'}), 400
        
        # 检查必要的列是否存在（支持中英文列名）
        required_columns_map = {
            'student_id': ['student_id', '学生ID'],
            'subject': ['subject', '科目'],
            'score': ['score', '成绩']
        }
        
        # 检查是否包含必需的列（支持中英文）
        missing_columns = []
        column_mapping = {}  # 用于后续重命名列
        
        for key, possible_names in required_columns_map.items():
            found = False
            for name in possible_names:
                if name in df.columns:
                    column_mapping[name] = key
                    found = True
                    break
            if not found:
                missing_columns.append(possible_names[0])
        
        if missing_columns:
            error_msg = f'文件缺少必要列: {", ".join(missing_columns)}'
            print(error_msg)
            return jsonify({'message': error_msg}), 400
        
        print(f"列映射关系: {column_mapping}")
        
        # 重命名列以匹配内部使用
        df.rename(columns=column_mapping, inplace=True)
        print(f"重命名后的列: {list(df.columns)}")
        
        # 转换数据类型
        print(f"转换前的数据类型: {df.dtypes}")
        print(f"前5行数据: {df.head()}")
        try:
            df['student_id'] = df['student_id'].astype(int)
            df['score'] = df['score'].astype(float)
        except ValueError as ve:
            error_msg = f'数据类型转换错误: {str(ve)}'
            print(error_msg)
            return jsonify({'message': error_msg}), 400
        print(f"转换后的数据类型: {df.dtypes}")
        
        # 如果存在exam_type列，则处理它
        if 'exam_type' in df.columns or '考试类型' in df.columns:
            exam_type_col = 'exam_type' if 'exam_type' in df.columns else '考试类型'
            df.rename(columns={exam_type_col: 'exam_type'}, inplace=True)
        else:
            # 如果没有提供考试类型，默认设为空字符串
            df['exam_type'] = ''
        
        # 创建成绩对象列表
        grades = []
        for index, row in df.iterrows():
            print(f"处理第 {index} 行数据: {row.to_dict()}")
            try:
                grade = Grade(
                    student_id=row['student_id'],
                    subject=row['subject'],
                    score=row['score']
                )
                # 只有当exam_type字段存在且不为空时才设置
                if 'exam_type' in row and row['exam_type']:
                    grade.exam_type = row['exam_type']
                grades.append(grade)
            except Exception as e:
                error_msg = f'创建第 {index} 行成绩记录时出错: {str(e)}'
                print(error_msg)
                return jsonify({'message': error_msg}), 400
        
        # 批量保存到数据库
        print(f"准备保存 {len(grades)} 条记录到数据库")
        try:
            db.session.bulk_save_objects(grades)
            db.session.commit()
            print("数据保存成功")
        except Exception as e:
            db.session.rollback()
            error_msg = f'数据库保存失败: {str(e)}'
            print(error_msg)
            return jsonify({'message': error_msg}), 500
        
        return jsonify({'message': f'成功导入 {len(grades)} 条成绩记录'}), 201
    
    except Exception as e:
        db.session.rollback()
        print(f"导入失败，错误详情: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'导入失败: {str(e)}'}), 500

@bp.route('/<string:subject>/statistics', methods=['GET'])
@jwt_required()
def get_statistics(subject):
    grades = Grade.query.filter_by(subject=subject).all()
    
    if not grades:
        return jsonify({'message': '该科目暂无成绩数据'}), 404
    
    scores = [g.score for g in grades]
    
    statistics = {
        'subject': subject,
        'count': len(scores),
        'average': float(np.mean(scores)),
        'median': float(np.median(scores)),
        'max': float(np.max(scores)),
        'min': float(np.min(scores)),
        'std': float(np.std(scores))
    }
    
    return jsonify(statistics), 200

@bp.route('/<int:student_id>/predict', methods=['GET'])
@jwt_required()
def predict_grades(student_id):
    # 获取学生的历史成绩数据
    grades = Grade.query.filter_by(student_id=student_id).all()
    
    if len(grades) < 2:
        return jsonify({'message': '数据不足，无法进行预测'}), 400
    
    # 准备数据用于线性回归
    X = np.array([i for i in range(len(grades))]).reshape(-1, 1)
    y = np.array([g.score for g in grades])
    
    # 创建并训练模型
    model = LinearRegression()
    model.fit(X, y)
    
    # 预测下一次成绩
    next_exam = len(grades)
    prediction = model.predict([[next_exam]])[0]
    
    # 判断是否有挂科风险
    at_risk = prediction < 60
    
    return jsonify({
        'predicted_score': prediction,
        'at_risk': at_risk,
        'trend': 'increasing' if model.coef_[0] > 0 else 'decreasing'
    }), 200

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_grade(id):
    data = request.get_json()
    grade = Grade.query.get_or_404(id)
    
    # 更新成绩信息
    grade.student_id = data.get('student_id', grade.student_id)
    grade.subject = data.get('subject', grade.subject)
    grade.score = data.get('score', grade.score)
    
    db.session.commit()
    
    return jsonify({'message': '成绩更新成功', 'grade': grade.to_dict()}), 200

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_grade(id):
    grade = Grade.query.get_or_404(id)
    db.session.delete(grade)
    db.session.commit()
    
    return jsonify({'message': '成绩删除成功'}), 200