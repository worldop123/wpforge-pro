"""
文件处理工具函数
"""
import os
import re
import mimetypes
from pathlib import Path
from typing import Optional


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    if not filename:
        return ""
    
    _, ext = os.path.splitext(filename)
    return ext.lower().lstrip('.')


def get_mime_type(filename: str) -> str:
    """获取文件MIME类型"""
    if not filename:
        return "application/octet-stream"
    
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小为人类可读格式"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"


def ensure_directory(path: str) -> bool:
    """确保目录存在，不存在则创建"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False


def safe_filename(filename: str) -> str:
    """生成安全的文件名"""
    if not filename:
        return "unnamed"
    
    # 移除路径分隔符
    filename = os.path.basename(filename)
    
    # 移除或替换不安全的字符
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
    
    # 移除控制字符
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # 限制长度
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        max_name_length = 255 - len(ext)
        filename = name[:max_name_length] + ext
    
    return filename


def get_file_info(filepath: str) -> Optional[dict]:
    """获取文件信息"""
    try:
        stat = os.stat(filepath)
        return {
            'name': os.path.basename(filepath),
            'path': filepath,
            'size': stat.st_size,
            'size_human': format_file_size(stat.st_size),
            'extension': get_file_extension(filepath),
            'mime_type': get_mime_type(filepath),
            'created_at': stat.st_ctime,
            'modified_at': stat.st_mtime,
            'is_file': os.path.isfile(filepath),
            'is_dir': os.path.isdir(filepath),
        }
    except Exception:
        return None


def list_files(directory: str, pattern: str = '*', recursive: bool = False) -> list:
    """列出目录中的文件"""
    if not os.path.exists(directory):
        return []
    
    files = []
    path = Path(directory)
    
    if recursive:
        file_list = path.rglob(pattern)
    else:
        file_list = path.glob(pattern)
    
    for f in file_list:
        if f.is_file():
            files.append(str(f))
    
    return sorted(files)


def delete_file(filepath: str) -> bool:
    """安全删除文件"""
    try:
        if os.path.exists(filepath) and os.path.isfile(filepath):
            os.remove(filepath)
            return True
    except Exception:
        pass
    return False


def read_file_content(filepath: str, encoding: str = 'utf-8') -> Optional[str]:
    """读取文件内容"""
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except Exception:
        return None


def write_file_content(filepath: str, content: str, encoding: str = 'utf-8') -> bool:
    """写入文件内容"""
    try:
        # 确保目录存在
        dir_path = os.path.dirname(filepath)
        if dir_path:
            ensure_directory(dir_path)
        
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception:
        return False


def is_image_file(filename: str) -> bool:
    """判断是否是图片文件"""
    ext = get_file_extension(filename)
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'tiff', 'ico'}
    return ext in image_extensions


def is_video_file(filename: str) -> bool:
    """判断是否是视频文件"""
    ext = get_file_extension(filename)
    video_extensions = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm', 'm4v'}
    return ext in video_extensions


def is_audio_file(filename: str) -> bool:
    """判断是否是音频文件"""
    ext = get_file_extension(filename)
    audio_extensions = {'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma', 'm4a'}
    return ext in audio_extensions


def is_document_file(filename: str) -> bool:
    """判断是否是文档文件"""
    ext = get_file_extension(filename)
    doc_extensions = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'rtf', 'odt'}
    return ext in doc_extensions
