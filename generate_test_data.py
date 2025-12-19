#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成测试数据脚本
用于向数据库中添加示例数据，方便测试系统功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User, Material, Attendance, Grade
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta

def generate_users():
    """生成测试用户数据"""
    print("生成用户数据...")
    
    # 检查是否已有用户
    if User.query.first():
        print("用户数据已存在，跳过创建")
        return
    
    # 创建教师用户
    teacher = User(
        username='teacher1',
        email='teacher1@example.com',
        role='teacher'
    )
    teacher.set_password('teacher123')
    
    # 创建学生用户
    students = []
    student_names = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十']
    for i, name in enumerate(student_names):
        student = User(
            username=f'student{i+1}',
            email=f'student{i+1}@example.com',
            role='student'
        )
        student.set_password(f'student{i+1}pwd')
        students.append(student)
    
    # 添加到数据库
    db.session.add(teacher)
    for student in students:
        db.session.add(student)
    
    db.session.commit()
    print(f"已创建1名教师和{len(students)}名学生")

def generate_materials():
    """生成测试资料数据"""
    print("生成资料数据...")
    
    # 检查是否已有资料
    if Material.query.first():
        print("资料数据已存在，跳过创建")
        return
    
    # 获取教师用户ID
    teacher = User.query.filter_by(role='teacher').first()
    if not teacher:
        print("未找到教师用户，请先创建用户数据")
        return
    
    materials_data = [
        {
            'title': '数学课件第一章',
            'description': '集合与函数概念',
            'filename': 'math_chapter1.pdf',
            'filepath': 'uploads/math_chapter1.pdf'
        },
        {
            'title': '英语语法资料',
            'description': '动词时态详解',
            'filename': 'english_grammar.docx',
            'filepath': 'uploads/english_grammar.docx'
        },
        {
            'title': '物理实验报告模板',
            'description': '标准实验报告格式',
            'filename': 'physics_template.xlsx',
            'filepath': 'uploads/physics_template.xlsx'
        },
        {
            'title': '化学元素周期表',
            'description': '高清彩色版元素周期表',
            'filename': 'chemistry_periodic_table.png',
            'filepath': 'uploads/chemistry_periodic_table.png'
        },
        {
            'title': '历史复习提纲',
            'description': '世界近代史重点整理',
            'filename': 'history_outline.pptx',
            'filepath': 'uploads/history_outline.pptx'
        }
    ]
    
    materials = []
    for data in materials_data:
        material = Material(
            title=data['title'],
            description=data['description'],
            filename=data['filename'],
            filepath=data['filepath'],
            uploaded_by=teacher.id
        )
        materials.append(material)
        db.session.add(material)
    
    db.session.commit()
    print(f"已创建{len(materials)}个资料")

def generate_attendance_tasks():
    """生成测试考勤任务数据"""
    print("生成考勤任务数据...")
    
    # 检查是否已有考勤任务
    if Attendance.query.first():
        print("考勤任务数据已存在，跳过创建")
        return
    
    # 获取教师用户ID
    teacher = User.query.filter_by(role='teacher').first()
    if not teacher:
        print("未找到教师用户，请先创建用户数据")
        return
    
    tasks_data = [
        {
            'title': '周一上午数学课',
            'course_id': 1,
            'deadline': datetime.now() + timedelta(days=1)
        },
        {
            'title': '周三下午英语课',
            'course_id': 2,
            'deadline': datetime.now() + timedelta(days=2)
        },
        {
            'title': '周五物理实验',
            'course_id': 3,
            'deadline': datetime.now() + timedelta(days=3)
        }
    ]
    
    tasks = []
    for data in tasks_data:
        task = Attendance(
            title=data['title'],
            course_id=data['course_id'],
            teacher_id=teacher.id,
            submitted_students='[]',  # 初始无学生提交
            deadline=data['deadline']
        )
        tasks.append(task)
        db.session.add(task)
    
    db.session.commit()
    print(f"已创建{len(tasks)}个考勤任务")

def generate_grades():
    """生成测试成绩数据"""
    print("生成成绩数据...")
    
    # 检查是否已有成绩数据
    if Grade.query.first():
        print("成绩数据已存在，跳过创建")
        return
    
    # 获取学生用户IDs
    students = User.query.filter_by(role='student').all()
    if not students:
        print("未找到学生用户，请先创建用户数据")
        return
    
    subjects = ['数学', '英语', '物理', '化学', '语文']
    exam_types = ['quiz', 'midterm', 'final', 'homework']
    
    grades = []
    for student in students:
        # 为每个学生生成几门课程的成绩
        for subject in subjects:
            # 生成2-4次成绩记录
            for _ in range(random.randint(2, 4)):
                grade = Grade(
                    student_id=student.id,
                    subject=subject,
                    score=round(random.uniform(60, 100), 2),  # 随机分数60-100，保留两位小数
                    exam_type=random.choice(exam_types)
                )
                grades.append(grade)
                db.session.add(grade)
    
    db.session.commit()
    print(f"已创建{len(grades)}条成绩记录")

def main():
    """主函数"""
    print("开始生成测试数据...")
    
    with app.app_context():
        # 创建所有表（如果不存在）
        db.create_all()
        
        # 生成各类测试数据
        generate_users()
        generate_materials()
        generate_attendance_tasks()
        generate_grades()
        
        print("测试数据生成完成！")

if __name__ == '__main__':
    main()