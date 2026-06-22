"""
工具函数测试
"""
import pytest
from datetime import datetime, timedelta
from app.utils.string_utils import (
    clean_text,
    extract_domain,
    generate_slug,
    truncate_string,
    remove_html_tags,
    normalize_url,
    generate_hash,
    extract_numbers,
    camel_to_snake,
    snake_to_camel,
)
from app.utils.date_utils import (
    format_datetime,
    parse_datetime,
    get_time_ago,
    get_date_range,
    is_today,
    is_this_week,
    is_this_month,
    get_timestamp,
    from_timestamp,
)
from app.utils.file_utils import (
    get_file_extension,
    get_mime_type,
    format_file_size,
    ensure_directory,
    safe_filename,
    is_image_file,
    is_video_file,
    is_audio_file,
    is_document_file,
)
from app.utils.validators import (
    is_valid_url,
    is_valid_email,
    is_valid_ip,
    is_valid_json,
    is_valid_phone,
    is_valid_password,
    is_valid_username,
    is_valid_domain,
    is_valid_port,
    is_valid_hex_color,
    is_valid_uuid,
    sanitize_html,
)


class TestStringUtils:
    """字符串工具函数测试"""

    def test_clean_text(self):
        """测试文本清理"""
        assert clean_text("  hello   world  ") == "hello world"
        assert clean_text("<p>text</p>") == "text"
        assert clean_text("") == ""

    def test_extract_domain(self):
        """测试域名提取"""
        assert extract_domain("https://example.com/path") == "example.com"
        assert extract_domain("https://www.example.com") == "example.com"
        assert extract_domain("") == ""

    def test_generate_slug(self):
        """测试slug生成"""
        assert generate_slug("Hello World") == "hello-world"
        assert generate_slug("Hello   World") == "hello-world"
        assert generate_slug("") == ""

    def test_truncate_string(self):
        """测试字符串截断"""
        text = "This is a long text that needs to be truncated."
        result = truncate_string(text, 20)
        assert len(result) <= 20
        assert result.endswith("...")

    def test_truncate_string_short(self):
        """测试短文本不截断"""
        text = "Short text"
        assert truncate_string(text, 100) == text

    def test_remove_html_tags(self):
        """测试HTML标签移除"""
        html = "<p>Hello <strong>World</strong></p>"
        result = remove_html_tags(html)
        assert "Hello" in result
        assert "World" in result
        assert "<" not in result

    def test_normalize_url(self):
        """测试URL标准化"""
        assert normalize_url("example.com") == "https://example.com"
        assert normalize_url("https://example.com/") == "https://example.com"
        assert normalize_url("") == ""

    def test_generate_hash(self):
        """测试哈希生成"""
        assert generate_hash("test") == generate_hash("test")
        assert len(generate_hash("test")) > 0
        assert generate_hash("test", "sha256") != generate_hash("test", "md5")

    def test_extract_numbers(self):
        """测试数字提取"""
        assert extract_numbers("abc123def456") == ["123", "456"]
        assert extract_numbers("price: 99.99") == ["99.99"]
        assert extract_numbers("") == []

    def test_camel_to_snake(self):
        """测试驼峰转下划线"""
        assert camel_to_snake("camelCase") == "camel_case"
        assert camel_to_snake("PascalCase") == "pascal_case"

    def test_snake_to_camel(self):
        """测试下划线转驼峰"""
        assert snake_to_camel("snake_case") == "snakeCase"
        assert snake_to_camel("simple") == "simple"


class TestDateUtils:
    """日期工具函数测试"""

    def test_format_datetime(self):
        """测试日期格式化"""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = format_datetime(dt, fmt="%Y-%m-%d")
        assert result == "2024-01-15"

    def test_format_datetime_default(self):
        """测试默认格式化"""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = format_datetime(dt)
        assert "2024-01-15 10:30:00" == result

    def test_format_datetime_none(self):
        """测试None值"""
        assert format_datetime(None) == ""

    def test_parse_datetime(self):
        """测试日期解析"""
        result = parse_datetime("2024-01-15")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_datetime_with_time(self):
        """测试带时间的日期解析"""
        result = parse_datetime("2024-01-15 10:30:00")
        assert result is not None
        assert result.hour == 10
        assert result.minute == 30

    def test_parse_datetime_invalid(self):
        """测试无效日期"""
        assert parse_datetime("not a date") is None

    def test_get_time_ago(self):
        """测试相对时间"""
        now = datetime.utcnow()
        recent = now - timedelta(minutes=5)
        result = get_time_ago(recent)
        assert "分钟" in result

    def test_get_time_ago_hours(self):
        """测试小时级相对时间"""
        past = datetime.utcnow() - timedelta(hours=2)
        result = get_time_ago(past)
        assert "小时" in result

    def test_get_date_range(self):
        """测试日期范围"""
        start, end = get_date_range(days=7)
        assert start < end
        assert (end - start).days == 7

    def test_is_today(self):
        """测试今天判断"""
        assert is_today(datetime.utcnow()) is True
        yesterday = datetime.utcnow() - timedelta(days=1)
        assert is_today(yesterday) is False

    def test_is_this_week(self):
        """测试本周判断"""
        assert is_this_week(datetime.utcnow()) is True

    def test_is_this_month(self):
        """测试本月判断"""
        assert is_this_month(datetime.utcnow()) is True

    def test_get_timestamp(self):
        """测试时间戳"""
        ts = get_timestamp()
        assert isinstance(ts, int)
        assert ts > 0

    def test_from_timestamp(self):
        """测试从时间戳创建"""
        ts = get_timestamp()
        dt = from_timestamp(ts)
        assert isinstance(dt, datetime)


