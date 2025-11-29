import os


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
        ["pdf", "ppt", "pptx", "doc", "docx", "xls", "xlsx", "png", "jpg", "jpeg"],
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
            "image/png",
            "image/jpeg",
        ],
    )
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_MB", "20")) * 1024 * 1024  # Flask will reject > size


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
