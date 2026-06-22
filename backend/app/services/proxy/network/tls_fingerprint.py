"""
TLS指纹（JA3/JA3S）伪造配置生成器
提供TLS ClientHello指纹的配置生成功能

注意：这是一个配置生成器，实际的TLS指纹伪造需要在底层网络库中实现
（如使用curl-impersonate、requests-impersonate等库）
"""
import random
import hashlib
from typing import Dict, Any, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class TLSFingerprintGenerator:
    """TLS指纹生成器"""
    
    # Chrome 124的密码套件
    CHROME_CIPHER_SUITES = [
        0x1301,  # TLS_AES_128_GCM_SHA256
        0x1302,  # TLS_AES_256_GCM_SHA384
        0x1303,  # TLS_CHACHA20_POLY1305_SHA256
        0xc02b,  # TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
        0xc02f,  # TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
        0xc02c,  # TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
        0xc030,  # TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        0xcca9,  # TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256
        0xcca8,  # TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256
        0xc013,  # TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA
        0xc014,  # TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA
        0x009c,  # TLS_RSA_WITH_AES_128_GCM_SHA256
        0x009d,  # TLS_RSA_WITH_AES_256_GCM_SHA384
        0x002f,  # TLS_RSA_WITH_AES_128_CBC_SHA
        0x0035,  # TLS_RSA_WITH_AES_256_CBC_SHA
        0x000a,  # TLS_RSA_WITH_3DES_EDE_CBC_SHA
    ]
    
    # Firefox 125的密码套件
    FIREFOX_CIPHER_SUITES = [
        0x1301,  # TLS_AES_128_GCM_SHA256
        0x1302,  # TLS_AES_256_GCM_SHA384
        0x1303,  # TLS_CHACHA20_POLY1305_SHA256
        0xc02b,  # TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
        0xc02f,  # TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
        0xc02c,  # TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
        0xc030,  # TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        0xcca9,  # TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256
        0xcca8,  # TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256
        0xc013,  # TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA
        0xc014,  # TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA
        0x009c,  # TLS_RSA_WITH_AES_128_GCM_SHA256
        0x009d,  # TLS_RSA_WITH_AES_256_GCM_SHA384
        0x002f,  # TLS_RSA_WITH_AES_128_CBC_SHA
        0x0035,  # TLS_RSA_WITH_AES_256_CBC_SHA
    ]
    
    # Chrome的扩展顺序
    CHROME_EXTENSIONS = [
        65281,  # renegotiation_info
        0,      # server_name
        23,     # extended_master_secret
        65282,  # extended_master_secret (duplicate?)
        16,     # application_layer_protocol_negotiation
        11,     # ec_point_formats
        10,     # supported_groups
        42,     # supported_versions
        45,     # psk_key_exchange_modes
        43,     # cookie
        50,     # signature_algorithms
        57,     # key_share
        35,     # SessionTicket TLS
        13,     # signature_algorithms (old?)
        41,     # pre_shared_key
        21,     # padding
        65037,  # encrypted_client_hello
        17513,  # compress_certificate
        12,     # signed_certificate_timestamp
        18,     # subject_alt_name
        34,     # status_request
        5,      # status_request_v2
        14,     # heartbeat
        15,     # application_layer_protocol_negotiation_settings
    ]
    
    # 支持的曲线
    CHROME_SUPPORTED_GROUPS = [
        0x001d,  # X25519
        0x0017,  # secp256r1
        0x0018,  # secp384r1
        0x0019,  # secp521r1
        0x0100,  # ffdhe2048
        0x0101,  # ffdhe3072
        0x0102,  # ffdhe4096
        0x0103,  # ffdhe6144
        0x0104,  # ffdhe8192
    ]
    
    # 签名算法
    CHROME_SIGNATURE_ALGORITHMS = [
        0x0403,  # ecdsa_secp256r1_sha256
        0x0503,  # ecdsa_secp384r1_sha384
        0x0603,  # ecdsa_secp521r1_sha512
        0x0807,  # ed25519
        0x0808,  # ed448
        0x0809,  # ed25519ph
        0x080a,  # ed448ph
        0x0401,  # rsa_pkcs1_sha256
        0x0501,  # rsa_pkcs1_sha384
        0x0601,  # rsa_pkcs1_sha512
        0x0201,  # rsa_pkcs1_sha1
        0x0203,  # ecdsa_sha1
    ]
    
    # ALPN协议
    CHROME_ALPN = [
        "h2",
        "http/1.1",
    ]
    
    def __init__(self):
        self._browser: str = "chrome"
        self._browser_version: str = "124"
        self._os: str = "windows"
    
    def set_browser(self, browser: str, version: str = "124"):
        """设置浏览器类型和版本"""
        self._browser = browser.lower()
        self._browser_version = version
    
    def set_os(self, os: str):
        """设置操作系统"""
        self._os = os.lower()
    
    def generate_tls_config(self) -> Dict[str, Any]:
        """
        生成TLS配置
        
        Returns:
            TLS配置字典
        """
        if self._browser == "chrome":
            return self._generate_chrome_config()
        elif self._browser == "firefox":
            return self._generate_firefox_config()
        elif self._browser == "safari":
            return self._generate_safari_config()
        else:
            return self._generate_chrome_config()
    
    def _generate_chrome_config(self) -> Dict[str, Any]:
        """生成Chrome风格的TLS配置"""
        return {
            "browser": "chrome",
            "version": self._browser_version,
            "cipher_suites": self.CHROME_CIPHER_SUITES.copy(),
            "extensions": self.CHROME_EXTENSIONS.copy(),
            "supported_groups": self.CHROME_SUPPORTED_GROUPS.copy(),
            "signature_algorithms": self.CHROME_SIGNATURE_ALGORITHMS.copy(),
            "alpn": self.CHROME_ALPN.copy(),
            "ec_point_formats": [0],  # uncompressed
            "compression_methods": [0],  # null
            "tls_version": "1.3",
            "supported_versions": [
                0x0304,  # TLS 1.3
                0x0303,  # TLS 1.2
                0x0302,  # TLS 1.1
                0x0301,  # TLS 1.0
            ],
            "key_share_groups": [0x001d, 0x0017],  # X25519, secp256r1
            "psk_key_exchange_modes": [0],  # psk_dhe_ke
            "record_size_limit": 16385,
            "ja3": self._calculate_ja3(
                self.CHROME_CIPHER_SUITES,
                self.CHROME_EXTENSIONS,
                self.CHROME_SUPPORTED_GROUPS,
                self.CHROME_SIGNATURE_ALGORITHMS,
            ),
        }
    
    def _generate_firefox_config(self) -> Dict[str, Any]:
        """生成Firefox风格的TLS配置"""
        return {
            "browser": "firefox",
            "version": self._browser_version,
            "cipher_suites": self.FIREFOX_CIPHER_SUITES.copy(),
            "extensions": self.CHROME_EXTENSIONS.copy(),  # 简化，实际不同
            "supported_groups": self.CHROME_SUPPORTED_GROUPS.copy(),
            "signature_algorithms": self.CHROME_SIGNATURE_ALGORITHMS.copy(),
            "alpn": ["h2", "http/1.1"],
            "ec_point_formats": [0],
            "compression_methods": [0],
            "tls_version": "1.3",
            "supported_versions": [
                0x0304,  # TLS 1.3
                0x0303,  # TLS 1.2
            ],
            "key_share_groups": [0x001d, 0x0017],
            "psk_key_exchange_modes": [0],
            "record_size_limit": 16385,
            "ja3": "",  # 需要实际计算
        }
    
    def _generate_safari_config(self) -> Dict[str, Any]:
        """生成Safari风格的TLS配置"""
        return {
            "browser": "safari",
            "version": self._browser_version,
            "cipher_suites": self.FIREFOX_CIPHER_SUITES.copy(),  # 简化
            "extensions": [],  # 简化
            "supported_groups": [],
            "signature_algorithms": [],
            "alpn": ["h2", "http/1.1"],
            "ec_point_formats": [0],
            "compression_methods": [0],
            "tls_version": "1.3",
            "supported_versions": [],
            "key_share_groups": [],
            "psk_key_exchange_modes": [],
            "record_size_limit": 16385,
            "ja3": "",
        }
    
    def _calculate_ja3(self, cipher_suites: List[int], extensions: List[int],
                       supported_groups: List[int], 
                       signature_algorithms: List[int]) -> str:
        """
        计算JA3指纹
        
        JA3格式：
        TLSVersion,Ciphers,Extensions,EllipticCurves,EllipticCurvePointFormats
        """
        # TLS 1.2 = 0x0303 = 771
        tls_version = "771"
        
        # 密码套件
        ciphers_str = "-".join(str(c) for c in cipher_suites)
        
        # 扩展
        extensions_str = "-".join(str(e) for e in extensions)
        
        # 椭圆曲线
        curves_str = "-".join(str(g) for g in supported_groups)
        
        # 椭圆曲线点格式
        point_formats_str = "0"  # uncompressed
        
        # 组合
        ja3_string = f"{tls_version},{ciphers_str},{extensions_str},{curves_str},{point_formats_str}"
        
        # MD5哈希
        ja3_hash = hashlib.md5(ja3_string.encode()).hexdigest()
        
        return ja3_hash
    
    def get_ja3_string(self) -> str:
        """获取JA3字符串"""
        config = self.generate_tls_config()
        return config.get("ja3", "")
    
    def get_recommended_libraries(self) -> List[str]:
        """获取推荐的TLS指纹伪造库"""
        return [
            "curl-impersonate",
            "requests-impersonate",
            "playwright-stealth",
            "puppeteer-extra-plugin-stealth",
            "undetected-chromedriver",
        ]
    
    def get_tls_fingerprint_tips(self) -> List[str]:
        """获取TLS指纹伪造的建议"""
        return [
            "使用与浏览器UA匹配的TLS指纹",
            "保持密码套件顺序与真实浏览器一致",
            "保持扩展顺序与真实浏览器一致",
            "使用与浏览器匹配的ALPN协议列表",
            "确保支持的曲线和签名算法匹配",
            "TLS 1.3需要正确配置key_share扩展",
            "注意GREASE值的使用",
            "保持record_size_limit一致",
        ]
