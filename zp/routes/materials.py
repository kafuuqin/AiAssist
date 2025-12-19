from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, verify_jwt_in_request
from models import Material, db
import os
import time
from werkzeug.utils import secure_filename

bp = Blueprint('materials', __name__, url_prefix='/api/materials')

# 配置文件上传
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/', methods=['POST'])
@bp.route('/<path:subpath>/', methods=['POST'])
@jwt_required()
def upload_material(subpath=None):
    try:
        print("开始处理文件上传请求")
        if 'file' not in request.files:
            print("请求中没有文件")
            return jsonify({'message': '没有文件'}), 400
        
        file = request.files['file']
        print(f"接收到文件: {file.filename}")
        if file.filename == '':
            print("文件名为空")
            return jsonify({'message': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            print("文件类型允许，开始处理")
            # 生成唯一的文件名以避免冲突
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            timestamp = str(int(time.time()))
            # 即使原文件没有扩展名，也要确保生成合理的文件名
            if not ext and '.' in filename:
                # 如果文件名中有点号但被secure_filename移除了扩展名，则恢复它
                ext = '.' + filename.split('.')[-1]
            # 如果完全没有扩展名，根据文件类型白名单添加适当扩展名
            elif not ext and filename.lower() in ALLOWED_EXTENSIONS:
                ext = '.' + filename.lower()
            unique_filename = f"{name}_{timestamp}{ext}" if ext else f"{name}_{timestamp}"
            print(f"生成唯一文件名: {unique_filename}")
            
            # 确保上传目录存在
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            print(f"文件保存路径: {filepath}")
            file.save(filepath)
            print("文件保存完成")
            
            # 保存到数据库
            material = Material(
                title=request.form.get('title', ''),
                description=request.form.get('description', ''),
                filename=unique_filename,
                filepath=filepath
            )
            
            print(f"保存文件记录到数据库: {filepath}")
            
            db.session.add(material)
            db.session.commit()
            print("数据库提交完成")
            
            return jsonify({'message': '文件上传成功', 'material': material.to_dict()}), 201
        
        print("文件类型不允许")
        return jsonify({'message': '不支持的文件类型'}), 400
    except Exception as e:
        print(f"文件上传过程中发生错误: {str(e)}")
        return jsonify({'message': f'服务器内部错误: {str(e)}'}), 500

@bp.route('/', methods=['GET'])
@bp.route('/<path:subpath>/', methods=['GET'])
@jwt_required()
def get_materials(subpath=None):
    try:
        materials = Material.query.all()
        return jsonify([material.to_dict() for material in materials]), 200
    except Exception as e:
        print(f"获取材料列表时发生错误: {str(e)}")
        return jsonify({'message': '服务器内部错误'}), 500

@bp.route('/<int:id>', methods=['GET'])
@bp.route('/<int:id>/', methods=['GET'])
def download_material(id):
    # 尝试从Authorization头或access_token参数获取token
    try:
        verify_jwt_in_request(optional=True)
    except:
        access_token = request.args.get('access_token')
        if access_token:
            try:
                from flask_jwt_extended import decode_token
                # 验证token有效性
                decode_token(access_token)
                # 设置上下文以便后续使用
                from flask import _request_ctx_stack
                ctx = _request_ctx_stack.top
                ctx.jwt = decode_token(access_token)
            except Exception as e:
                return jsonify({'message': 'Token无效'}), 401
        else:
            return jsonify({'message': '缺少Token'}), 401
    try:
        print(f"尝试下载ID为{id}的材料")
        # 查询材料记录
        material = Material.query.get(id)
        if not material:
            print(f"材料ID {id} 不存在")
            return jsonify({'message': '材料不存在'}), 404
        
        print(f"找到材料记录: {material.to_dict()}")
        
        # 检查文件路径是否存在
        print(f"检查文件路径: {material.filepath}")
        if not os.path.exists(material.filepath):
            print(f"文件不存在: {material.filepath}")
            # 检查上传目录下是否存在该文件
            upload_folder_path = os.path.join(UPLOAD_FOLDER, material.filename)
            print(f"检查上传目录下的文件: {upload_folder_path}")
            if os.path.exists(upload_folder_path):
                print("文件在上传目录下存在")
                # 检查是否是预览请求
                is_preview = request.args.get('preview', False)
                return send_from_directory(UPLOAD_FOLDER, material.filename, as_attachment=not is_preview)
            return jsonify({'message': '文件不存在'}), 404
        
        print(f"发送文件: {material.filename}")
        # 检查是否是预览请求
        is_preview = request.args.get('preview', False)
        return send_from_directory(UPLOAD_FOLDER, material.filename, as_attachment=not is_preview)
    except Exception as e:
        print(f"文件下载过程中发生错误: {str(e)}")
        return jsonify({'message': f'服务器内部错误: {str(e)}'}), 500

@bp.route('/<int:id>', methods=['DELETE'])
@bp.route('/<int:id>/', methods=['DELETE'])
@jwt_required()
def delete_material(id):
    try:
        material = Material.query.get_or_404(id)
        
        # 删除文件
        print(f"删除文件: {material.filepath}")
        if os.path.exists(material.filepath):
            os.remove(material.filepath)
        
        # 从数据库删除
        db.session.delete(material)
        db.session.commit()
        
        return jsonify({'message': '材料删除成功'}), 200
    except Exception as e:
        print(f"删除材料时发生错误: {str(e)}")
        return jsonify({'message': f'服务器内部错误: {str(e)}'}), 500