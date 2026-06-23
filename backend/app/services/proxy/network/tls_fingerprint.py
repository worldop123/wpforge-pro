"""
TLS指纹（JA3/JA3S）伪造配置生成器与TLS客户端
提供TLS ClientHello指纹的配置生成功能，以及基于curl_cffi的真实TLS指纹伪造HTTP客户端

支持的浏览器指纹：
- Chrome（默认）
- Firefox
- Safari
- Edge

使用curl_cffi库在底层模拟浏览器的TLS握手，使Python发出的HTTP请求在TLS层
看起来与真实浏览器一致，从而绕过基于JA3/JA4指纹的反爬虫检测。
"""
import random
import hashlib
from typing import Dict, Any, List, Optional, Union

from app.core.logging import get_logger

logger = get_logger(__name__)

# 尝试导入curl_cffi，用于真实的TLS指纹伪造
try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False
    curl_requests = None
    logger.warning(
        "curl_cffi未安装，TLSClient将降级为httpx。"
        "请运行 pip install curl_cffi 以启用真实的TLS指纹伪造。"
    )

# curl_cffi不可用时降级到httpx
if not CURL_CFFI_AVAILABLE:
    try:
        import httpx
        HTTPX_AVAILABLE = True
    except ImportError:
        HTTPX_AVAILABLE = False
        httpx = None


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


# curl_cffi支持的浏览器指纹标识符
# 参考：https://curl-cffi.readthedocs.io/en/latest/impersonate.html
SUPPORTED_IMPERSONATE_TARGETS = {
    "chrome": [
        "chrome", "chrome99", "chrome100", "chrome101", "chrome104",
        "chrome107", "chrome110", "chrome116", "chrome119", "chrome120",
        "chrome123", "chrome124",
    ],
    "firefox": [
        "firefox", "firefox99", "firefox100", "firefox102", "firefox109",
        "firefox117", "firefox120", "firefox133",
    ],
    "safari": [
        "safari", "safari15_3", "safari15_5", "safari17_0",
    ],
    "edge": [
        "edge", "edge99", "edge101",
    ],
}


