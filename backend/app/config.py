import os
from typing import Dict, Any

def _parse_list(value, default):
    if value is None:
        return default
    if isinstance(value, (list, tuple)):
        return list(value)
    # 逗号分隔
    return [v.strip() for v in value.split(",") if v.strip()]


class BaseConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///instance/app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
    CORS_ORIGINS = _parse_list(os.getenv("CORS_ORIGINS"), ["*"])
    JSON_SORT_KEYS = False
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.getcwd(), "instance", "uploads"))
    ALLOWED_UPLOAD_EXTS = _parse_list(
        os.getenv("ALLOWED_UPLOAD_EXTS"),
        [
            "pdf",
            "ppt",
            "pptx",
            "doc",
            "docx",
            "xls",
            "xlsx",
            "csv",
            "png",
            "jpg",
            "jpeg",
        ],
    )
    DISALLOWED_UPLOAD_EXTS = _parse_list(
        os.getenv("DISALLOWED_UPLOAD_EXTS"),
        ["exe", "bat", "cmd", "sh", "js", "msi", "apk"],
    )
    ALLOWED_UPLOAD_MIME = _parse_list(
        os.getenv("ALLOWED_UPLOAD_MIME"),
        [
            "application/pdf",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/csv",
            "image/png",
            "image/jpeg",
        ],
    )
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_MB", "20")) * 1024 * 1024 * 60  # Flask will reject > size


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(name=None):
    name = name or os.getenv("FLASK_ENV", "development")
    return config_map.get(name, DevelopmentConfig)



class Config:
    # API配置
    ZHIPU_API_KEY = "828590b7664b458798a512eceab31c14.xEjyLLpsD5Szrhrc"
    ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"

    # 模型配置
    EMBEDDING_MODEL = "shibing624/text2vec-base-chinese"
    RERANKER_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
    LLM_MODEL = "glm-4"

    # 检索配置
    RETRIEVAL_TOP_K = 5
    RERANK_TOP_K = 3

    # 文件路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DOC_FILE = os.path.join(BASE_DIR, "data", "doc.md")

    # LLM参数
    LLM_PARAMS = {
        "max_tokens": 4096,
        "temperature": 0.7,
        "top_p": 0.7,
    }

    # 重试配置
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 1

    # 对话配置
    MAX_HISTORY = 10

    # 调试配置
    VERBOSE = True  # 是否显示详细日志