"""
指纹模板
预设的浏览器指纹模板，用于快速生成真实的浏览器指纹
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random


@dataclass
class FingerprintTemplate:
    """指纹模板"""
    name: str
    description: str
    browser: str
    os: str
    os_version: str
    user_agents: List[str]
    
    # Navigator
    platform: str
    vendor: str
    product_sub: str
    app_name: str
    app_code_name: str
    app_version: str
    
    # 硬件
    min_hardware_concurrency: int
    max_hardware_concurrency: int
    min_device_memory: int
    max_device_memory: int
    
    # 屏幕
    screen_resolutions: List[tuple]
    pixel_ratios: List[float]
    color_depths: List[int]
    
    # WebGL
    webgl_vendors: List[str]
    webgl_renderers: List[str]
    
    # 字体
    fonts: List[str]
    
    # 插件
    plugins: List[str]
    mime_types: List[str]
    
    # 语言
    languages: List[str]
    accept_language: str
    
    # 时区
    timezones: List[tuple]  # (timezone, offset)
    
    # 其他
    max_touch_points: int
    webdriver: bool = False
    cookie_enabled: bool = True
    do_not_track: Optional[str] = None


# Windows Chrome 模板
WINDOWS_CHROME_TEMPLATE = FingerprintTemplate(
    name="windows_chrome",
    description="Windows 10/11 Chrome 浏览器",
    browser="chrome",
    os="windows",
    os_version="10.0",
    user_agents=[
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    ],
    platform="Win32",
    vendor="Google Inc.",
    product_sub="20030107",
    app_name="Netscape",
    app_code_name="Mozilla",
    app_version="5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    min_hardware_concurrency=4,
    max_hardware_concurrency=16,
    min_device_memory=4,
    max_device_memory=32,
    screen_resolutions=[
        (1920, 1080),
        (2560, 1440),
        (1366, 768),
        (1536, 864),
        (1440, 900),
        (1600, 900),
        (1280, 720),
        (3840, 2160),
    ],
    pixel_ratios=[1.0, 1.25, 1.5, 2.0],
    color_depths=[24, 24, 24, 32],
    webgl_vendors=[
        "Google Inc. (NVIDIA)",
        "Google Inc. (Intel)",
        "Google Inc. (AMD)",
    ],
    webgl_renderers=[
        "ANGLE (NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (NVIDIA GeForce GTX 1660 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (AMD, AMD Radeon RX 580 Series Direct3D11 vs_5_0 ps_5_0)",
    ],
    fonts=[
        "Arial", "Arial Black", "Arial Narrow",
        "Calibri", "Cambria", "Cambria Math",
        "Comic Sans MS", "Consolas", "Constantia", "Corbel",
        "Courier", "Courier New",
        "Georgia", "Helvetica", "Impact",
        "Lucida Console", "Lucida Sans Unicode",
        "Microsoft Sans Serif", "Palatino Linotype",
        "Segoe UI", "Segoe UI Light", "Segoe UI Semibold",
        "Tahoma", "Times", "Times New Roman",
        "Trebuchet MS", "Verdana", "Wingdings",
    ],
    plugins=[
        "Chrome PDF Plugin",
        "Chrome PDF Viewer",
        "Native Client",
        "Widevine Content Decryption Module",
    ],
    mime_types=[
        "application/pdf",
        "application/x-google-chrome-pdf",
        "application/x-nacl",
        "application/x-pnacl",
        "application/x-ppapi-widevine-cdm",
    ],
    languages=["en-US", "en"],
    accept_language="en-US,en;q=0.9",
    timezones=[
        ("America/New_York", 300),
        ("America/Chicago", 360),
        ("America/Denver", 420),
        ("America/Los_Angeles", 480),
    ],
    max_touch_points=0,
)

# Mac Safari 模板
MAC_SAFARI_TEMPLATE = FingerprintTemplate(
    name="mac_safari",
    description="macOS Safari 浏览器",
    browser="safari",
    os="macos",
    os_version="10_15_7",
    user_agents=[
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    ],
    platform="MacIntel",
    vendor="Apple Computer, Inc.",
    product_sub="20030107",
    app_name="Netscape",
    app_code_name="Mozilla",
    app_version="5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    min_hardware_concurrency=4,
    max_hardware_concurrency=16,
    min_device_memory=8,
    max_device_memory=64,
    screen_resolutions=[
        (2560, 1440),
        (1920, 1080),
        (2880, 1800),
        (3072, 1920),
        (1440, 900),
        (1680, 1050),
    ],
    pixel_ratios=[1.0, 2.0],
    color_depths=[24, 30],
    webgl_vendors=[
        "Google Inc. (Apple)",
    ],
    webgl_renderers=[
        "ANGLE (Apple, ANGLE Metal Renderer: Apple M1, Unspecified Version)",
        "ANGLE (Apple, ANGLE Metal Renderer: Apple M1 Pro, Unspecified Version)",
        "ANGLE (Apple, ANGLE Metal Renderer: Apple M2, Unspecified Version)",
        "ANGLE (Apple, ANGLE Metal Renderer: Apple M2 Pro, Unspecified Version)",
        "ANGLE (Apple, Apple M1, OpenGL 4.1)",
    ],
    fonts=[
        "Arial", "Arial Black", "Arial Narrow",
        "Helvetica", "Helvetica Neue",
        "Times", "Times New Roman",
        "Courier", "Courier New",
        "Verdana", "Georgia", "Tahoma",
        "Impact", "Comic Sans MS",
        "Trebuchet MS", "Palatino",
        "Optima", "Futura", "Gill Sans",
        "Hoefler Text", "Baskerville",
        "Didot", "American Typewriter",
        "Andale Mono", "Monaco", "Consolas",
    ],
    plugins=[
        "Adobe Acrobat and Reader",
        "Default Browser Helper",
        "Java Applet Plug-in",
        "QuickTime Plug-in",
        "Shockwave Flash",
        "Silverlight Plug-In",
    ],
    mime_types=[
        "application/pdf",
        "application/postscript",
        "application/vnd.ms-excel",
        "application/msword",
        "application/vnd.ms-powerpoint",
    ],
    languages=["en-us", "en"],
    accept_language="en-us",
    timezones=[
        ("America/New_York", 300),
        ("America/Los_Angeles", 480),
        ("Europe/London", 0),
        ("Europe/Paris", -60),
    ],
    max_touch_points=0,
)

# Android Chrome 模板
ANDROID_CHROME_TEMPLATE = FingerprintTemplate(
    name="android_chrome",
    description="Android Chrome 浏览器",
    browser="chrome",
    os="android",
    os_version="13",
    user_agents=[
        "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    ],
    platform="Linux armv8l",
    vendor="Google Inc.",
    product_sub="20030107",
    app_name="Netscape",
    app_code_name="Mozilla",
    app_version="5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    min_hardware_concurrency=4,
    max_hardware_concurrency=8,
    min_device_memory=4,
    max_device_memory=12,
    screen_resolutions=[
        (360, 800),
        (375, 812),
        (412, 915),
        (414, 896),
        (393, 851),
        (360, 780),
    ],
    pixel_ratios=[2.0, 2.5, 3.0, 3.5],
    color_depths=[24, 32],
    webgl_vendors=[
        "Google Inc. (ARM)",
        "Qualcomm",
    ],
    webgl_renderers=[
        "ANGLE (ARM, Mali-G78 MP14 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (Qualcomm, Adreno (TM) 660 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (Qualcomm, Adreno (TM) 730 Direct3D11 vs_5_0 ps_5_0)",
    ],
    fonts=[
        "Roboto", "Roboto Condensed", "Roboto Mono",
        "Noto Sans", "Noto Serif",
        "Droid Sans", "Droid Serif", "Droid Sans Mono",
        "Arial", "Helvetica", "Times New Roman",
        "Courier New", "Verdana", "Georgia",
    ],
    plugins=[],
    mime_types=[],
    languages=["en-US", "en"],
    accept_language="en-US,en;q=0.9",
    timezones=[
        ("America/New_York", 300),
        ("America/Los_Angeles", 480),
        ("Europe/London", 0),
        ("Asia/Tokyo", -540),
    ],
    max_touch_points=5,
)

# iOS Safari 模板
IOS_SAFARI_TEMPLATE = FingerprintTemplate(
    name="ios_safari",
    description="iOS Safari 浏览器",
    browser="safari",
    os="ios",
    os_version="17_2",
    user_agents=[
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    ],
    platform="iPhone",
    vendor="Apple Computer, Inc.",
    product_sub="20030107",
    app_name="Netscape",
    app_code_name="Mozilla",
    app_version="5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    min_hardware_concurrency=4,
    max_hardware_concurrency=6,
    min_device_memory=4,
    max_device_memory=6,
    screen_resolutions=[
        (375, 812),
        (390, 844),
        (414, 896),
        (428, 926),
        (360, 780),
        (768, 1024),
        (834, 1194),
        (1024, 1366),
    ],
    pixel_ratios=[2.0, 3.0],
    color_depths=[24, 30],
    webgl_vendors=[
        "Apple Inc.",
    ],
    webgl_renderers=[
        "Apple GPU",
        "Apple A15 GPU",
        "Apple A16 GPU",
        "Apple A17 Pro GPU",
        "Apple M1 GPU",
    ],
    fonts=[
        "Helvetica", "Helvetica Neue",
        "Arial", "Arial Unicode MS",
        "Times New Roman", "Georgia",
        "Courier", "Courier New",
        "Verdana", "Tahoma", "Trebuchet MS",
        "Impact", "Comic Sans MS",
        "Palatino", "Optima",
        "American Typewriter", "Didot",
        "Futura", "Baskerville",
        "Hoefler Text", "Gill Sans",
        "Marker Felt", "Thonburi",
        "STHeiti", "STKaiti", "STSong",
    ],
    plugins=[],
    mime_types=[],
    languages=["en-us", "en"],
    accept_language="en-us",
    timezones=[
        ("America/New_York", 300),
        ("America/Los_Angeles", 480),
        ("Europe/London", 0),
        ("Asia/Tokyo", -540),
        ("Asia/Shanghai", -480),
    ],
    max_touch_points=5,
)

# 所有模板
TEMPLATES: Dict[str, FingerprintTemplate] = {
    "windows_chrome": WINDOWS_CHROME_TEMPLATE,
    "mac_safari": MAC_SAFARI_TEMPLATE,
    "android_chrome": ANDROID_CHROME_TEMPLATE,
    "ios_safari": IOS_SAFARI_TEMPLATE,
}


def get_template(name: str) -> Optional[FingerprintTemplate]:
    """获取指定名称的模板"""
    return TEMPLATES.get(name)


def list_templates() -> List[str]:
    """列出所有可用模板"""
    return list(TEMPLATES.keys())


def get_random_template() -> FingerprintTemplate:
    """获取随机模板"""
    return random.choice(list(TEMPLATES.values()))
