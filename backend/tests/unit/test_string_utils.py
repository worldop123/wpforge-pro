"""
字符串工具函数测试
"""
import pytest
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


class TestStringUtils:
    """字符串工具函数测试类"""

    def test_clean_text(self):
        """测试清理文本"""
        # 测试多余空白
        assert clean_text("  hello   world  ") == "hello world"
        # 测试换行符
        assert clean_text("hello\nworld") == "hello world"
        # 测试制表符
        assert clean_text("hello\tworld") == "hello world"
        # 测试空字符串
        assert clean_text("") == ""
        # 测试None
        assert clean_text(None) == ""

    def test_extract_domain(self):
        """测试提取域名"""
        assert extract_domain("https://www.example.com/path") == "example.com"
        assert extract_domain("http://blog.example.co.uk/page") == "example.co.uk"
        assert extract_domain("https://example.com") == "example.com"
        assert extract_domain("not a url") == ""
        assert extract_domain("") == ""

    def test_generate_slug(self):
        """测试生成slug"""
        assert generate_slug("Hello World") == "hello-world"
        assert generate_slug("  Hello   World  ") == "hello-world"
        assert generate_slug("Hello-World!") == "hello-world"
        assert generate_slug("") == ""
        # 测试中文
        assert generate_slug("你好世界") == "你好世界"

    def test_truncate_string(self):
        """测试截断字符串"""
        assert truncate_string("Hello World", 5) == "Hello..."
        assert truncate_string("Hello", 10) == "Hello"
        assert truncate_string("Hello World", 5, suffix="") == "Hello"
        assert truncate_string("", 10) == ""

    def test_remove_html_tags(self):
        """测试移除HTML标签"""
        assert remove_html_tags("<p>Hello <b>World</b></p>") == "Hello World"
        assert remove_html_tags("<div><span>Test</span></div>") == "Test"
        assert remove_html_tags("No HTML") == "No HTML"
        assert remove_html_tags("") == ""

    def test_normalize_url(self):
        """测试标准化URL"""
        assert normalize_url("example.com") == "https://example.com"
        assert normalize_url("http://example.com") == "http://example.com"
        assert normalize_url("https://example.com/") == "https://example.com"
        assert normalize_url("") == ""

    def test_generate_hash(self):
        """测试生成哈希"""
        # MD5
        md5_hash = generate_hash("test", algorithm="md5")
        assert len(md5_hash) == 32
        
        # SHA1
        sha1_hash = generate_hash("test", algorithm="sha1")
        assert len(sha1_hash) == 40
        
        # SHA256
        sha256_hash = generate_hash("test", algorithm="sha256")
        assert len(sha256_hash) == 64
        
        # 相同输入相同输出
        assert generate_hash("test") == generate_hash("test")
        
        # 不同输入不同输出
        assert generate_hash("test1") != generate_hash("test2")

    def test_extract_numbers(self):
        """测试提取数字"""
        assert extract_numbers("Price: $123.45") == [123.45]
        assert extract_numbers("1, 2, 3, 4, 5") == [1, 2, 3, 4, 5]
        assert extract_numbers("No numbers here") == []
        assert extract_numbers("") == []

    def test_camel_to_snake(self):
        """测试驼峰转下划线"""
        assert camel_to_snake("camelCase") == "camel_case"
        assert camel_to_snake("CamelCase") == "camel_case"
        assert camel_to_snake("getHTTPResponse") == "get_http_response"
        assert camel_to_snake("already_snake") == "already_snake"
        assert camel_to_snake("") == ""

    def test_snake_to_camel(self):
        """测试下划线转驼峰"""
        assert snake_to_camel("snake_case") == "snakeCase"
        assert snake_to_camel("hello_world_test") == "helloWorldTest"
        assert snake_to_camel("alreadyCamel") == "alreadyCamel"
        assert snake_to_camel("") == ""
