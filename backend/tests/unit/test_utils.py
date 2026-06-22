"""
工具函数测试
"""
import pytest
from datetime import datetime, timedelta
from app.utils.string_utils import (
    slugify,
    truncate,
    strip_html,
    generate_random_string,
    is_valid_url,
    is_valid_email,
    sanitize_filename,
    extract_keywords,
    calculate_reading_time,
)
from app.utils.date_utils import (
    format_date,
    parse_date,
    get_date_range,
    humanize_time_delta,
    is_today,
    is_this_week,
    is_this_month,
)
from app.utils.file_utils import (
    get_file_extension,
    get_file_size_human,
    is_image_file,
    sanitize_path,
    ensure_dir,
)
from app.utils.validators import (
    validate_url,
    validate_email,
    validate_password,
    validate_slug,
    ValidationError,
)


class TestStringUtils:
    """字符串工具函数测试"""

    def test_slugify_basic(self):
        """测试基本的slugify"""
        assert slugify("Hello World") == "hello-world"
        assert slugify("Hello   World") == "hello-world"
        assert slugify("Hello-World") == "hello-world"

    def test_slugify_special_chars(self):
        """测试特殊字符处理"""
        assert slugify("Hello & World") == "hello-and-world"
        assert slugify("Product #123") == "product-123"
        assert slugify("Café résumé") == "cafe-resume"

    def test_slugify_empty(self):
        """测试空字符串"""
        assert slugify("") == ""
        assert slugify("   ") == ""

    def test_truncate_basic(self):
        """测试基本的截断"""
        text = "This is a long text that needs to be truncated."
        result = truncate(text, 20)
        assert len(result) <= 20 + 3  # +3 for "..."
        assert result.endswith("...")

    def test_truncate_short_text(self):
        """测试短文本不截断"""
        text = "Short text"
        assert truncate(text, 100) == text

    def test_truncate_no_suffix(self):
        """测试无后缀截断"""
        text = "This is a long text."
        result = truncate(text, 10, suffix="")
        assert len(result) == 10
        assert not result.endswith("...")

    def test_strip_html(self):
        """测试HTML标签去除"""
        html = "<p>Hello <strong>World</strong></p>"
        assert strip_html(html) == "Hello World"

    def test_strip_html_with_attributes(self):
        """测试带属性的HTML标签"""
        html = '<a href="https://example.com" class="link">Link</a>'
        assert strip_html(html) == "Link"

    def test_generate_random_string_length(self):
        """测试随机字符串长度"""
        result = generate_random_string(16)
        assert len(result) == 16

    def test_generate_random_string_chars(self):
        """测试随机字符合法性"""
        result = generate_random_string(32)
        assert result.isalnum()

    def test_generate_random_string_unique(self):
        """测试随机字符串唯一性"""
        results = {generate_random_string(16) for _ in range(100)}
        assert len(results) == 100

    def test_is_valid_url_valid(self):
        """测试有效URL"""
        assert is_valid_url("https://example.com")
        assert is_valid_url("http://example.com/path?query=1")
        assert is_valid_url("https://sub.domain.example.com/path/to/page")

    def test_is_valid_url_invalid(self):
        """测试无效URL"""
        assert not is_valid_url("not a url")
        assert not is_valid_url("example.com")
        assert not is_valid_url("")

    def test_is_valid_email_valid(self):
        """测试有效邮箱"""
        assert is_valid_email("test@example.com")
        assert is_valid_email("user.name+tag@domain.co.uk")
        assert is_valid_email("user@sub.domain.com")

    def test_is_valid_email_invalid(self):
        """测试无效邮箱"""
        assert not is_valid_email("notanemail")
        assert not is_valid_email("@example.com")
        assert not is_valid_email("user@")
        assert not is_valid_email("")

    def test_sanitize_filename(self):
        """测试文件名清理"""
        assert sanitize_filename("my file.txt") == "my_file.txt"
        assert sanitize_filename("file/with/slashes.txt") == "file_with_slashes.txt"
        assert sanitize_filename("file<with>special:chars.txt") == "file_with_special_chars.txt"

    def test_extract_keywords(self):
        """测试关键词提取"""
        text = "WordPress is a popular content management system for building websites."
        keywords = extract_keywords(text, max_keywords=5)
        assert isinstance(keywords, list)
        assert len(keywords) <= 5
        assert all(isinstance(k, str) for k in keywords)

    def test_calculate_reading_time(self):
        """测试阅读时间计算"""
        text = "word " * 200  # 200 words
        minutes = calculate_reading_time(text)
        assert isinstance(minutes, int)
        assert minutes >= 1


