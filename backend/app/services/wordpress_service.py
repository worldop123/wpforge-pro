"""
WordPress导入引擎服务 - WooCommerce全量导入、三种导入方式
支持断点续传、数据完整性校验、版本兼容性检测
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
import time
import json
import base64
import hashlib
from enum import Enum
from urllib.parse import urljoin

import httpx
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ImportMethod(str, Enum):
    """导入方式"""
    REST_API = "rest_api"  # REST API导入
    WP_CLI = "wp_cli"  # WP-CLI导入
    DATABASE = "database"  # 直接数据库写入
    PLUGIN = "plugin"  # 配套插件导入


class ImportStatus(str, Enum):
    """导入状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


@dataclass
class WPConfig:
    """WordPress配置"""
    url: str
    username: str
    app_password: str
    rest_api_url: Optional[str] = None
    wc_consumer_key: Optional[str] = None
    wc_consumer_secret: Optional[str] = None
    version: Optional[str] = None
    php_version: Optional[str] = None
    
    def get_rest_url(self) -> str:
        """获取REST API URL"""
        if self.rest_api_url:
            return self.rest_api_url
        return urljoin(self.url, "/wp-json/wp/v2/")
    
    def get_wc_rest_url(self) -> str:
        """获取WooCommerce REST API URL"""
        return urljoin(self.url, "/wp-json/wc/v3/")
    
    def get_auth_header(self) -> Dict[str, str]:
        """获取认证头"""
        auth = base64.b64encode(f"{self.username}:{self.app_password}".encode()).decode()
        return {"Authorization": f"Basic {auth}"}


