from flask_sqlalchemy import SQLAlchemy

# 创建全局 db 实例
db = SQLAlchemy()

from .user import User
from .material import Material
from .attendance import Attendance
from .grade import Grade
from .course import Course, CourseEnrollment