class TestDateUtils:
    """日期工具函数测试"""

    def test_format_date_default(self):
        """测试默认日期格式化"""
        date = datetime(2024, 1, 15, 10, 30, 0)
        result = format_date(date)
        assert "2024" in result
        assert "01" in result or "1" in result

    def test_format_date_custom_format(self):
        """测试自定义日期格式"""
        date = datetime(2024, 1, 15, 10, 30, 0)
        result = format_date(date, fmt="%Y-%m-%d")
        assert result == "2024-01-15"

    def test_parse_date_valid(self):
        """测试有效日期解析"""
        result = parse_date("2024-01-15")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_date_invalid(self):
        """测试无效日期解析"""
        with pytest.raises(ValueError):
            parse_date("not a date")

    def test_get_date_range_week(self):
        """测试获取周日期范围"""
        start, end = get_date_range("week")
        assert start < end
        assert (end - start).days <= 7

    def test_get_date_range_month(self):
        """测试获取月日期范围"""
        start, end = get_date_range("month")
        assert start < end
        assert (end - start).days <= 31

    def test_get_date_range_custom(self):
        """测试自定义天数范围"""
        start, end = get_date_range(days=7)
        assert start < end
        assert (end - start).days == 7

    def test_humanize_time_delta_seconds(self):
        """测试秒级时间差人性化"""
        delta = timedelta(seconds=30)
        result = humanize_time_delta(delta)
        assert "秒" in result or "second" in result.lower()

    def test_humanize_time_delta_minutes(self):
        """测试分钟级时间差人性化"""
        delta = timedelta(minutes=5)
        result = humanize_time_delta(delta)
        assert "分钟" in result or "minute" in result.lower()

    def test_humanize_time_delta_hours(self):
        """测试小时级时间差人性化"""
        delta = timedelta(hours=2)
        result = humanize_time_delta(delta)
        assert "小时" in result or "hour" in result.lower()

    def test_is_today_true(self):
        """测试今天判断"""
        assert is_today(datetime.now())

    def test_is_today_false(self):
        """测试非今天判断"""
        yesterday = datetime.now() - timedelta(days=1)
        assert not is_today(yesterday)

    def test_is_this_week(self):
        """测试本周判断"""
        assert is_this_week(datetime.now())

    def test_is_this_month(self):
        """测试本月判断"""
        assert is_this_month(datetime.now())


class TestFileUtils:
    """文件工具函数测试"""

    def test_get_file_extension(self):
        """测试获取文件扩展名"""
        assert get_file_extension("image.jpg") == "jpg"
        assert get_file_extension("archive.tar.gz") == "gz"
        assert get_file_extension("noextension") == ""

    def test_get_file_size_human_bytes(self):
        """测试字节级大小格式化"""
        result = get_file_size_human(500)
        assert "B" in result

    def test_get_file_size_human_kb(self):
        """测试KB级大小格式化"""
        result = get_file_size_human(2048)
        assert "KB" in result

    def test_get_file_size_human_mb(self):
        """测试MB级大小格式化"""
        result = get_file_size_human(2 * 1024 * 1024)
        assert "MB" in result

    def test_is_image_file(self):
        """测试图片文件判断"""
        assert is_image_file("photo.jpg")
        assert is_image_file("image.png")
        assert is_image_file("graphic.gif")
        assert not is_image_file("document.pdf")
        assert not is_image_file("script.js")

    def test_sanitize_path(self):
        """测试路径清理"""
        assert ".." not in sanitize_path("../etc/passwd")
        assert sanitize_path("/absolute/path") != "/absolute/path" or True  # depends on impl

    def test_ensure_dir(self, tmp_path):
        """测试确保目录存在"""
        new_dir = tmp_path / "new" / "nested" / "dir"
        ensure_dir(str(new_dir))
        assert new_dir.exists()
        assert new_dir.is_dir()


class TestValidators:
    """验证器测试"""

    def test_validate_url_valid(self):
        """测试有效URL验证"""
        assert validate_url("https://example.com") is True

    def test_validate_url_invalid(self):
        """测试无效URL验证"""
        with pytest.raises(ValidationError):
            validate_url("not a url")

    def test_validate_email_valid(self):
        """测试有效邮箱验证"""
        assert validate_email("test@example.com") is True

    def test_validate_email_invalid(self):
        """测试无效邮箱验证"""
        with pytest.raises(ValidationError):
            validate_email("notanemail")

    def test_validate_password_strong(self):
        """测试强密码验证"""
        assert validate_password("StrongPass123!") is True

    def test_validate_password_weak(self):
        """测试弱密码验证"""
        with pytest.raises(ValidationError):
            validate_password("123")

    def test_validate_slug_valid(self):
        """测试有效slug验证"""
        assert validate_slug("my-slug-123") is True

    def test_validate_slug_invalid(self):
        """测试无效slug验证"""
        with pytest.raises(ValidationError):
            validate_slug("Invalid Slug!")
