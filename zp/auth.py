from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User, db

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 检查用户是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        role=data['role']  # teacher, student, admin
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': '用户注册成功'}), 201

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        print(f"接收到的原始数据: {data}")
        
        if not data:
            return jsonify({'message': '请求数据为空'}), 400
            
        identifier = data.get('username')  # 可以是用户名或邮箱
        password = data.get('password')
        
        print(f"登录请求 - 用户标识: {identifier}, 密码: {password}")

        if not identifier or not password:
            return jsonify({'message': '用户名/邮箱和密码不能为空'}), 400

        # 查找用户（通过用户名或邮箱）
        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        
        print(f"查找用户结果: {user}")
        if user:
            print(f"用户信息 - ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}")

        if user and user.check_password(password):
            print("密码验证成功")
            # 登录成功，生成JWT令牌
            # 将用户ID转换为字符串，确保JWT subject是字符串类型
            access_token = create_access_token(identity=str(user.id))
            response_data = {
                'access_token': access_token, 
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
            }
            print(f"登录成功，返回数据: {response_data}")
            return jsonify(response_data), 200
        else:
            print(f"登录失败 - 用户不存在或密码错误")
            return jsonify({'message': '用户名/邮箱或密码错误'}), 401
    except Exception as e:
        print(f"登录过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': '服务器内部错误'}), 500

@bp.route('/profile', methods=['GET'])
@bp.route('/profile/', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    # 将字符串形式的用户ID转换回整数
    user = User.query.get(int(current_user_id))
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    }), 200

@bp.route('/students', methods=['GET'])
@bp.route('/students/', methods=['GET'])
@jwt_required()
def get_students():
    students = User.query.filter_by(role='student').all()
    return jsonify([{'id': s.id, 'username': s.username} for s in students]), 200