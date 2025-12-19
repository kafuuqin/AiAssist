from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

# 配置 MySQL 数据库驱动
import pymysql
pymysql.install_as_MySQLdb()

# 导入配置
from config import config

# 导入模型
from models import User, Material, Attendance, Grade, db

def create_app(config_name='default'):
    # 配置应用
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)

    # 添加JWT错误处理回调
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"Token已过期: {jwt_header}, {jwt_payload}")
        return jsonify({'message': 'Token已过期'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"无效的Token: {error}")
        return jsonify({'message': '无效的Token'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"缺少Token: {error}")
        return jsonify({'message': '缺少Token'}), 401

    # 移除这里的手动创建表操作，让init_db.py来处理

    @app.route('/')
    def hello_world():
        return '教师智能助手 API 服务正在运行!'

    # 将 db 和其他扩展附加到 app 对象上，以便在路由中访问
    app.db = db
    app.jwt = jwt

    return app

# 导入路由并注册蓝图
from routes import auth, materials, attendance, grades, classroom, courses

def register_blueprints(app):
    app.register_blueprint(auth.bp)
    app.register_blueprint(materials.bp)
    app.register_blueprint(attendance.bp)
    app.register_blueprint(grades.bp)
    app.register_blueprint(classroom.bp)
    app.register_blueprint(courses.bp)

# 创建应用实例
app = create_app()

# 注册蓝图
with app.app_context():
    register_blueprints(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000)