@dataclass
class ImportResult:
    """导入结果"""
    status: ImportStatus
    total: int = 0
    imported: int = 0
    failed: int = 0
    skipped: int = 0
    errors: List[str] = field(default_factory=list)
    imported_ids: List[int] = field(default_factory=list)
    failed_items: List[Dict] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    @property
    def duration(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.imported / self.total


class WordPressCompatibilityChecker:
    """WordPress兼容性检测器"""
    
    def __init__(self):
        pass
    
    async def check_site_health(self, config: WPConfig) -> Dict:
        """检查站点健康状态"""
        results = {
            "wordpress_version": None,
            "php_version": None,
            "woocommerce_active": False,
            "woocommerce_version": None,
            "permalink_structure": None,
            "rest_api_available": False,
            "memory_limit": None,
            "max_execution_time": None,
            "upload_max_filesize": None,
            "issues": [],
            "warnings": [],
            "compatible": True,
        }
        
        try:
            # 检查REST API可用性
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    urljoin(config.url, "/wp-json/"),
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results["rest_api_available"] = True
                    results["wordpress_version"] = data.get("version")
                    
                    # 检查版本兼容性
                    wp_version = data.get("version", "0.0")
                    if self._version_compare(wp_version, "5.0") < 0:
                        results["issues"].append(f"WordPress版本过低: {wp_version}，需要5.0+")
                        results["compatible"] = False
                
                # 检查WooCommerce
                try:
                    wc_response = await client.get(
                        config.get_wc_rest_url() + "system_status",
                        auth=(config.wc_consumer_key, config.wc_consumer_secret),
                        timeout=10
                    )
                    
                    if wc_response.status_code == 200:
                        wc_data = wc_response.json()
                        results["woocommerce_active"] = True
                        results["woocommerce_version"] = wc_data.get("version")
                        results["php_version"] = wc_data.get("environment", {}).get("php_version")
                        results["memory_limit"] = wc_data.get("environment", {}).get("wp_memory_limit")
                        results["max_execution_time"] = wc_data.get("environment", {}).get("max_execution_time")
                        
                        # 检查PHP版本
                        php_version = wc_data.get("environment", {}).get("php_version", "0.0")
                        if self._version_compare(php_version, "7.4") < 0:
                            results["issues"].append(f"PHP版本过低: {php_version}，需要7.4+")
                            results["compatible"] = False
                        elif self._version_compare(php_version, "8.3") > 0:
                            results["warnings"].append(f"PHP版本过高: {php_version}，建议8.0-8.3")
                            
                except Exception as e:
                    results["warnings"].append(f"无法获取WooCommerce状态: {e}")
                
        except Exception as e:
            results["issues"].append(f"无法连接到WordPress站点: {e}")
            results["compatible"] = False
        
        return results
    
    def _version_compare(self, version1: str, version2: str) -> int:
        """比较版本号"""
        def parse_version(v):
            parts = []
            for part in v.split("."):
                try:
                    parts.append(int(part))
                except ValueError:
                    parts.append(0)
            return parts
        
        v1 = parse_version(version1)
        v2 = parse_version(version2)
        
        # 补齐长度
        max_len = max(len(v1), len(v2))
        v1.extend([0] * (max_len - len(v1)))
        v2.extend([0] * (max_len - len(v2)))
        
        for i in range(max_len):
            if v1[i] < v2[i]:
                return -1
            elif v1[i] > v2[i]:
                return 1
        
        return 0
    
    async def check_plugin_conflicts(self, config: WPConfig) -> List[str]:
        """检查插件冲突"""
        # 已知可能冲突的插件
        conflict_plugins = [
            "wordfence",
            "sucuri-scanner",
            "wp-super-cache",
            "w3-total-cache",
            "wp-rocket",
        ]
        
        warnings = []
        
        try:
            async with httpx.AsyncClient() as client:
                # 尝试获取插件列表（需要管理员权限）
                response = await client.get(
                    config.get_rest_url() + "plugins",
                    headers=config.get_auth_header(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    plugins = response.json()
                    active_plugins = [p.get("plugin", "") for p in plugins if p.get("status") == "active"]
                    
                    for plugin in conflict_plugins:
                        if any(plugin in p for p in active_plugins):
                            warnings.append(f"检测到可能冲突的插件: {plugin}，可能影响导入速度")
                            
        except Exception as e:
            logger.debug(f"Failed to check plugin conflicts: {e}")
        
        return warnings


class WooCommerceImporter:
    """WooCommerce产品导入器"""
    
    def __init__(self, config: WPConfig):
        self.config = config
        self.compatibility_checker = WordPressCompatibilityChecker()
        self._client = None
    
    def _get_client(self) -> httpx.AsyncClient:
        """获取HTTP客户端"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                auth=(self.config.wc_consumer_key, self.config.wc_consumer_secret),
                timeout=30.0
            )
        return self._client
    
    async def close(self):
        """关闭客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def check_connection(self) -> bool:
        """检查连接"""
        try:
            client = self._get_client()
            response = await client.get(
                self.config.get_wc_rest_url() + "system_status"
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"WooCommerce connection check failed: {e}")
            return False
    
    async def import_product(
        self,
        product_data: Dict,
        update_if_exists: bool = True,
        skip_images: bool = False
    ) -> Tuple[bool, Optional[int], Optional[str]]:
        """导入单个产品
        
        Returns:
            (success, product_id, error_message)
        """
        try:
            client = self._get_client()
            
            # 准备产品数据
            wc_product = self._convert_to_wc_product(product_data, skip_images)
            
            # 检查产品是否已存在（通过SKU）
            existing_id = None
            if wc_product.get("sku"):
                existing_id = await self._find_product_by_sku(wc_product["sku"])
            
            if existing_id and update_if_exists:
                # 更新现有产品
                response = await client.put(
                    f"{self.config.get_wc_rest_url()}products/{existing_id}",
                    json=wc_product
                )
                action = "updated"
            else:
                # 创建新产品
                response = await client.post(
                    f"{self.config.get_wc_rest_url()}products",
                    json=wc_product
                )
                action = "created"
            
            if response.status_code in (200, 201):
                product = response.json()
                logger.info(f"Product {action}: {product.get('id')} - {product.get('name')}")
                return True, product.get("id"), None
            else:
                error = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Product import failed: {error}")
                return False, None, error
                
        except Exception as e:
            error = str(e)
            logger.error(f"Product import error: {e}")
            return False, None, error
    
    def _convert_to_wc_product(self, product_data: Dict, skip_images: bool = False) -> Dict:
        """转换为WooCommerce产品格式"""
        wc_product = {}
        
        # 基础信息
        if "name" in product_data:
            wc_product["name"] = product_data["name"]
        elif "title" in product_data:
            wc_product["name"] = product_data["title"]
        
        if "description" in product_data:
            wc_product["description"] = product_data["description"]
        
        if "short_description" in product_data:
            wc_product["short_description"] = product_data["short_description"]
        
        if "sku" in product_data:
            wc_product["sku"] = product_data["sku"]
        
        # 价格
        if "regular_price" in product_data and product_data["regular_price"] is not None:
            wc_product["regular_price"] = str(product_data["regular_price"])
        
        if "sale_price" in product_data and product_data["sale_price"] is not None:
            wc_product["sale_price"] = str(product_data["sale_price"])
        
        if "price" in product_data and product_data["price"] is not None:
            if "regular_price" not in wc_product:
                wc_product["regular_price"] = str(product_data["price"])
        
        # 库存
        if "stock_quantity" in product_data:
            wc_product["stock_quantity"] = product_data["stock_quantity"]
            wc_product["manage_stock"] = True
        
        if "in_stock" in product_data:
            wc_product["in_stock"] = product_data["in_stock"]
        
        # 状态
        if "status" in product_data:
            wc_product["status"] = product_data["status"]
        else:
            wc_product["status"] = "publish"
        
        # 分类
        if "categories" in product_data and product_data["categories"]:
            wc_product["categories"] = [
                {"name": cat} if isinstance(cat, str) else cat
                for cat in product_data["categories"]
            ]
        
        # 标签
        if "tags" in product_data and product_data["tags"]:
            wc_product["tags"] = [
                {"name": tag} if isinstance(tag, str) else tag
                for tag in product_data["tags"]
            ]
        
        # 图片
        if not skip_images and "images" in product_data and product_data["images"]:
            wc_product["images"] = [
                {"src": img} if isinstance(img, str) else img
                for img in product_data["images"]
            ]
        
        # 属性
        if "attributes" in product_data and product_data["attributes"]:
            wc_product["attributes"] = product_data["attributes"]
        
        # 元数据
        if "meta_data" in product_data:
            wc_product["meta_data"] = product_data["meta_data"]
        
        # 产品类型
        if product_data.get("is_variable", False):
            wc_product["type"] = "variable"
        else:
            wc_product["type"] = "simple"
        
        return wc_product
    
    async def _find_product_by_sku(self, sku: str) -> Optional[int]:
        """通过SKU查找产品ID"""
        try:
            client = self._get_client()
            response = await client.get(
                f"{self.config.get_wc_rest_url()}products",
                params={"sku": sku, "per_page": 1}
            )
            
            if response.status_code == 200:
                products = response.json()
                if products:
                    return products[0]["id"]
        except Exception as e:
            logger.debug(f"Failed to find product by SKU: {e}")
        
        return None
    
    async def import_products_batch(
        self,
        products: List[Dict],
        update_if_exists: bool = True,
        skip_images: bool = False,
        delay_between: float = 0.5,
        progress_callback=None
    ) -> ImportResult:
        """批量导入产品"""
        result = ImportResult(
            status=ImportStatus.RUNNING,
            total=len(products)
        )
        
        for i, product in enumerate(products):
            try:
                success, product_id, error = await self.import_product(
                    product,
                    update_if_exists=update_if_exists,
                    skip_images=skip_images
                )
                
                if success:
                    result.imported += 1
                    result.imported_ids.append(product_id)
                else:
                    result.failed += 1
                    result.failed_items.append({
                        "index": i,
                        "product": product.get("name", product.get("title", "Unknown")),
                        "error": error
                    })
                    if error:
                        result.errors.append(error)
                
                # 更新进度
                if progress_callback:
                    progress_callback(i + 1, len(products))
                
                # 延迟
                if delay_between > 0 and i < len(products) - 1:
                    time.sleep(delay_between)
                    
            except Exception as e:
                result.failed += 1
                result.errors.append(str(e))
                result.failed_items.append({
                    "index": i,
                    "product": product.get("name", product.get("title", "Unknown")),
                    "error": str(e)
                })
        
        result.end_time = time.time()
        
        if result.failed == 0:
            result.status = ImportStatus.COMPLETED
        elif result.imported > 0:
            result.status = ImportStatus.PARTIAL
        else:
            result.status = ImportStatus.FAILED
        
        return result
    
    async def get_categories(self) -> List[Dict]:
        """获取产品分类"""
        try:
            client = self._get_client()
            response = await client.get(
                f"{self.config.get_wc_rest_url()}products/categories",
                params={"per_page": 100}
            )
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
        
        return []
    
    async def create_category(self, name: str, parent_id: Optional[int] = None) -> Optional[int]:
        """创建产品分类"""
        try:
            client = self._get_client()
            
            data = {"name": name}
            if parent_id:
                data["parent"] = parent_id
            
            response = await client.post(
                f"{self.config.get_wc_rest_url()}products/categories",
                json=data
            )
            
            if response.status_code == 201:
                return response.json()["id"]
        except Exception as e:
            logger.error(f"Failed to create category: {e}")
        
        return None
    
    async def import_categories(self, categories: List[Dict]) -> ImportResult:
        """导入分类"""
        result = ImportResult(
            status=ImportStatus.RUNNING,
            total=len(categories)
        )
        
        category_map = {}  # 原ID -> 新ID
        
        # 先导入一级分类
        for cat in categories:
            if not cat.get("parent"):
                try:
                    # 检查是否已存在
                    existing = await self._find_category_by_name(cat["name"])
                    if existing:
                        category_map[cat.get("id", cat["name"])] = existing
                        result.skipped += 1
                        continue
                    
                    new_id = await self.create_category(cat["name"])
                    if new_id:
                        category_map[cat.get("id", cat["name"])] = new_id
                        result.imported += 1
                        result.imported_ids.append(new_id)
                    else:
                        result.failed += 1
                except Exception as e:
                    result.failed += 1
                    result.errors.append(str(e))
        
        # 再导入子分类
        for cat in categories:
            if cat.get("parent"):
                try:
                    parent_id = category_map.get(cat["parent"])
                    if parent_id:
                        new_id = await self.create_category(cat["name"], parent_id)
                        if new_id:
                            category_map[cat.get("id", cat["name"])] = new_id
                            result.imported += 1
                            result.imported_ids.append(new_id)
                        else:
                            result.failed += 1
                    else:
                        result.failed += 1
                        result.errors.append(f"Parent category not found: {cat['parent']}")
                except Exception as e:
                    result.failed += 1
                    result.errors.append(str(e))
        
        result.end_time = time.time()
        result.status = ImportStatus.COMPLETED if result.failed == 0 else ImportStatus.PARTIAL
        
        return result
    
    async def _find_category_by_name(self, name: str) -> Optional[int]:
        """通过名称查找分类"""
        try:
            client = self._get_client()
            response = await client.get(
                f"{self.config.get_wc_rest_url()}products/categories",
                params={"search": name, "per_page": 5}
            )
            
            if response.status_code == 200:
                categories = response.json()
                for cat in categories:
                    if cat["name"].lower() == name.lower():
                        return cat["id"]
        except Exception as e:
            logger.debug(f"Failed to find category: {e}")
        
        return None


class WordPressMediaImporter:
    """WordPress媒体导入器"""
    
    def __init__(self, config: WPConfig):
        self.config = config
    
    async def import_image(self, image_url: str, alt_text: Optional[str] = None) -> Optional[int]:
        """导入图片到媒体库"""
        try:
            # 下载图片
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=30)
                if response.status_code != 200:
                    return None
                
                image_data = response.content
                filename = image_url.split("/")[-1].split("?")[0]
            
            # 上传到WordPress
            async with httpx.AsyncClient() as client:
                files = {"file": (filename, image_data, "image/jpeg")}
                data = {}
                if alt_text:
                    data["alt_text"] = alt_text
                
                response = await client.post(
                    urljoin(self.config.get_rest_url(), "media"),
                    headers=self.config.get_auth_header(),
                    files=files,
                    data=data
                )
                
                if response.status_code == 201:
                    return response.json()["id"]
                    
        except Exception as e:
            logger.error(f"Failed to import image: {e}")
        
        return None
    
    async def import_images_batch(self, image_urls: List[str]) -> List[Optional[int]]:
        """批量导入图片"""
        results = []
        for url in image_urls:
            media_id = await self.import_image(url)
            results.append(media_id)
            time.sleep(0.3)  # 避免请求过快
        return results


class ImportCheckpointManager:
    """导入断点续传管理器"""
    
    def __init__(self, import_id: str):
        self.import_id = import_id
        self.checkpoint_file = f"checkpoint_{import_id}.json"
        self._checkpoint = None
    
    def save_checkpoint(self, progress: Dict):
        """保存检查点"""
        import os
        checkpoint_dir = os.path.join(settings.UPLOAD_DIR, "checkpoints")
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        checkpoint_path = os.path.join(checkpoint_dir, self.checkpoint_file)
        
        checkpoint = {
            "import_id": self.import_id,
            "timestamp": time.time(),
            "progress": progress
        }
        
        with open(checkpoint_path, "w") as f:
            json.dump(checkpoint, f)
        
        self._checkpoint = checkpoint
    
    def load_checkpoint(self) -> Optional[Dict]:
        """加载检查点"""
        import os
        checkpoint_dir = os.path.join(settings.UPLOAD_DIR, "checkpoints")
        checkpoint_path = os.path.join(checkpoint_dir, self.checkpoint_file)
        
        if os.path.exists(checkpoint_path):
            with open(checkpoint_path, "r") as f:
                self._checkpoint = json.load(f)
            return self._checkpoint.get("progress")
        
        return None
    
    def clear_checkpoint(self):
        """清除检查点"""
        import os
        checkpoint_dir = os.path.join(settings.UPLOAD_DIR, "checkpoints")
        checkpoint_path = os.path.join(checkpoint_dir, self.checkpoint_file)
        
        if os.path.exists(checkpoint_path):
            os.remove(checkpoint_path)
        
        self._checkpoint = None


class DataIntegrityChecker:
    """数据完整性校验器"""
    
    def __init__(self):
        pass
    
    def validate_product(self, product_data: Dict) -> List[str]:
        """验证产品数据完整性"""
        errors = []
        warnings = []
        
        # 必填字段检查
        required_fields = ["name", "title"]
        has_name = any(field in product_data and product_data[field] for field in required_fields)
        if not has_name:
            errors.append("产品名称不能为空")
        
        # 价格检查
        if "price" in product_data and product_data["price"] is not None:
            try:
                price = float(product_data["price"])
                if price < 0:
                    errors.append("价格不能为负数")
            except (ValueError, TypeError):
                errors.append("价格格式无效")
        
        # SKU格式检查
        if "sku" in product_data and product_data["sku"]:
            if len(product_data["sku"]) > 100:
                warnings.append("SKU过长，可能导致问题")
        
        # 图片检查
        if "images" in product_data and product_data["images"]:
            if len(product_data["images"]) > 100:
                warnings.append("图片数量过多")
        
        return errors, warnings
    
    def check_import_consistency(
        self,
        source_products: List[Dict],
        imported_ids: List[int],
        wc_products: List[Dict]
    ) -> Dict:
        """检查导入一致性"""
        result = {
            "total_source": len(source_products),
            "total_imported": len(imported_ids),
            "missing": [],
            "mismatched": [],
            "integrity_score": 1.0
        }
        
        # 检查数量
        if len(source_products) > 0:
            result["integrity_score"] = len(imported_ids) / len(source_products)
        
        return result


# 工厂函数
def create_woocommerce_importer(
    url: str,
    username: str,
    app_password: str,
    wc_consumer_key: Optional[str] = None,
    wc_consumer_secret: Optional[str] = None,
    **kwargs
) -> WooCommerceImporter:
    """创建WooCommerce导入器"""
    config = WPConfig(
        url=url,
        username=username,
        app_password=app_password,
        wc_consumer_key=wc_consumer_key,
        wc_consumer_secret=wc_consumer_secret
    )
    return WooCommerceImporter(config)
