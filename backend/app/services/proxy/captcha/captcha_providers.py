"""
打码平台管理器
提供多个打码平台的统一接口和自动选择功能

支持的打码平台：
- 2Captcha（https://2captcha.com）
- Anti-Captcha（https://anti-captcha.com）
- CapMonster Cloud（https://capmonster.cloud）

所有平台均通过 httpx 进行真实的 API 调用，包含任务提交、结果轮询、错误处理。
"""
import base64
import time
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

import httpx

from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseCaptchaProvider(ABC):
    """打码平台基类"""

    # 默认轮询与超时配置
    POLL_INTERVAL = 5  # 轮询结果间隔（秒）
    MAX_WAIT = 120  # 最大等待时间（秒）
    REQUEST_TIMEOUT = 30  # 单次请求超时（秒）

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self._balance = 0.0
        self._solved_count = 0
        self._failed_count = 0
        # 每个平台复用一个 httpx.Client
        self._http_client = httpx.Client(timeout=self.REQUEST_TIMEOUT)

    @abstractmethod
    def solve_recaptcha_v2(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决reCAPTCHA v2"""
        pass

    @abstractmethod
    def solve_recaptcha_v3(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决reCAPTCHA v3"""
        pass

    @abstractmethod
    def solve_hcaptcha(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决hCaptcha"""
        pass

    @abstractmethod
    def solve_image_captcha(self, image_data: bytes, **kwargs) -> Optional[str]:
        """解决图片验证码"""
        pass

    def solve_funcaptcha(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决FunCaptcha（子类可覆盖）"""
        logger.warning(f"{getattr(self, 'name', 'provider')} does not support FunCaptcha")
        return None

    def solve_geetest(self, site_url: str, **kwargs) -> Optional[str]:
        """解决GeeTest（子类可覆盖）"""
        logger.warning(f"{getattr(self, 'name', 'provider')} does not support GeeTest")
        return None

    def solve_turnstile(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决Cloudflare Turnstile（子类可覆盖）"""
        logger.warning(f"{getattr(self, 'name', 'provider')} does not support Turnstile")
        return None

    def solve_slider_captcha(self, image_data: bytes, **kwargs) -> Optional[str]:
        """解决滑块验证码（子类可覆盖）"""
        logger.warning(f"{getattr(self, 'name', 'provider')} does not support slider captcha")
        return None

    def solve_click_captcha(self, image_data: bytes, **kwargs) -> Optional[str]:
        """解决点选验证码（子类可覆盖）"""
        logger.warning(f"{getattr(self, 'name', 'provider')} does not support click captcha")
        return None

    def get_balance(self) -> float:
        """获取余额"""
        return self._balance

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "balance": self._balance,
            "solved_count": self._solved_count,
            "failed_count": self._failed_count,
        }

    def report_bad(self, captcha_id: str) -> bool:
        """报告错误的验证码"""
        return False

    def _ensure_api_key(self) -> bool:
        """检查API密钥是否已配置"""
        if not self.api_key:
            logger.warning(f"{getattr(self, 'name', 'provider')} API key not configured")
            return False
        return True

    def close(self) -> None:
        """关闭HTTP客户端"""
        try:
            self._http_client.close()
        except Exception:
            pass


class TwoCaptchaProvider(BaseCaptchaProvider):
    """2Captcha打码平台

    API文档：https://2captcha.com/api-docs
    - 提交任务：POST https://api.2captcha.com/in.php
    - 获取结果：GET https://api.2captcha.com/res.php
    """

    def __init__(self, api_key: str = ""):
        super().__init__(api_key)
        self.name = "2captcha"
        self.base_url = "https://api.2captcha.com"

    def _submit(self, params: Dict[str, Any]) -> Optional[str]:
        """提交验证码任务，返回任务ID。失败返回None。"""
        if not self._ensure_api_key():
            return None

        params.setdefault("key", self.api_key)
        params.setdefault("json", 1)

        try:
            response = self._http_client.post(
                self.base_url + "/in.php",
                data=params,
            )
            data = response.json()
        except Exception as e:
            logger.error(f"2Captcha submit request failed: {e}")
            return None

        if data.get("status") == 1:
            return data.get("request")

        logger.warning(f"2Captcha submit error: {data.get('request')}")
        return None

    def _poll_result(self, captcha_id: str) -> Optional[str]:
        """轮询获取验证码结果。失败返回None。"""
        if not captcha_id:
            return None

        deadline = time.time() + self.MAX_WAIT
        while time.time() < deadline:
            try:
                response = self._http_client.get(
                    self.base_url + "/res.php",
                    params={
                        "key": self.api_key,
                        "action": "get",
                        "id": captcha_id,
                        "json": 1,
                    },
                )
                data = response.json()
            except Exception as e:
                logger.error(f"2Captcha poll request failed: {e}")
                time.sleep(self.POLL_INTERVAL)
                continue

            if data.get("status") == 1:
                return data.get("request")

            # CAPCHA_NOT_READY 表示还在处理中，继续轮询
            if data.get("request") == "CAPCHA_NOT_READY":
                time.sleep(self.POLL_INTERVAL)
                continue

            logger.warning(f"2Captcha poll error: {data.get('request')}")
            return None

        logger.warning("2Captcha poll timeout")
        return None

    def _solve(self, params: Dict[str, Any]) -> Optional[str]:
        """提交并轮询的通用流程"""
        captcha_id = self._submit(params)
        if not captcha_id:
            self._failed_count += 1
            return None

        result = self._poll_result(captcha_id)
        if result:
            self._solved_count += 1
            # 缓存最近一次任务ID，便于 report_bad
            self._last_captcha_id = captcha_id
        else:
            self._failed_count += 1
        return result

    def solve_recaptcha_v2(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决reCAPTCHA v2"""
        logger.info(f"2Captcha solving reCAPTCHA v2 for {site_url}")
        return self._solve({
            "method": "userrecaptcha",
            "googlekey": site_key,
            "pageurl": site_url,
        })

    def solve_recaptcha_v3(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决reCAPTCHA v3"""
        logger.info(f"2Captcha solving reCAPTCHA v3 for {site_url}")
        params = {
            "method": "userrecaptcha",
            "googlekey": site_key,
            "pageurl": site_url,
            "version": "v3",
        }
        # 可选的 action 和 min_score
        if kwargs.get("action"):
            params["action"] = kwargs["action"]
        if kwargs.get("min_score") is not None:
            params["min_score"] = kwargs["min_score"]
        return self._solve(params)

    def solve_hcaptcha(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决hCaptcha"""
        logger.info(f"2Captcha solving hCaptcha for {site_url}")
        return self._solve({
            "method": "hcaptcha",
            "sitekey": site_key,
            "pageurl": site_url,
        })

    def solve_turnstile(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决Cloudflare Turnstile"""
        logger.info(f"2Captcha solving Turnstile for {site_url}")
        return self._solve({
            "method": "turnstile",
            "sitekey": site_key,
            "pageurl": site_url,
        })

    def solve_funcaptcha(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决FunCaptcha"""
        logger.info(f"2Captcha solving FunCaptcha for {site_url}")
        return self._solve({
            "method": "funcaptcha",
            "publickey": site_key,
            "pageurl": site_url,
        })

    def solve_image_captcha(self, image_data: bytes, **kwargs) -> Optional[str]:
        """解决图片验证码"""
        logger.info("2Captcha solving image captcha")
        if not image_data:
            return None
        return self._solve({
            "method": "base64",
            "body": base64.b64encode(image_data).decode("ascii"),
        })

    def get_balance(self) -> float:
        """获取账户余额"""
        if not self._ensure_api_key():
            return self._balance
        try:
            response = self._http_client.get(
                self.base_url + "/res.php",
                params={"key": self.api_key, "action": "getbalance", "json": 1},
            )
            data = response.json()
            if data.get("status") == 1:
                self._balance = float(data.get("request", 0.0))
        except Exception as e:
            logger.error(f"2Captcha get_balance failed: {e}")
        return self._balance

    def report_bad(self, captcha_id: str) -> bool:
        """报告错误的验证码（用于退款）"""
        if not self._ensure_api_key():
            return False
        try:
            response = self._http_client.get(
                self.base_url + "/res.php",
                params={
                    "key": self.api_key,
                    "action": "reportbad",
                    "id": captcha_id,
                    "json": 1,
                },
            )
            data = response.json()
            if data.get("status") == 1:
                return True
            logger.warning(f"2Captcha report_bad error: {data.get('request')}")
        except Exception as e:
            logger.error(f"2Captcha report_bad failed: {e}")
        return False


class AntiCaptchaProvider(BaseCaptchaProvider):
    """Anti-Captcha打码平台

    API文档：https://anti-captcha.com/apidoc
    使用 JSON-RPC 风格接口：
    - createTask：提交任务
    - getTaskResult：轮询结果
    - getBalance：查询余额
    """

    def __init__(self, api_key: str = ""):
        super().__init__(api_key)
        self.name = "anti-captcha"
        self.base_url = "https://api.anti-captcha.com"

    def _create_task(self, task: Dict[str, Any]) -> Optional[int]:
        """提交任务，返回taskId。失败返回None。"""
        if not self._ensure_api_key():
            return None

        payload = {
            "clientKey": self.api_key,
            "task": task,
        }
        try:
            response = self._http_client.post(
                self.base_url + "/createTask",
                json=payload,
            )
            data = response.json()
        except Exception as e:
            logger.error(f"Anti-Captcha createTask request failed: {e}")
            return None

        if data.get("errorId", 1) == 0:
            return data.get("taskId")

        logger.warning(f"Anti-Captcha createTask error: {data.get('errorCode')} - {data.get('errorDescription')}")
        return None

    def _poll_result(self, task_id: int) -> Optional[Dict[str, Any]]:
        """轮询任务结果，返回solution字典。失败返回None。"""
        if task_id is None:
            return None

        deadline = time.time() + self.MAX_WAIT
        while time.time() < deadline:
            try:
                response = self._http_client.post(
                    self.base_url + "/getTaskResult",
                    json={
                        "clientKey": self.api_key,
                        "taskId": task_id,
                    },
                )
                data = response.json()
            except Exception as e:
                logger.error(f"Anti-Captcha poll request failed: {e}")
                time.sleep(self.POLL_INTERVAL)
                continue

            if data.get("errorId", 1) != 0:
                logger.warning(f"Anti-Captcha poll error: {data.get('errorCode')}")
                return None

            if data.get("status") == "ready":
                return data.get("solution")

            # processing 状态继续轮询
            time.sleep(self.POLL_INTERVAL)

        logger.warning("Anti-Captcha poll timeout")
        return None

    def _solve(self, task: Dict[str, Any], solution_key: str = "gRecaptchaResponse") -> Optional[str]:
        """提交并轮询的通用流程"""
        task_id = self._create_task(task)
        if task_id is None:
            self._failed_count += 1
            return None

        solution = self._poll_result(task_id)
        if solution and solution_key in solution:
            self._solved_count += 1
            self._last_task_id = task_id
            return solution[solution_key]

        self._failed_count += 1
        return None

    def solve_recaptcha_v2(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决reCAPTCHA v2"""
        logger.info(f"Anti-Captcha solving reCAPTCHA v2 for {site_url}")
        task = {
            "type": "NoCaptchaTaskProxyless",
            "websiteURL": site_url,
            "websiteKey": site_key,
        }
        return self._solve(task)

    def solve_recaptcha_v3(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决reCAPTCHA v3"""
        logger.info(f"Anti-Captcha solving reCAPTCHA v3 for {site_url}")
        task = {
            "type": "RecaptchaV3TaskProxyless",
            "websiteURL": site_url,
            "websiteKey": site_key,
            "pageAction": kwargs.get("action", ""),
            "minScore": kwargs.get("min_score", 0.7),
        }
        return self._solve(task)

    def solve_hcaptcha(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决hCaptcha"""
        logger.info(f"Anti-Captcha solving hCaptcha for {site_url}")
        task = {
            "type": "HCaptchaTaskProxyless",
            "websiteURL": site_url,
            "websiteKey": site_key,
        }
        return self._solve(task)

    def solve_turnstile(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决Cloudflare Turnstile"""
        logger.info(f"Anti-Captcha solving Turnstile for {site_url}")
        task = {
            "type": "TurnstileTaskProxyless",
            "websiteURL": site_url,
            "websiteKey": site_key,
        }
        return self._solve(task)

    def solve_funcaptcha(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决FunCaptcha"""
        logger.info(f"Anti-Captcha solving FunCaptcha for {site_url}")
        task = {
            "type": "FunCaptchaTaskProxyless",
            "websiteURL": site_url,
            "websitePublicKey": site_key,
        }
        return self._solve(task, solution_key="token")

    def solve_image_captcha(self, image_data: bytes, **kwargs) -> Optional[str]:
        """解决图片验证码"""
        logger.info("Anti-Captcha solving image captcha")
        if not image_data:
            return None
        task = {
            "type": "ImageToTextTask",
            "body": base64.b64encode(image_data).decode("ascii"),
            "case": kwargs.get("case", True),
        }
        return self._solve(task, solution_key="text")

    def get_balance(self) -> float:
        """获取账户余额"""
        if not self._ensure_api_key():
            return self._balance
        try:
            response = self._http_client.post(
                self.base_url + "/getBalance",
                json={"clientKey": self.api_key},
            )
            data = response.json()
            if data.get("errorId", 1) == 0:
                self._balance = float(data.get("balance", 0.0))
        except Exception as e:
            logger.error(f"Anti-Captcha get_balance failed: {e}")
        return self._balance

    def report_bad(self, captcha_id: str) -> bool:
        """报告错误的验证码（用于退款）"""
        if not self._ensure_api_key():
            return False
        try:
            response = self._http_client.post(
                self.base_url + "/reportIncorrectRecaptcha",
                json={
                    "clientKey": self.api_key,
                    "taskId": int(captcha_id),
                },
            )
            data = response.json()
            if data.get("errorId", 1) == 0:
                return True
            logger.warning(f"Anti-Captcha report_bad error: {data.get('errorCode')}")
        except Exception as e:
            logger.error(f"Anti-Captcha report_bad failed: {e}")
        return False


class CapMonsterProvider(BaseCaptchaProvider):
    """CapMonster Cloud打码平台

    API文档：https://capmonster.cloud/en/apidoc
    接口风格与 Anti-Captcha 兼容（JSON-RPC）。
    """

    def __init__(self, api_key: str = ""):
        super().__init__(api_key)
        self.name = "capmonster"
        self.base_url = "https://api.capmonster.cloud"

    def _create_task(self, task: Dict[str, Any]) -> Optional[str]:
        """提交任务，返回taskId。失败返回None。"""
        if not self._ensure_api_key():
            return None
        try:
            response = self._http_client.post(
                self.base_url + "/createTask",
                json={"clientKey": self.api_key, "task": task},
            )
            data = response.json()
        except Exception as e:
            logger.error(f"CapMonster createTask request failed: {e}")
            return None

        if data.get("errorId", 1) == 0:
            return data.get("taskId")

        logger.warning(f"CapMonster createTask error: {data.get('errorCode')}")
        return None

    def _poll_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """轮询任务结果。失败返回None。"""
        if task_id is None:
            return None
        deadline = time.time() + self.MAX_WAIT
        while time.time() < deadline:
            try:
                response = self._http_client.post(
                    self.base_url + "/getTaskResult",
                    json={"clientKey": self.api_key, "taskId": task_id},
                )
                data = response.json()
            except Exception as e:
                logger.error(f"CapMonster poll request failed: {e}")
                time.sleep(self.POLL_INTERVAL)
                continue

            if data.get("errorId", 1) != 0:
                logger.warning(f"CapMonster poll error: {data.get('errorCode')}")
                return None

            if data.get("status") == "ready":
                return data.get("solution")

            time.sleep(self.POLL_INTERVAL)

        logger.warning("CapMonster poll timeout")
        return None

    def _solve(self, task: Dict[str, Any], solution_key: str = "gRecaptchaResponse") -> Optional[str]:
        """提交并轮询的通用流程"""
        task_id = self._create_task(task)
        if task_id is None:
            self._failed_count += 1
            return None

        solution = self._poll_result(task_id)
        if solution and solution_key in solution:
            self._solved_count += 1
            return solution[solution_key]

        self._failed_count += 1
        return None

    def solve_recaptcha_v2(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决reCAPTCHA v2"""
        logger.info(f"CapMonster solving reCAPTCHA v2 for {site_url}")
        task = {
            "type": "NoCaptchaTaskProxyless",
            "websiteURL": site_url,
            "websiteKey": site_key,
        }
        return self._solve(task)

    def solve_recaptcha_v3(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决reCAPTCHA v3"""
        logger.info(f"CapMonster solving reCAPTCHA v3 for {site_url}")
        task = {
            "type": "RecaptchaV3TaskProxyless",
            "websiteURL": site_url,
            "websiteKey": site_key,
            "pageAction": kwargs.get("action", ""),
            "minScore": kwargs.get("min_score", 0.7),
        }
        return self._solve(task)

    def solve_hcaptcha(self, site_url: str, site_key: str, **kwargs) -> Optional[str]:
        """解决hCaptcha"""
        logger.info(f"CapMonster solving hCaptcha for {site_url}")
        task = {
            "type": "HCaptchaTaskProxyless",
            "websiteURL": site_url,
            "websiteKey": site_key,
        }
        return self._solve(task)

    def solve_image_captcha(self, image_data: bytes, **kwargs) -> Optional[str]:
        """解决图片验证码"""
        logger.info("CapMonster solving image captcha")
        if not image_data:
            return None
        task = {
            "type": "ImageToTextTask",
            "body": base64.b64encode(image_data).decode("ascii"),
        }
        return self._solve(task, solution_key="text")

    def get_balance(self) -> float:
        """获取账户余额"""
        if not self._ensure_api_key():
            return self._balance
        try:
            response = self._http_client.post(
                self.base_url + "/getBalance",
                json={"clientKey": self.api_key},
            )
            data = response.json()
            if data.get("errorId", 1) == 0:
                self._balance = float(data.get("balance", 0.0))
        except Exception as e:
            logger.error(f"CapMonster get_balance failed: {e}")
        return self._balance

    def report_bad(self, captcha_id: str) -> bool:
        """报告错误的验证码（用于退款）"""
        if not self._ensure_api_key():
            return False
        try:
            response = self._http_client.post(
                self.base_url + "/reportIncorrectRecaptcha",
                json={"clientKey": self.api_key, "taskId": int(captcha_id)},
            )
            data = response.json()
            if data.get("errorId", 1) == 0:
                return True
        except Exception as e:
            logger.error(f"CapMonster report_bad failed: {e}")
        return False


class CaptchaProviderManager:
    """打码平台管理器"""

    def __init__(self):
        self._providers: Dict[str, BaseCaptchaProvider] = {}
        self._current_provider: Optional[str] = None
        self._auto_select: bool = True
        self._priority_order: List[str] = []

    def add_provider(self, name: str, provider: BaseCaptchaProvider):
        """添加打码平台"""
        self._providers[name] = provider
        if self._current_provider is None:
            self._current_provider = name
        if name not in self._priority_order:
            self._priority_order.append(name)

    def remove_provider(self, name: str):
        """移除打码平台"""
        if name in self._providers:
            del self._providers[name]
        if name in self._priority_order:
            self._priority_order.remove(name)
        if self._current_provider == name:
            self._current_provider = self._priority_order[0] if self._priority_order else None

    def set_priority_order(self, order: List[str]):
        """设置优先级顺序"""
        self._priority_order = order

    def set_auto_select(self, enabled: bool):
        """设置是否自动选择平台"""
        self._auto_select = enabled

    def get_current_provider(self) -> Optional[BaseCaptchaProvider]:
        """获取当前使用的平台"""
        if self._current_provider and self._current_provider in self._providers:
            return self._providers[self._current_provider]
        return None

    def select_best_provider(self, captcha_type: str = "") -> Optional[str]:
        """
        选择最佳的打码平台

        Args:
            captcha_type: 验证码类型

        Returns:
            平台名称
        """
        if not self._auto_select:
            return self._current_provider

        # 按优先级顺序选择第一个可用的
        for name in self._priority_order:
            if name in self._providers:
                return name

        return None

    def get_provider(self, name: str) -> Optional[BaseCaptchaProvider]:
        """获取指定的平台"""
        return self._providers.get(name)

    def get_all_providers(self) -> Dict[str, BaseCaptchaProvider]:
        """获取所有平台"""
        return self._providers.copy()

    def get_provider_names(self) -> List[str]:
        """获取所有平台名称"""
        return list(self._providers.keys())

    def get_all_balances(self) -> Dict[str, float]:
        """获取所有平台的余额"""
        balances = {}
        for name, provider in self._providers.items():
            balances[name] = provider.get_balance()
        return balances

    def get_total_balance(self) -> float:
        """获取总余额"""
        return sum(p.get_balance() for p in self._providers.values())

    def check_health(self) -> Dict[str, bool]:
        """检查所有平台的健康状态"""
        health = {}
        for name, provider in self._providers.items():
            # 通过查询余额判断平台是否可用（密钥有效且可连通）
            try:
                provider.get_balance()
                health[name] = True
            except Exception:
                health[name] = False
        return health
