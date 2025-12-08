"""
RAG系统API服务器 - 适配前端调用
"""
import os
import json
import logging
from typing import List, Dict, Any
from flask import Blueprint, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sys
from pathlib import Path

from ..utils.chatUtils import RAGSystem

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建蓝图
chat_bp = Blueprint("chat", __name__, url_prefix="/chat")

# 配置
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'md'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

# 全局RAG系统实例
rag_system: RAGSystem = None
current_doc_path: str = None

def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def initialize_rag_system(doc_path: str = None, chunk_strategy: str = "paragraph") -> bool:
    """初始化RAG系统"""
    global rag_system, current_doc_path

    try:
        logger.info(f"正在初始化RAG系统，文档路径: {doc_path}")

        if rag_system is None:
            rag_system = RAGSystem()

        # 如果提供了新文档，使用新文档初始化
        if doc_path and os.path.exists(doc_path):
            rag_system.initialize(doc_path, chunk_strategy)
            current_doc_path = doc_path
        elif hasattr(rag_system, 'is_initialized') and not rag_system.is_initialized:
            # 使用默认文档初始化
            from app.config import Config
            config = Config()
            default_doc = config.DOC_FILE
            if os.path.exists(default_doc):
                rag_system.initialize(default_doc, chunk_strategy)
                current_doc_path = default_doc

        return True
    except Exception as e:
        logger.error(f"初始化RAG系统失败: {str(e)}")
        rag_system = None
        current_doc_path = None
        return False

@chat_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'rag_initialized': rag_system is not None and getattr(rag_system, 'is_initialized', False),
        'current_document': current_doc_path
    })

@chat_bp.route('/status', methods=['GET'])
def get_system_status():
    """获取系统状态"""
    try:
        if rag_system is None:
            return jsonify({
                'status': 'not_initialized',
                'message': '系统未初始化',
                'rag_initialized': False
            })

        return jsonify({
            'status': 'ready',
            'rag_initialized': rag_system.is_initialized,
            'current_document': os.path.basename(current_doc_path) if current_doc_path else None,
            'chunk_count': len(rag_system.chunks) if hasattr(rag_system, 'chunks') else 0,
            'has_history': len(rag_system.conversation.history) > 0 if hasattr(rag_system, 'conversation') else False
        })
    except Exception as e:
        logger.error(f"获取状态失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@chat_bp.route('', methods=['POST'])
def handle_chat():
    """处理聊天请求"""
    try:
        # 确保系统已初始化
        if rag_system is None or not rag_system.is_initialized:
            success = initialize_rag_system()
            if not success:
                return jsonify({
                    'success': False,
                    'error': '系统未初始化，请先上传文档'
                }), 400

        data = request.json
        query = data.get('message', '').strip()
        verbose = data.get('verbose', False)

        if not query:
            return jsonify({
                'success': False,
                'error': '消息不能为空'
            }), 400

        logger.info(f"处理用户查询: {query[:50]}...")

        # 执行查询
        answer = rag_system.query(query, verbose=verbose)

        # 判断是否使用了检索
        retrieval_used = rag_system.needs_retrieval(query, rag_system.conversation.get_history()[:-1])

        response = {
            'success': True,
            'answer': answer,
            'retrieval_used': retrieval_used,
            'timestamp': request.headers.get('X-Request-Id', '')
        }

        # 如果需要，可以添加检索到的文档片段
        # response['sources'] = []  # 这里可以添加检索到的文档片段

        logger.info(f"查询处理完成，回答长度: {len(answer)}")
        return jsonify(response)

    except Exception as e:
        logger.error(f"聊天处理失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '处理您的请求时发生错误'
        }), 500

