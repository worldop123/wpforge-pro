"""
字符串工具函数测试

对应 app/utils/string_utils.py 的实际实现。
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
        assert clean_text("  hello   world  ") == "hello world"
        assert clean_text("hello\nworld") == "hello world"
        assert clean_text("hello\tworld") == "hello world"
        assert clean_text("") == ""
        assert clean_text(None) == ""

    def test_clean_text_html(self):
        """测试清理含HTML的文本"""
        assert clean_text("<p>hello</p>") == "hello"

    def test_extract_domain(self):
        """测试提取域名"""
        assert extract_domain("https://www.example.com/path") == "example.com"
        assert extract_domain("https://example.com") == "example.com"
        assert extract_domain("http://example.com/path?q=1") == "example.com"
        assert extract_domain("not a url") == ""
        assert extract_domain("") == ""

    def test_extract_domain_with_subdomain(self):
        """测试提取带子域名的URL（函数仅去除 www 前缀）"""
        # blog.example.co.uk 不会被简化为 example.co.uk
        assert extract_domain("http://blog.example.co.uk/page") == "blog.example.co.uk"

    def test_generate_slug(self):
        """测试生成slug"""
        assert generate_slug("Hello World") == "hello-world"
        assert generate_slug("  Hello   World  ") == "hello-world"
        assert generate_slug("Hello-World!") == "hello-world"
        assert generate_slug("") == ""

    def test_generate_slug_chinese(self):
        """测试中文slug（python-slugify 会转为拼音）"""
        slug = generate_slug("你好世界")
        assert isinstance(slug, str)
        assert len(slug) > 0

    def test_truncate_string(self):
        """测试截断字符串"""
        # 实现为 text[:max_length - len(suffix)] + suffix
        assert truncate_string("Hello World", 8) == "Hello..."
        assert truncate_string("Hello", 10) == "Hello"
        assert truncate_string("Hello World", 5, suffix="") == "Hello"
        assert truncate_string("", 10) == ""
        assert truncate_string(None, 10) == ""

    def test_truncate_string_custom_suffix(self):
        """测试自定义后缀截断"""
        result = truncate_string("Hello World", 10, suffix="***")
        assert result.endswith("***")

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
        md5_hash = generate_hash("test", algorithm="md5")
        assert len(md5_hash) == 32

        sha1_hash = generate_hash("test", algorithm="sha1")
        assert len(sha1_hash) == 40

        sha256_hash = generate_hash("test", algorithm="sha256")
        assert len(sha256_hash) == 64

        assert generate_hash("test") == generate_hash("test")
        assert generate_hash("test1") != generate_hash("test2")
        assert generate_hash("") == ""

    def test_generate_hash_unknown_algorithm(self):
        """测试未知算法默认使用md5"""
        result = generate_hash("test", algorithm="unknown")
        assert len(result) == 32  # md5 长度

    def test_extract_numbers(self):
        """测试提取数字（返回字符串列表）"""
        # 实现使用 re.findall(r'\d+\.?\d*', text) 返回字符串
        result = extract_numbers("Price: $123.45")
        assert isinstance(result, list)
        assert "123.45" in result

        result = extract_numbers("1, 2, 3, 4, 5")
        assert len(result) == 5

        assert extract_numbers("No numbers here") == []
        assert extract_numbers("") == []

    def test_camel_to_snake(self):
        """测试驼峰转下划线"""
        assert camel_to_snake("camelCase") == "camel_case"
        assert camel_to_snake("CamelCase") == "camel_case"
        assert camel_to_snake("already_snake") == "already_snake"
        assert camel_to_snake("") == ""

    def test_camel_to_snake_consecutive_uppercase(self):
        """测试连续大写字母（每个大写字母前都加下划线）"""
        # 实现使用 (?<!^)(?=[A-Z]) 正则，对连续大写字母会逐个加下划线
        result = camel_to_snake("getHTTPResponse")
        assert isinstance(result, str)
        assert result == "get_h_t_t_p_response"

    def test_snake_to_camel(self):
        """测试下划线转驼峰"""
        assert snake_to_camel("snake_case") == "snakeCase"
        assert snake_to_camel("hello_world_test") == "helloWorldTest"
        assert snake_to_camel("alreadyCamel") == "alreadyCamel"
        assert snake_to_camel("") == ""

    def test_snake_to_camel_single_word(self):
        """测试单个单词"""
        assert snake_to_camel("word") == "word"