class TestFileUtils:
    """文件工具函数测试"""

    def test_get_file_extension(self):
        """测试获取文件扩展名"""
        assert get_file_extension("image.jpg") == "jpg"
        assert get_file_extension("archive.tar.gz") == "gz"
        assert get_file_extension("noextension") == ""
        assert get_file_extension("") == ""

    def test_get_mime_type(self):
        """测试获取MIME类型"""
        assert "image" in get_mime_type("photo.jpg")
        assert "text" in get_mime_type("file.txt") or get_mime_type("file.txt") != "application/octet-stream"

    def test_format_file_size(self):
        """测试文件大小格式化"""
        assert "B" in format_file_size(500)
        assert "KB" in format_file_size(2048)
        assert "MB" in format_file_size(2 * 1024 * 1024)
        assert "GB" in format_file_size(2 * 1024 * 1024 * 1024)

    def test_ensure_directory(self, tmp_path):
        """测试确保目录存在"""
        new_dir = tmp_path / "new" / "nested" / "dir"
        assert ensure_directory(str(new_dir)) is True
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_safe_filename(self):
        """测试安全文件名"""
        result = safe_filename("my file.txt")
        assert " " in result or "_" in result  # 空格保留或替换
        assert "/" not in result

    def test_safe_filename_dangerous(self):
        """测试危险字符文件名"""
        result = safe_filename("file<with>special:chars.txt")
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result

    def test_is_image_file(self):
        """测试图片文件判断"""
        assert is_image_file("photo.jpg") is True
        assert is_image_file("image.png") is True
        assert is_image_file("graphic.gif") is True
        assert is_image_file("document.pdf") is False
        assert is_image_file("script.js") is False

    def test_is_video_file(self):
        """测试视频文件判断"""
        assert is_video_file("video.mp4") is True
        assert is_video_file("clip.avi") is True
        assert is_video_file("image.jpg") is False

    def test_is_audio_file(self):
        """测试音频文件判断"""
        assert is_audio_file("song.mp3") is True
        assert is_audio_file("voice.wav") is True
        assert is_audio_file("image.jpg") is False

    def test_is_document_file(self):
        """测试文档文件判断"""
        assert is_document_file("doc.pdf") is True
        assert is_document_file("notes.txt") is True
        assert is_document_file("image.jpg") is False


class TestValidators:
    """验证器测试"""

    def test_is_valid_url_valid(self):
        """测试有效URL"""
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("http://example.com/path?query=1") is True

    def test_is_valid_url_invalid(self):
        """测试无效URL"""
        assert is_valid_url("not a url") is False
        assert is_valid_url("example.com") is False
        assert is_valid_url("") is False

    def test_is_valid_email_valid(self):
        """测试有效邮箱"""
        assert is_valid_email("test@example.com") is True
        assert is_valid_email("user.name+tag@domain.co.uk") is True

    def test_is_valid_email_invalid(self):
        """测试无效邮箱"""
        assert is_valid_email("notanemail") is False
        assert is_valid_email("@example.com") is False
        assert is_valid_email("user@") is False
        assert is_valid_email("") is False

    def test_is_valid_ip(self):
        """测试IP验证"""
        assert is_valid_ip("192.168.1.1") is True
        assert is_valid_ip("256.1.1.1") is False
        assert is_valid_ip("") is False

    def test_is_valid_json(self):
        """测试JSON验证"""
        assert is_valid_json('{"key": "value"}') is True
        assert is_valid_json('[1, 2, 3]') is True
        assert is_valid_json("not json") is False

    def test_is_valid_phone(self):
        """测试手机号验证"""
        assert is_valid_phone("13812345678") is True
        assert is_valid_phone("12345") is False

    def test_is_valid_password(self):
        """测试密码验证"""
        assert is_valid_password("password123") is True
        assert is_valid_password("123") is False
        assert is_valid_password("") is False

    def test_is_valid_password_complexity(self):
        """测试密码复杂度"""
        assert is_valid_password("Pass123!", require_complexity=True) is True
        assert is_valid_password("password", require_complexity=True) is False

    def test_is_valid_username(self):
        """测试用户名验证"""
        assert is_valid_username("testuser") is True
        assert is_valid_username("ab") is False
        assert is_valid_username("user@name") is False

    def test_is_valid_domain(self):
        """测试域名验证"""
        assert is_valid_domain("example.com") is True
        assert is_valid_domain("sub.example.com") is True
        assert is_valid_domain("notadomain") is False

    def test_is_valid_port(self):
        """测试端口验证"""
        assert is_valid_port(80) is True
        assert is_valid_port(65535) is True
        assert is_valid_port(0) is False
        assert is_valid_port(70000) is False

    def test_is_valid_hex_color(self):
        """测试十六进制颜色"""
        assert is_valid_hex_color("#ff0000") is True
        assert is_valid_hex_color("#fff") is True
        assert is_valid_hex_color("red") is False

    def test_is_valid_uuid(self):
        """测试UUID验证"""
        assert is_valid_uuid("550e8400-e29b-41d4-a716-446655440000") is True
        assert is_valid_uuid("not-a-uuid") is False

    def test_sanitize_html(self):
        """测试HTML清理"""
        html = '<script>alert("xss")</script><p>safe</p>'
        result = sanitize_html(html)
        assert "<script>" not in result.lower()
        assert "safe" in result
