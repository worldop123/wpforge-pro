# WPForge 开发指南

## 目录

- [项目结构](#项目结构)
- [技术栈](#技术栈)
- [开发环境搭建](#开发环境搭建)
- [后端开发](#后端开发)
- [前端开发](#前端开发)
- [数据库迁移](#数据库迁移)
- [插件开发](#插件开发)
- [测试](#测试)
- [代码规范](#代码规范)
- [调试技巧](#调试技巧)

## 项目结构

```
wpforge/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API 路由
│   │   │   └── v1/         # v1 版本 API
│   │   ├── core/           # 核心模块
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── services/       # 业务服务
│   │   ├── tasks/          # Celery 任务
│   │   ├── utils/          # 工具函数
│   │   ├── middleware/     # 中间件
│   │   ├── plugins/        # 插件系统
│   │   └── main.py         # 应用入口
│   ├── alembic/            # 数据库迁移
│   ├── tests/              # 测试代码
│   └── requirements.txt    # Python 依赖
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/            # API 封装
│   │   ├── components/     # 组件库
│   │   ├── views/          # 页面视图
│   │   ├── store/          # Pinia 状态管理
│   │   ├── router/         # 路由配置
│   │   ├── utils/          # 工具函数
│   │   ├── assets/         # 静态资源
│   │   ├── types/          # TypeScript 类型
│   │   ├── App.vue         # 根组件
│   │   └── main.ts         # 应用入口
│   ├── package.json        # 前端依赖
│   └── vite.config.ts      # Vite 配置
├── docker/                 # Docker 配置
├── docs/                   # 文档
├── wordpress-plugin/       # WordPress 插件
├── README.md               # 项目说明
├── .env.example            # 环境变量示例
└── LICENSE                 # 许可证
```

## 技术栈

### 后端技术栈

- **编程语言**: Python 3.11+
- **Web 框架**: FastAPI
- **任务队列**: Celery + Redis
- **主数据库**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **数据验证**: Pydantic v2
- **数据库迁移**: Alembic
- **浏览器自动化**: Playwright
- **反检测插件**: playwright-stealth

### 前端技术栈

- **框架**: Vue 3
- **UI 组件库**: Element Plus
- **状态管理**: Pinia
- **构建工具**: Vite
- **路由**: Vue Router
- **语言**: TypeScript

### 部署技术栈

- **容器化**: Docker
- **反向代理**: Nginx
- **容器编排**: Docker Compose

## 开发环境搭建

### 1. 克隆项目

```bash
git clone https://github.com/wpforge/wpforge.git
cd wpforge
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库、Redis、AI API 等信息。

### 3. 启动依赖服务

使用 Docker 启动 PostgreSQL 和 Redis：

```bash
cd docker
docker-compose up -d postgres redis
```

或者手动安装 PostgreSQL 和 Redis。

### 4. 后端开发环境

```bash
# 创建虚拟环境
cd backend
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium

# 初始化数据库
alembic upgrade head

# 创建管理员
python -m app.commands create-admin --username admin --password admin123 --email admin@example.com

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 前端开发环境

```bash
cd ../frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 6. 启动 Celery Worker

```bash
cd backend
source venv/bin/activate

# 启动 Worker
celery -A app.tasks worker --loglevel=info --concurrency=2

# 启动 Beat (定时任务)
celery -A app.tasks beat --loglevel=info
```

## 后端开发

### 添加新的 API 端点

1. 在 `app/api/v1/` 下创建或编辑路由文件

```python
# app/api/v1/example.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import ExampleCreate, ExampleResponse
from app.services import example_service

router = APIRouter(prefix="/examples", tags=["examples"])


@router.get("", response_model=PaginatedResponse[ExampleResponse])
def get_examples(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取示例列表"""
    items, total = example_service.get_list(db, page=page, page_size=page_size)
    return PaginatedResponse(
        success=True,
        message="获取成功",
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
    )


@router.post("", response_model=SuccessResponse[ExampleResponse])
def create_example(
    example_in: ExampleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建示例"""
    example = example_service.create(db, obj_in=example_in, user_id=current_user.id)
    return SuccessResponse(success=True, message="创建成功", data=example)
```

2. 在 `app/api/v1/__init__.py` 中注册路由

```python
from fastapi import APIRouter

from app.api.v1 import auth, sites, products, tasks, scraping, example

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(sites.router)
api_router.include_router(products.router)
api_router.include_router(tasks.router)
api_router.include_router(scraping.router)
api_router.include_router(example.router)
```

### 添加新的数据库模型

1. 在 `app/models/` 下创建模型文件

```python
# app/models/example.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Example(BaseModel):
    __tablename__ = "examples"

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="examples")
```

2. 在 `app/models/__init__.py` 中导出模型

```python
from app.models.base import BaseModel
from app.models.user import User
from app.models.site import Site
from app.models.product import Product, ProductCategory
from app.models.task import Task, TaskLog
from app.models.example import Example

__all__ = [
    "BaseModel",
    "User",
    "Site",
    "Product",
    "ProductCategory",
    "Task",
    "TaskLog",
    "Example",
]
```

### 添加新的服务

在 `app/services/` 下创建服务文件：

```python
# app/services/example_service.py
from typing import List, Tuple
from sqlalchemy.orm import Session

from app.models.example import Example
from app.schemas import ExampleCreate, ExampleUpdate


class ExampleService:
    def get(self, db: Session, id: int) -> Example | None:
        return db.query(Example).filter(Example.id == id).first()

    def get_list(
        self, db: Session, *, page: int = 1, page_size: int = 20
    ) -> Tuple[List[Example], int]:
        query = db.query(Example)
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def create(self, db: Session, *, obj_in: ExampleCreate, user_id: int) -> Example:
        db_obj = Example(**obj_in.model_dump(), user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Example, obj_in: ExampleUpdate
    ) -> Example:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Example:
        obj = db.query(Example).get(id)
        db.delete(obj)
        db.commit()
        return obj


example_service = ExampleService()
```

### 添加 Celery 任务

在 `app/tasks/` 下创建任务文件：

```python
# app/tasks/example_tasks.py
from celery import shared_task
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services import example_service


@shared_task(bind=True, max_retries=3)
def process_example_task(self, example_id: int):
    """处理示例任务"""
    db: Session = SessionLocal()
    try:
        # 更新任务状态
        # ...

        # 执行业务逻辑
        example = example_service.get(db, id=example_id)
        if not example:
            raise ValueError(f"Example {example_id} not found")

        # 处理逻辑
        # ...

        return {"status": "success", "example_id": example_id}
    except Exception as e:
        # 记录错误
        # ...
        raise
    finally:
        db.close()
```

## 前端开发

### 添加新页面

1. 在 `src/views/` 下创建页面组件

```vue
<!-- src/views/Example.vue -->
<template>
  <div class="example-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>示例管理</span>
          <el-button type="primary" @click="handleAdd">新增</el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchData"
        @current-change="fetchData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getExampleList, deleteExample } from '@/api/example'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getExampleList({
      page: page.value,
      page_size: pageSize.value,
    })
    tableData.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  // 打开新增对话框
}

const handleEdit = (row: any) => {
  // 打开编辑对话框
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除吗？', '提示', {
      type: 'warning',
    })
    await deleteExample(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.example-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
```

2. 在 `src/router/index.ts` 中添加路由

```typescript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/Default.vue'),
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
      },
      {
        path: 'examples',
        name: 'Example',
        component: () => import('@/views/Example.vue'),
      },
      // ... 其他路由
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
```

### 添加 API 封装

在 `src/api/` 下创建 API 文件：

```typescript
// src/api/example.ts
import request from '@/utils/request'

export interface Example {
  id: number
  name: string
  description?: string
  created_at: string
  updated_at: string
}

export interface ExampleListParams {
  page?: number
  page_size?: number
  keyword?: string
}

export interface ExampleCreate {
  name: string
  description?: string
}

export interface ExampleUpdate {
  name?: string
  description?: string
}

export function getExampleList(params: ExampleListParams) {
  return request.get('/examples', { params })
}

export function getExample(id: number) {
  return request.get(`/examples/${id}`)
}

export function createExample(data: ExampleCreate) {
  return request.post('/examples', data)
}

export function updateExample(id: number, data: ExampleUpdate) {
  return request.put(`/examples/${id}`, data)
}

export function deleteExample(id: number) {
  return request.delete(`/examples/${id}`)
}
```

## 数据库迁移

### 创建迁移

```bash
cd backend
alembic revision --autogenerate -m "add_example_table"
```

### 执行迁移

```bash
alembic upgrade head
```

### 回滚迁移

```bash
# 回滚上一个版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade <revision_id>
```

### 查看迁移历史

```bash
alembic history
```

### 查看当前版本

```bash
alembic current
```

## 插件开发

WPForge 支持插件扩展，可以通过插件添加新功能。

### 插件结构

```
plugins/
└── my_plugin/
    ├── __init__.py
    ├── plugin.json
    ├── routes.py
    ├── services.py
    └── templates/
```

### 插件配置

```json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "description": "My custom plugin",
  "author": "Your Name",
  "dependencies": []
}
```

### 钩子系统

WPForge 使用钩子系统实现插件扩展：

```python
from app.core.hooks import add_action, add_filter

# 动作钩子
def my_custom_action(data):
    # 自定义逻辑
    pass

add_action('after_product_import', my_custom_action)

# 过滤器钩子
def my_custom_filter(content):
    # 修改内容
    return modified_content

add_filter('product_description', my_custom_filter)
```

## 测试

### 运行测试

```bash
cd backend

# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行特定测试文件
pytest tests/unit/test_example.py

# 运行特定测试函数
pytest tests/unit/test_example.py::test_get_example

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

### 编写测试

```python
# tests/unit/test_example.py
import pytest
from sqlalchemy.orm import Session

from app.models.example import Example
from app.services.example_service import example_service


def test_create_example(db: Session):
    """测试创建示例"""
    example_in = ExampleCreate(name="test", description="test description")
    example = example_service.create(db, obj_in=example_in, user_id=1)

    assert example.name == "test"
    assert example.description == "test description"
    assert example.id is not None


def test_get_example(db: Session):
    """测试获取示例"""
    # 先创建
    example_in = ExampleCreate(name="test")
    created = example_service.create(db, obj_in=example_in, user_id=1)

    # 再获取
    example = example_service.get(db, id=created.id)

    assert example is not None
    assert example.name == "test"
```

## 代码规范

### Python 代码规范

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 规范
- 使用类型注解
- 文档字符串使用 Google 风格
- 代码格式化使用 black
- 导入排序使用 isort

```python
# 示例
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.example import Example
from app.schemas import ExampleCreate


def get_examples(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    keyword: Optional[str] = None,
) -> tuple[List[Example], int]:
    """获取示例列表。

    Args:
        db: 数据库会话
        page: 页码
        page_size: 每页数量
        keyword: 搜索关键词

    Returns:
        示例列表和总数
    """
    query = db.query(Example)

    if keyword:
        query = query.filter(Example.name.ilike(f"%{keyword}%"))

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return items, total
```

### 前端代码规范

- 遵循 Vue 3 风格指南
- 使用 TypeScript
- 组件命名使用 PascalCase
- 组合式 API 优先
- 使用 ESLint 和 Prettier

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Props {
  title?: string
  count?: number
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Default Title',
  count: 0,
})

const emit = defineEmits<{
  (e: 'update', value: number): void
}>()

const localCount = ref(props.count)

const doubledCount = computed(() => localCount.value * 2)

const increment = () => {
  localCount.value++
  emit('update', localCount.value)
}

onMounted(() => {
  console.log('Component mounted')
})
</script>

<template>
  <div class="example-component">
    <h3>{{ title }}</h3>
    <p>Count: {{ localCount }}</p>
    <p>Doubled: {{ doubledCount }}</p>
    <button @click="increment">Increment</button>
  </div>
</template>

<style scoped>
.example-component {
  padding: 16px;
}
</style>
```

## 调试技巧

### 后端调试

1. **使用日志**

```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

2. **使用调试器**

```python
import pdb

def my_function():
    pdb.set_trace()  # 设置断点
    # ...
```

或使用 VS Code 调试器。

3. **查看 SQL 查询**

```python
# 开启 SQL 日志
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### 前端调试

1. **使用 Vue DevTools**

安装 Vue.js DevTools 浏览器扩展。

2. **使用 console**

```typescript
console.log('Message')
console.warn('Warning')
console.error('Error')
console.table(data)
console.time('label')
// ...
console.timeEnd('label')
```

3. **网络请求调试**

在浏览器开发者工具的 Network 面板中查看 API 请求。

### API 调试

使用 Swagger UI 调试 API：

- 访问 `http://localhost:8000/api/v1/docs`
- 或使用 Postman、curl 等工具

## 下一步

- 阅读 [安装指南](INSTALL.md) 了解如何安装系统
- 阅读 [使用手册](USER_GUIDE.md) 了解如何使用系统
- 阅读 [API 文档](API.md) 了解 API 接口
- 阅读 [贡献指南](CONTRIBUTING.md) 了解如何贡献代码
