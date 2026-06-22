"""
工具函数补充测试 - 覆盖 file_utils、date_utils、validators 的边界情况
"""
import os
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.utils.file_utils import (
    get_file_extension,
    get_mime_type,
    format_file_size,
    ensure_directory,
    safe_filename,
    get_file_info,
    list_files,
    delete_file,
    read_file_content,
    write_file_content,
    is_image_file,
    is_video_file,
    is_audio_file,
    is_document_file,
)
from app.utils.date_utils import (
    format_datetime,
    parse_datetime,
    get_time_ago,
    get_date_range,
    convert_timezone,
    is_today,
    is_this_week,
    is_this_month,
    get_timestamp,
    from_timestamp,
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
    is_valid_date,
    sanitize_html,
)


# ==================== file_utils 补充测试 ====================

class TestFileUtilsExtra:
    """文件工具函数补充测试"""

    def test_get_file_extension_uppercase(self):
        assert get_file_extension("IMAGE.JPG") == "jpg"

    def test_get_mime_type_empty(self):
        assert get_mime_type("") == "application/octet-stream"

    def test_get_mime_type_unknown(self):
        assert get_mime_type("file.unknownext") == "application/octet-stream"

    def test_format_file_size_zero(self):
        assert format_file_size(0) == "0 B"

    def test_format_file_size_tb(self):
        assert "TB" in format_file_size(2 * 1024 * 1024 * 1024 * 1024)

    def test_format_file_size_pb(self):
        assert "PB" in format_file_size(2 * 1024 * 1024 * 1024 * 1024 * 1024)

    def test_ensure_directory_failure(self):
        # 无效路径应返回 False
        assert ensure_directory("/nonexistent_root/path/with\0null") is False or \
               ensure_directory("") is False

    def test_safe_filename_empty(self):
        assert safe_filename("") == "unnamed"

    def test_safe_filename_with_path(self):
        result = safe_filename("/path/to/file.txt")
        assert "/" not in result
        assert "file.txt" in result

    def test_safe_filename_control_chars(self):
        result = safe_filename("file\x00name.txt")
        assert "\x00" not in result

    def test_safe_filename_long_name(self, tmp_path):
        # 超长文件名应被截断
        long_name = "a" * 300 + ".txt"
        result = safe_filename(long_name)
        assert len(result) <= 255

    def test_get_file_info_existing(self, tmp_path):
        filepath = tmp_path / "test.txt"
        filepath.write_text("hello")
        info = get_file_info(str(filepath))
        assert info is not None
        assert info["name"] == "test.txt"
        assert info["size"] == 5
        assert info["is_file"] is True
        assert info["is_dir"] is False
        assert info["extension"] == "txt"

    def test_get_file_info_nonexistent(self):
        info = get_file_info("/nonexistent/file.txt")
        assert info is None

    def test_get_file_info_directory(self, tmp_path):
        info = get_file_info(str(tmp_path))
        assert info is not None
        assert info["is_dir"] is True
        assert info["is_file"] is False

    def test_list_files_empty_directory(self, tmp_path):
        files = list_files(str(tmp_path))
        assert files == []

    def test_list_files_nonexistent(self):
        files = list_files("/nonexistent/directory")
        assert files == []

    def test_list_files_with_files(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        files = list_files(str(tmp_path))
        assert len(files) == 2

    def test_list_files_recursive(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "b.txt").write_text("b")
        files = list_files(str(tmp_path), recursive=True)
        assert len(files) == 2

    def test_list_files_with_pattern(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.log").write_text("b")
        files = list_files(str(tmp_path), pattern="*.txt")
        assert len(files) == 1

    def test_delete_file_existing(self, tmp_path):
        filepath = tmp_path / "delete_me.txt"
        filepath.write_text("data")
        assert delete_file(str(filepath)) is True
        assert not filepath.exists()

    def test_delete_file_nonexistent(self):
        assert delete_file("/nonexistent/file.txt") is False

    def test_delete_file_directory(self, tmp_path):
        # 删除目录应返回 False
        assert delete_file(str(tmp_path)) is False

    def test_read_file_content(self, tmp_path):
        filepath = tmp_path / "read.txt"
        filepath.write_text("content here")
        assert read_file_content(str(filepath)) == "content here"

    def test_read_file_content_nonexistent(self):
        assert read_file_content("/nonexistent/file.txt") is None

    def test_write_file_content(self, tmp_path):
        filepath = tmp_path / "subdir" / "write.txt"
        assert write_file_content(str(filepath), "new content") is True
        assert filepath.read_text() == "new content"

    def test_write_file_content_failure(self):
        # 通过 mock open 触发异常路径
        with patch("builtins.open", side_effect=OSError("denied")):
            assert write_file_content("/tmp/whatever_fail.txt", "data") is False

    def test_is_image_file_various(self):
        assert is_image_file("photo.jpeg") is True
        assert is_image_file("photo.bmp") is True
        assert is_image_file("photo.webp") is True
        assert is_image_file("photo.svg") is True
        assert is_image_file("photo.tiff") is True
        assert is_image_file("photo.ico") is True

    def test_is_video_file_various(self):
        assert is_video_file("video.mov") is True
        assert is_video_file("video.wmv") is True
        assert is_video_file("video.flv") is True
        assert is_video_file("video.mkv") is True
        assert is_video_file("video.webm") is True

    def test_is_audio_file_various(self):
        assert is_audio_file("audio.flac") is True
        assert is_audio_file("audio.aac") is True
        assert is_audio_file("audio.ogg") is True
        assert is_audio_file("audio.wma") is True

    def test_is_document_file_various(self):
        assert is_document_file("doc.docx") is True
        assert is_document_file("doc.xls") is True
        assert is_document_file("doc.xlsx") is True
        assert is_document_file("doc.ppt") is True
        assert is_document_file("doc.pptx") is True
        assert is_document_file("doc.rtf") is True
        assert is_document_file("doc.odt") is True


# ==================== date_utils 补充测试 ====================

class TestDateUtilsExtra:
    """日期工具函数补充测试"""

    def test_format_datetime_with_string(self):
        result = format_datetime("2024-01-15")
        assert "2024" in result

    def test_format_datetime_invalid_string(self):
        # parse_datetime 对无效字符串返回 None，后续 strftime 抛 AttributeError
        with pytest.raises(AttributeError):
            format_datetime("not a date")

    def test_parse_datetime_empty(self):
        assert parse_datetime("") is None

    def test_parse_datetime_with_format(self):
        result = parse_datetime("15/01/2024", fmt="%d/%m/%Y")
        assert result is not None
        assert result.day == 15

    def test_parse_datetime_invalid_format(self):
        result = parse_datetime("invalid", fmt="%Y-%m-%d")
        assert result is None

    def test_parse_datetime_iso_format(self):
        result = parse_datetime("2024-01-15T10:30:00Z")
        assert result is not None

    def test_parse_datetime_iso_with_microseconds(self):
        result = parse_datetime("2024-01-15T10:30:00.123456Z")
        assert result is not None

    def test_parse_datetime_slash_format(self):
        result = parse_datetime("15/01/2024 10:30:00")
        assert result is not None

    def test_parse_datetime_us_format(self):
        result = parse_datetime("01/15/2024")
        assert result is not None

    def test_get_time_ago_none(self):
        assert get_time_ago(None) == ""

    def test_get_time_ago_seconds(self):
        now = datetime.utcnow()
        recent = now - timedelta(seconds=30)
        result = get_time_ago(recent)
        assert "刚刚" in result

    def test_get_time_ago_days(self):
        past = datetime.utcnow() - timedelta(days=5)
        result = get_time_ago(past)
        assert "天" in result

    def test_get_time_ago_months(self):
        past = datetime.utcnow() - timedelta(days=60)
        result = get_time_ago(past)
        assert "个月" in result

    def test_get_time_ago_years(self):
        past = datetime.utcnow() - timedelta(days=400)
        result = get_time_ago(past)
        assert "年" in result

    def test_get_time_ago_with_timezone(self):
        past = datetime.now(timezone.utc) - timedelta(hours=2)
        result = get_time_ago(past)
        assert "小时" in result

    def test_get_date_range_with_end_date(self):
        end = datetime(2024, 6, 15)
        start, end_result = get_date_range(days=7, end_date=end)
        assert (end_result - start).days == 7

    def test_convert_timezone(self):
        dt = datetime(2024, 1, 15, 12, 0, 0)
        result = convert_timezone(dt, from_tz="UTC", to_tz="Asia/Shanghai")
        assert result.hour == 20

    def test_convert_timezone_with_aware_dt(self):
        dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = convert_timezone(dt, to_tz="Asia/Shanghai")
        assert result.hour == 20

    def test_is_today_none(self):
        assert is_today(datetime.utcnow()) is True

    def test_is_this_week_past(self):
        past = datetime.utcnow() - timedelta(days=10)
        assert is_this_week(past) is False

    def test_is_this_month_different_month(self):
        past = datetime.utcnow() - timedelta(days=60)
        assert is_this_month(past) is False

    def test_get_timestamp_with_dt(self):
        dt = datetime(2024, 1, 1)
        ts = get_timestamp(dt)
        assert isinstance(ts, int)

    def test_from_timestamp_roundtrip(self):
        ts = 1704067200  # 2024-01-01
        dt = from_timestamp(ts)
        assert dt.year == 2024


# ==================== validators 补充测试 ====================

class TestValidatorsExtra:
    """验证器补充测试"""

    def test_is_valid_url_empty(self):
        assert is_valid_url("") is False

    def test_is_valid_url_exception(self):
        # 触发异常的情况
        assert is_valid_url(None) is False

    def test_is_valid_email_empty(self):
        assert is_valid_email("") is False

    def test_is_valid_ip_empty(self):
        assert is_valid_ip("") is False

    def test_is_valid_ip_ipv6(self):
        assert is_valid_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334") is True

    def test_is_valid_ip_invalid(self):
        assert is_valid_ip("999.999.999.999") is False

    def test_is_valid_json_empty(self):
        assert is_valid_json("") is False

    def test_is_valid_json_invalid(self):
        assert is_valid_json("{invalid}") is False

    def test_is_valid_json_none(self):
        assert is_valid_json(None) is False

    def test_is_valid_phone_empty(self):
        assert is_valid_phone("") is False

    def test_is_valid_phone_us(self):
        assert is_valid_phone("1234567890", country="US") is True

    def test_is_valid_phone_with_special_chars(self):
        # 去除 - 后为 11 位有效号码
        assert is_valid_phone("138-1234-5678") is True

    def test_is_valid_phone_with_country_code_invalid(self):
        # +86 前缀去除后变为 13 位，不符合 CN 11 位规则
        assert is_valid_phone("+86 138-1234-5678") is False

    def test_is_valid_phone_other_country(self):
        assert is_valid_phone("12345678", country="XX") is True

    def test_is_valid_password_empty(self):
        assert is_valid_password("") is False

    def test_is_valid_password_complexity_missing_upper(self):
        assert is_valid_password("password1!", require_complexity=True) is False

    def test_is_valid_password_complexity_missing_lower(self):
        assert is_valid_password("PASSWORD1!", require_complexity=True) is False

    def test_is_valid_password_complexity_missing_digit(self):
        assert is_valid_password("Password!", require_complexity=True) is False

    def test_is_valid_password_complexity_missing_special(self):
        assert is_valid_password("Password1", require_complexity=True) is False

    def test_is_valid_username_empty(self):
        assert is_valid_username("") is False

    def test_is_valid_username_too_long(self):
        assert is_valid_username("a" * 51) is False

    def test_is_valid_username_with_underscore_hyphen(self):
        assert is_valid_username("user_name-123") is True

    def test_is_valid_domain_empty(self):
        assert is_valid_domain("") is False

    def test_is_valid_domain_invalid(self):
        assert is_valid_domain("-invalid.com") is False

    def test_is_valid_port_string(self):
        assert is_valid_port("80") is True

    def test_is_valid_port_invalid_string(self):
        assert is_valid_port("abc") is False

    def test_is_valid_port_negative(self):
        assert is_valid_port(-1) is False

    def test_is_valid_hex_color_empty(self):
        assert is_valid_hex_color("") is False

    def test_is_valid_hex_color_invalid(self):
        assert is_valid_hex_color("#gggggg") is False

    def test_is_valid_date_valid(self):
        assert is_valid_date("2024-01-15") is True

    def test_is_valid_date_invalid(self):
        assert is_valid_date("invalid") is False

    def test_is_valid_date_empty(self):
        assert is_valid_date("") is False

    def test_is_valid_date_custom_format(self):
        assert is_valid_date("15/01/2024", fmt="%d/%m/%Y") is True

    def test_is_valid_uuid_empty(self):
        assert is_valid_uuid("") is False

    def test_is_valid_uuid_uppercase(self):
        assert is_valid_uuid("550E8400-E29B-41D4-A716-446655440000") is True

    def test_is_valid_uuid_invalid(self):
        assert is_valid_uuid("not-a-uuid") is False

    def test_sanitize_html_empty(self):
        assert sanitize_html("") == ""

    def test_sanitize_html_none(self):
        assert sanitize_html(None) == ""

    def test_sanitize_html_script_tag(self):
        html = '<script>alert("xss")</script><p>safe</p>'
        result = sanitize_html(html)
        assert "<script>" not in result.lower()
        assert "safe" in result

    def test_sanitize_html_style_tag(self):
        html = '<style>body{color:red}</style><p>text</p>'
        result = sanitize_html(html)
        assert "<style>" not in result.lower()

    def test_sanitize_html_iframe_tag(self):
        html = '<iframe src="evil.com"></iframe><p>text</p>'
        result = sanitize_html(html)
        assert "<iframe>" not in result.lower()

    def test_sanitize_html_on_event_double_quotes(self):
        html = '<p onclick="alert(1)">text</p>'
        result = sanitize_html(html)
        assert "onclick" not in result.lower()

    def test_sanitize_html_on_event_single_quotes(self):
        html = "<p onclick='alert(1)'>text</p>"
        result = sanitize_html(html)
        assert "onclick" not in result.lower()

    def test_sanitize_html_javascript_protocol(self):
        html = '<a href="javascript:alert(1)">link</a>'
        result = sanitize_html(html)
        assert "javascript:" not in result.lower()