@chat_bp.route('/upload', methods=['POST'])
def upload_document():
    """上传文档文件"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传文件'
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400

        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'不支持的文件类型，只支持: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400

        # 确保上传目录存在
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # 安全保存文件名
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # 保存文件
        file.save(file_path)
        logger.info(f"文件上传成功: {filename}，保存路径: {file_path}")

        # 初始化RAG系统
        chunk_strategy = request.form.get('chunk_strategy', 'paragraph')
        success = initialize_rag_system(file_path, chunk_strategy)

        if not success:
            return jsonify({
                'success': False,
                'error': '文档处理失败'
            }), 500

        return jsonify({
            'success': True,
            'filename': filename,
            'file_path': file_path,
            'rag_initialized': True,
            'message': '文档上传并处理成功'
        })

    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/initialize', methods=['POST'])
def initialize_system():
    """初始化系统"""
    try:
        data = request.json or {}
        doc_path = data.get('doc_path')
        chunk_strategy = data.get('chunk_strategy', 'paragraph')

        success = initialize_rag_system(doc_path, chunk_strategy)

        if success:
            return jsonify({
                'success': True,
                'message': '系统初始化成功',
                'rag_initialized': True,
                'current_document': os.path.basename(current_doc_path) if current_doc_path else None
            })
        else:
            return jsonify({
                'success': False,
                'error': '系统初始化失败'
            }), 500

    except Exception as e:
        logger.error(f"系统初始化失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/history', methods=['GET'])
def get_conversation_history():
    """获取对话历史"""
    try:
        if rag_system is None or not hasattr(rag_system, 'conversation'):
            return jsonify({
                'success': True,
                'history': []
            })

        history = rag_system.conversation.get_history()

        # 格式化历史记录
        formatted_history = []
        for msg in history:
            formatted_history.append({
                'role': msg.get('role', 'unknown'),
                'content': msg.get('content', ''),
                'timestamp': 'recent'  # 可以添加时间戳
            })

        return jsonify({
            'success': True,
            'history': formatted_history,
            'total': len(formatted_history)
        })

    except Exception as e:
        logger.error(f"获取历史记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/clear', methods=['POST'])
def clear_conversation():
    """清空对话历史"""
    try:
        if rag_system is not None and hasattr(rag_system, 'conversation'):
            rag_system.conversation.clear_history()
            logger.info("对话历史已清空")

        return jsonify({
            'success': True,
            'message': '对话历史已清空'
        })

    except Exception as e:
        logger.error(f"清空历史失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/batch-query', methods=['POST'])
def handle_batch_query():
    """处理批量查询"""
    try:
        if rag_system is None or not rag_system.is_initialized:
            return jsonify({
                'success': False,
                'error': '系统未初始化'
            }), 400

        data = request.json
        queries = data.get('queries', [])

        if not queries:
            return jsonify({
                'success': False,
                'error': '查询列表不能为空'
            }), 400

        logger.info(f"批量处理 {len(queries)} 个查询")

        # 执行批量查询
        answers = []
        for i, query in enumerate(queries):
            try:
                answer = rag_system.query(query, verbose=False)
                answers.append({
                    'query': query,
                    'answer': answer,
                    'success': True
                })
                logger.info(f"已完成 {i+1}/{len(queries)}")
            except Exception as e:
                answers.append({
                    'query': query,
                    'answer': f"查询失败: {str(e)}",
                    'success': False,
                    'error': str(e)
                })
                logger.warning(f"查询失败: {query[:50]}... - {str(e)}")

        return jsonify({
            'success': True,
            'results': answers,
            'total': len(answers),
            'success_count': sum(1 for r in answers if r['success'])
        })

    except Exception as e:
        logger.error(f"批量查询失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/settings', methods=['GET'])
def get_settings():
    """获取系统设置"""
    try:
        if rag_system is None:
            return jsonify({
                'success': True,
                'settings': {
                    'chunk_size': 500,
                    'overlap': 50,
                    'retrieval_top_k': 5,
                    'rerank_top_k': 3,
                    'max_history': 10
                }
            })

        # 从配置获取设置
        from app.config import Config
        config = Config()

        settings = {
            'chunk_size': rag_system.chunker.chunk_size if hasattr(rag_system, 'chunker') else 500,
            'overlap': rag_system.chunker.overlap if hasattr(rag_system, 'chunker') else 50,
            'retrieval_top_k': config.RETRIEVAL_TOP_K,
            'rerank_top_k': config.RERANK_TOP_K,
            'max_history': rag_system.conversation.max_history if hasattr(rag_system, 'conversation') else 10,
            'verbose': config.VERBOSE
        }

        return jsonify({
            'success': True,
            'settings': settings
        })

    except Exception as e:
        logger.error(f"获取设置失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/system-info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    try:
        info = {
            'rag_system': 'Initialized' if rag_system and rag_system.is_initialized else 'Not Initialized',
            'current_document': current_doc_path,
            'api_version': '1.0.0',
            'components': ['chunker', 'embedding', 'retriever', 'reranker', 'generator']
        }

        return jsonify({
            'success': True,
            'info': info
        })

    except Exception as e:
        logger.error(f"获取系统信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/documents', methods=['GET'])
def list_documents():
    """列出已上传的文档"""
    try:
        documents = []
        if os.path.exists(UPLOAD_FOLDER):
            for file in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, file)
                if os.path.isfile(file_path) and allowed_file(file):
                    documents.append({
                        'name': file,
                        'path': file_path,
                        'size': os.path.getsize(file_path),
                        'is_current': file_path == current_doc_path,
                        'upload_time': os.path.getctime(file_path)
                    })

        return jsonify({
            'success': True,
            'documents': documents,
            'current': current_doc_path
        })

    except Exception as e:
        logger.error(f"列出文档失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