class TLSClient:
    """带TLS指纹伪造的HTTP客户端

    使用curl_cffi创建一个模拟指定浏览器TLS指纹的HTTP会话。
    当curl_cffi不可用时，自动降级为httpx（此时不会伪造TLS指纹）。

    使用示例：
        client = TLSClient(impersonate="chrome124")
        response = client.get("https://example.com", headers={"User-Agent": "..."})
        response = client.post("https://example.com/api", json={"key": "value"})

    属性：
        impersonate: 当前使用的浏览器指纹标识符
        using_curl_cffi: 是否正在使用curl_cffi（True表示已启用TLS指纹伪造）
    """

    # 默认请求超时（秒）
    DEFAULT_TIMEOUT = 30

    def __init__(
        self,
        impersonate: str = "chrome124",
        proxy: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        verify: bool = True,
    ):
        """
        初始化TLS客户端

        Args:
            impersonate: 浏览器指纹标识符（如chrome124, firefox120, safari17_0）
            proxy: 代理URL（如 http://user:pass@host:port 或 socks5://host:port）
            headers: 默认请求头（每次请求都会携带）
            timeout: 默认请求超时时间（秒）
            verify: 是否验证SSL证书
        """
        self.impersonate = self._resolve_impersonate(impersonate)
        self.proxy = proxy
        self.default_headers = headers or {}
        self.timeout = timeout
        self.verify = verify
        self.using_curl_cffi = CURL_CFFI_AVAILABLE

        if CURL_CFFI_AVAILABLE:
            # 使用curl_cffi创建带TLS指纹的会话
            self._session = curl_requests.Session(
                impersonate=self.impersonate,
                timeout=timeout,
                verify=verify,
                proxy=proxy,
            )
            logger.debug(f"TLSClient已启用curl_cffi，使用指纹: {self.impersonate}")
        elif HTTPX_AVAILABLE:
            # 降级到httpx（无TLS指纹伪造）
            self._session = httpx.Client(
                timeout=timeout,
                verify=verify,
                proxy=proxy,
            )
            logger.warning(
                f"TLSClient降级为httpx（无TLS指纹伪造），目标指纹: {self.impersonate}"
            )
        else:
            raise RuntimeError(
                "curl_cffi和httpx均未安装，无法创建TLSClient。"
                "请运行 pip install curl_cffi 或 pip install httpx"
            )

    def _resolve_impersonate(self, impersonate: str) -> str:
        """解析并校验浏览器指纹标识符

        如果传入的标识符不在支持列表中，尝试匹配最接近的浏览器类型。
        """
        if not impersonate:
            return "chrome124"

        impersonate_lower = impersonate.lower()

        # 如果完全匹配已知标识符，直接使用
        for browser_type, targets in SUPPORTED_IMPERSONATE_TARGETS.items():
            if impersonate_lower in targets:
                return impersonate_lower

        # 尝试按浏览器类型匹配默认版本
        for browser_type, targets in SUPPORTED_IMPERSONATE_TARGETS.items():
            if impersonate_lower.startswith(browser_type) or impersonate_lower == browser_type:
                # 返回该浏览器类型的最新版本
                return targets[-1]

        # 未知标识符，默认使用chrome124
        logger.warning(
            f"未知的浏览器指纹标识符: {impersonate}，将使用chrome124"
        )
        return "chrome124"

    def _merge_headers(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """合并默认请求头和请求级请求头"""
        merged = dict(self.default_headers)
        if headers:
            merged.update(headers)
        return merged

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ):
        """发送HTTP请求

        Args:
            method: HTTP方法（GET, POST, PUT, DELETE等）
            url: 请求URL
            headers: 请求头（会与默认请求头合并）
            params: URL查询参数
            data: 请求体（表单或原始数据）
            json: JSON请求体（会自动设置Content-Type）
            timeout: 本次请求超时时间（秒）
            **kwargs: 其他传递给底层库的参数

        Returns:
            响应对象（curl_cffi.Response 或 httpx.Response）
        """
        merged_headers = self._merge_headers(headers)
        request_timeout = timeout if timeout is not None else self.timeout

        try:
            if self.using_curl_cffi:
                return self._session.request(
                    method=method,
                    url=url,
                    headers=merged_headers,
                    params=params,
                    data=data,
                    json=json,
                    timeout=request_timeout,
                    **kwargs,
                )
            else:
                # httpx降级模式
                return self._session.request(
                    method=method,
                    url=url,
                    headers=merged_headers,
                    params=params,
                    data=data,
                    json=json,
                    timeout=request_timeout,
                    **kwargs,
                )
        except Exception as e:
            logger.error(f"TLSClient请求失败 [{method} {url}]: {e}")
            raise

    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ):
        """发送GET请求"""
        return self.request(
            method="GET",
            url=url,
            headers=headers,
            params=params,
            timeout=timeout,
            **kwargs,
        )

    def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ):
        """发送POST请求"""
        return self.request(
            method="POST",
            url=url,
            headers=headers,
            data=data,
            json=json,
            timeout=timeout,
            **kwargs,
        )

    def put(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ):
        """发送PUT请求"""
        return self.request(
            method="PUT",
            url=url,
            headers=headers,
            data=data,
            json=json,
            timeout=timeout,
            **kwargs,
        )

    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ):
        """发送DELETE请求"""
        return self.request(
            method="DELETE",
            url=url,
            headers=headers,
            params=params,
            timeout=timeout,
            **kwargs,
        )

    def head(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ):
        """发送HEAD请求"""
        return self.request(
            method="HEAD",
            url=url,
            headers=headers,
            params=params,
            timeout=timeout,
            **kwargs,
        )

    def patch(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ):
        """发送PATCH请求"""
        return self.request(
            method="PATCH",
            url=url,
            headers=headers,
            data=data,
            json=json,
            timeout=timeout,
            **kwargs,
        )

    def set_proxy(self, proxy: Optional[str]) -> None:
        """更新代理设置

        Args:
            proxy: 代理URL，None表示不使用代理
        """
        self.proxy = proxy
        if self.using_curl_cffi:
            # curl_cffi的Session通过proxies参数设置代理
            self._session.proxies = {"http": proxy, "https": proxy} if proxy else None
        else:
            # httpx的Client通过proxy参数设置代理（需要重建客户端）
            old_headers = self.default_headers
            old_timeout = self.timeout
            old_verify = self.verify
            try:
                self._session.close()
            except Exception:
                pass
            self._session = httpx.Client(
                timeout=old_timeout,
                verify=old_verify,
                proxy=proxy,
            )
            self.default_headers = old_headers
        logger.debug(f"TLSClient代理已更新: {proxy}")

    def update_headers(self, headers: Dict[str, str]) -> None:
        """更新默认请求头"""
        self.default_headers.update(headers)

    def clear_headers(self) -> None:
        """清空默认请求头"""
        self.default_headers = {}

    def close(self) -> None:
        """关闭客户端，释放资源"""
        try:
            self._session.close()
        except Exception as e:
            logger.debug(f"关闭TLSClient时出错: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def create_tls_client(
    browser: str = "chrome",
    version: str = "124",
    proxy: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = TLSClient.DEFAULT_TIMEOUT,
) -> TLSClient:
    """便捷工厂函数：根据浏览器类型和版本创建TLS客户端

    Args:
        browser: 浏览器类型（chrome, firefox, safari, edge）
        version: 浏览器版本（如124, 120）
        proxy: 代理URL
        headers: 默认请求头
        timeout: 请求超时时间（秒）

    Returns:
        TLSClient实例
    """
    # 组合浏览器类型和版本作为指纹标识符
    impersonate = f"{browser.lower()}{version}"
    return TLSClient(
        impersonate=impersonate,
        proxy=proxy,
        headers=headers,
        timeout=timeout,
    )
