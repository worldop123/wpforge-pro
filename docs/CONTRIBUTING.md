# WPForge 贡献指南

感谢您对 WPForge 项目的关注和贡献！本文档将帮助您了解如何参与项目开发。

## 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Pull Request 规范](#pull-request-规范)
- [Issue 规范](#issue-规范)
- [文档贡献](#文档贡献)
- [社区交流](#社区交流)

## 行为准则

参与本项目的所有人都应遵守以下行为准则：

- **友善待人**：尊重他人，保持友善和专业的态度
- **包容差异**：欢迎不同背景、经验水平的贡献者
- **建设性沟通**：专注于解决问题，避免人身攻击
- **尊重他人**：尊重不同的观点和经验
- **负责任**：对自己的言行负责

任何违反行为准则的行为都可能导致被禁止参与项目。

## 如何贡献

您可以通过以下方式为项目做出贡献：

### 1. 报告 Bug

如果您发现了 Bug，请提交 Issue 报告。在报告时请提供：

- 清晰的标题和描述
- 复现步骤
- 预期行为和实际行为
- 系统环境信息（操作系统、Python 版本、浏览器等）
- 相关的日志或截图

### 2. 提出功能建议

如果您有新的功能想法或改进建议，请提交 Issue 讨论。在建议时请说明：

- 功能描述
- 使用场景
- 预期效果
- 可能的实现方案（可选）

### 3. 提交代码

如果您想直接贡献代码，请按照开发流程提交 Pull Request。

### 4. 完善文档

文档也是项目的重要组成部分，您可以：

- 修复文档中的错误
- 补充缺失的文档
- 翻译文档
- 改进文档的可读性

### 5. 帮助他人

- 回答 Issue 中的问题
- 帮助审查 Pull Request
- 在社区中分享使用经验

## 开发流程

### 1. Fork 项目

首先，在 GitHub 上 Fork 本项目到您的账号下。

### 2. 克隆项目

```bash
git clone https://github.com/your-username/wpforge.git
cd wpforge
```

### 3. 添加上游仓库

```bash
git remote add upstream https://github.com/wpforge/wpforge.git
```

### 4. 创建分支

从 `main` 分支创建新的开发分支：

```bash
git checkout -b feature/your-feature-name
```

分支命名建议：
- `feature/xxx`: 新功能
- `fix/xxx`: Bug 修复
- `docs/xxx`: 文档更新
- `refactor/xxx`: 代码重构
- `perf/xxx`: 性能优化
- `test/xxx`: 测试相关

### 5. 开发

按照 [开发指南](DEVELOPMENT.md) 搭建开发环境，进行开发。

### 6. 运行测试

确保所有测试通过：

```bash
cd backend
pytest
```

### 7. 提交代码

按照 [提交规范](#提交规范) 提交代码。

### 8. 同步上游

在提交 PR 之前，请同步上游最新代码：

```bash
git fetch upstream
git rebase upstream/main
```

### 9. 提交 Pull Request

将您的分支推送到您的 Fork，然后提交 Pull Request。

## 代码规范

### Python 代码规范

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 规范
- 使用类型注解
- 文档字符串使用 Google 风格
- 代码格式化使用 black
- 导入排序使用 isort
- 单元测试覆盖率不低于 70%

#### 代码检查

```bash
# 安装检查工具
pip install black isort flake8 mypy

# 格式化代码
black .
isort .

# 代码检查
flake8 .
mypy app/
```

### 前端代码规范

- 遵循 Vue 3 风格指南
- 使用 TypeScript
- 组件命名使用 PascalCase
- 组合式 API 优先
- 使用 ESLint 和 Prettier

#### 代码检查

```bash
# 代码检查
npm run lint

# 代码格式化
npm run format
```

### 通用规范

- 保持代码简洁、易读
- 避免重复代码
- 适当添加注释
- 遵循 SOLID 原则
- 考虑性能和安全性

## 提交规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

### 提交格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整（不影响代码运行）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `build`: 构建系统或外部依赖变更
- `ci`: CI/CD 配置变更
- `chore`: 其他杂项

### Scope 范围（可选）

影响的模块或组件，例如：
- `api`: API 相关
- `frontend`: 前端相关
- `scraper`: 采集器相关
- `translation`: 翻译相关
- `seo`: SEO 相关
- `wordpress`: WordPress 相关

### Subject 主题

简短描述，不超过 50 个字符。

### Body 正文（可选）

详细描述，可以分成多行。

### Footer 页脚（可选）

- 关联 Issue：`Closes #123`
- 破坏性变更：`BREAKING CHANGE: 描述`

### 示例

```
feat(scraper): add support for Shopify product scraping

Add support for scraping product data from Shopify stores.
Includes automatic detection of Shopify platform and field mapping.

Closes #42
```

```
fix(api): fix pagination offset calculation

The offset calculation was incorrect when page number was 0.
Added validation to ensure page number is at least 1.

Closes #123
```

```
docs: update installation guide for Docker deployment

Add detailed instructions for Docker Compose deployment,
including environment configuration and troubleshooting.
```

## Pull Request 规范

### PR 标题

PR 标题遵循提交规范格式。

### PR 描述

在 PR 描述中请包含：

1. **变更类型**：新功能 / Bug 修复 / 文档更新 / 其他
2. **变更描述**：简要说明做了什么改动
3. **关联 Issue**：Closes #xxx
4. **测试情况**：是否添加了测试，测试结果如何
5. **截图/录屏**：如果是 UI 变更，请附上截图
6. **其他说明**：需要注意的事项或需要讨论的问题

### PR 模板

```markdown
## 变更类型

- [ ] 新功能
- [ ] Bug 修复
- [ ] 文档更新
- [ ] 代码重构
- [ ] 性能优化
- [ ] 其他

## 变更描述

简要描述本次变更的内容...

## 关联 Issue

Closes #xxx

## 测试情况

- [ ] 我已添加单元测试
- [ ] 所有测试通过
- [ ] 我已进行了手动测试

## 截图/录屏

（如果是 UI 变更，请附上截图或录屏）

## 其他说明

（需要注意的事项或需要讨论的问题）
```

### 审查流程

1. 提交 PR 后，自动运行 CI 检查
2. 至少需要一位维护者审查通过
3. 根据审查意见进行修改
4. 审查通过后，由维护者合并

### 合并策略

- 使用 Squash Merge 方式合并
- 合并前请确保分支已同步最新代码
- 确保所有检查通过

## Issue 规范

### Bug 报告模板

```markdown
## Bug 描述

清晰描述 Bug 是什么...

## 复现步骤

1. 前往 '...'
2. 点击 '...'
3. 滚动到 '...'
4. 看到错误

## 预期行为

描述你期望发生什么...

## 实际行为

描述实际发生了什么...

## 截图/录屏

如果可以的话，添加截图或录屏帮助解释问题。

## 环境信息

- 操作系统: [e.g. Windows 11, macOS 14, Ubuntu 22.04]
- 浏览器: [e.g. Chrome 120, Firefox 121]
- Python 版本: [e.g. 3.11.4]
- WPForge 版本: [e.g. 1.0.0]

## 其他信息

其他相关信息...
```

### 功能建议模板

```markdown
## 功能描述

清晰描述你想要的功能是什么...

## 使用场景

描述这个功能的使用场景...

## 预期效果

描述你期望的效果...

## 可能的实现方案

（可选）你有什么实现思路...

## 相关参考

（可选）类似功能的参考...

## 其他信息

其他相关信息...
```

## 文档贡献

文档也是项目的重要组成部分，欢迎贡献文档。

### 文档类型

- **README.md**: 项目介绍
- **docs/INSTALL.md**: 安装指南
- **docs/USER_GUIDE.md**: 使用手册
- **docs/API.md**: API 文档
- **docs/DEVELOPMENT.md**: 开发指南
- **docs/CONTRIBUTING.md**: 贡献指南
- **代码注释**: 代码中的文档字符串和注释

### 文档规范

- 使用 Markdown 格式
- 语言简洁明了
- 结构清晰，层次分明
- 代码示例完整可运行
- 中英文标点正确使用

### 翻译贡献

如果您想将文档翻译成其他语言：

1. 请先确认是否已有该语言的翻译
2. 在 `docs/` 下创建对应语言的子目录
3. 翻译所有文档文件
4. 保持文档结构和内容与英文版一致

## 社区交流

### 讨论区

使用 GitHub Discussions 进行交流：
- 💡 功能想法
- ❓ 问题求助
- 🤝 开发讨论
- 📢 公告发布

### 联系方式

- GitHub Issues: Bug 报告和功能建议
- GitHub Discussions: 一般讨论
- 邮件: contact@wpforge.com

## 常见问题

### Q: 我是新手，可以贡献代码吗？

当然可以！我们欢迎所有水平的贡献者。您可以从简单的问题开始，比如修复文档错误、添加注释、修复小 Bug 等。

### Q: 如何找到适合新手的任务？

查看带有 `good first issue` 或 `help wanted` 标签的 Issue，这些通常是比较容易上手的任务。

### Q: 贡献代码有什么奖励吗？

这是一个开源项目，没有金钱奖励。但是您可以：
- 提升编程技能
- 积累开源项目经验
- 结识志同道合的朋友
- 为社区做出贡献
- 在简历中展示

### Q: 我的 PR 多久会被审查？

我们会尽快审查所有 PR，通常在 3-7 天内。如果您的 PR 长时间未被审查，可以在评论中 @ 维护者。

### Q: 可以添加商业功能吗？

本项目采用 GPL v3 许可证，所有贡献的代码都将使用相同的许可证。不建议添加特定于商业的功能，但可以通过插件系统扩展。

## 致谢

感谢所有为 WPForge 做出贡献的人！

---

如果您有任何问题，欢迎随时提问。祝您贡献愉快！
