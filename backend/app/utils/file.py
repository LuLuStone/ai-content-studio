"""文件管理工具"""

import os
import uuid
from app.config import get_settings


def get_storage_path(sub_dir: str) -> str:
    """获取存储目录的绝对路径"""
    settings = get_settings()
    path = os.path.join(settings.STORAGE_PATH, sub_dir)
    os.makedirs(path, exist_ok=True)
    return path


def generate_filename(extension: str) -> str:
    """生成唯一文件名"""
    return f"{uuid.uuid4().hex}.{extension}"


def get_file_url(sub_dir: str, filename: str) -> str:
    """获取文件访问 URL"""
    return f"/storage/{sub_dir}/{filename}"


def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False
