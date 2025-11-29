# 为 gac 贡献

[English](../en/CONTRIBUTING.md) | **简体中文** | [繁體中文](../zh-TW/CONTRIBUTING.md) | [日本語](../ja/CONTRIBUTING.md) | [한국어](../ko/CONTRIBUTING.md) | [हिन्दी](../hi/CONTRIBUTING.md) | [Tiếng Việt](../vi/CONTRIBUTING.md) | [Français](../fr/CONTRIBUTING.md) | [Русский](../ru/CONTRIBUTING.md) | [Español](../es/CONTRIBUTING.md) | [Português](../pt/CONTRIBUTING.md) | [Norsk](../no/CONTRIBUTING.md) | [Svenska](../sv/CONTRIBUTING.md) | [Deutsch](../de/CONTRIBUTING.md) | [Nederlands](../nl/CONTRIBUTING.md) | [Italiano](../it/CONTRIBUTING.md)

感谢你有兴趣为本项目做出贡献！我们非常感谢你的帮助。请遵循这些指南，使每个人的流程都顺畅。

## 目录

- [为 gac 贡献](#为-gac-贡献)
  - [目录](#目录)
  - [开发环境设置](#开发环境设置)
    - [快速设置](#快速设置)
    - [备选设置（如果你更喜欢分步骤）](#备选设置如果你更喜欢分步骤)
    - [可用命令](#可用命令)
  - [版本升级](#版本升级)
    - [如何升级版本](#如何升级版本)
    - [发布流程](#发布流程)
    - [使用 bump-my-version（可选）](#使用-bump-my-version可选)
  - [添加新的 AI 提供商](#添加新的-ai-提供商)
    - [添加新提供商的清单](#添加新提供商的清单)
    - [示例实现](#示例实现)
    - [关键点](#关键点)
  - [编码标准](#编码标准)
  - [Git 钩子（Lefthook）](#git-钩子lefthook)
    - [设置](#设置)
    - [跳过 Git 钩子](#跳过-git-钩子)
  - [测试指南](#测试指南)
    - [运行测试](#运行测试)
      - [提供商集成测试](#提供商集成测试)
  - [行为准则](#行为准则)
  - [许可证](#许可证)
  - [获取帮助](#获取帮助)

## 开发环境设置

本项目使用 `uv` 进行依赖管理，并提供 Makefile 用于常见开发任务：

### 快速设置

```bash
# 一条命令设置所有内容，包括 Lefthook 钩子
make dev
```

此命令将：

- 安装开发依赖项
- 安装 git 钩子
- 在所有文件上运行 Lefthook 钩子以修复任何现有问题

### 备选设置（如果你更喜欢分步骤）

```bash
# 创建虚拟环境并安装依赖项
make setup

# 安装开发依赖项
make dev

# 安装 Lefthook 钩子
brew install lefthook  # 或参见下面的文档了解替代方案
lefthook install
lefthook run pre-commit --all
```

### 可用命令

- `make setup` - 创建虚拟环境并安装所有依赖项
- `make dev` - **完整的开发设置** - 包括 Lefthook 钩子
- `make test` - 运行标准测试（不包括集成测试）
- `make test-integration` - 仅运行集成测试（需要 API 密钥）
- `make test-all` - 运行所有测试
- `make test-cov` - 运行带覆盖率报告的测试
- `make lint` - 检查代码质量（ruff、prettier、markdownlint）
- `make format` - 自动修复代码格式问题

## 版本升级

**重要**：当 PR 包含应该发布的更改时，应该在 `src/gac/__version__.py` 中包含版本升级。

### 如何升级版本

1. 编辑 `src/gac/__version__.py` 并增加版本号
2. 遵循 [语义化版本](https://semver.org/)：
   - **补丁**（1.6.X）：错误修复、小改进
   - **次要**（1.X.0）：新功能、向后兼容的更改（例如，添加新提供商）
   - **主要**（X.0.0）：破坏性更改

### 发布流程

通过推送版本标签触发发布：

1. 将带有版本升级的 PR 合并到 main
2. 创建标签：`git tag v1.6.1`
3. 推送标签：`git push origin v1.6.1`
4. GitHub Actions 自动发布到 PyPI

示例：

```python
# src/gac/__version__.py
__version__ = "1.6.1"  # 从 1.6.0 升级
```

### 使用 bump-my-version（可选）

如果你安装了 `bump-my-version`，你可以在本地使用它：

```bash
# 对于错误修复：
bump-my-version bump patch

# 对于新功能：
bump-my-version bump minor

# 对于破坏性更改：
bump-my-version bump major
```

## 添加新的 AI 提供商

添加新的 AI 提供商时，你需要更新代码库中的多个文件。遵循此综合清单：

### 添加新提供商的清单

- [ ] **1. 创建提供商实现**（`src/gac/providers/<provider_name>.py`）

  - 创建一个以提供商命名的新文件（例如，`minimax.py`）
  - 实现 `call_<provider>_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str`
  - 如果提供商支持，使用 OpenAI 兼容格式
  - 从环境变量 `<PROVIDER>_API_KEY` 处理 API 密钥
  - 包括使用 `AIError` 类型的适当错误处理：
    - `AIError.authentication_error()` 用于身份验证问题
    - `AIError.rate_limit_error()` 用于速率限制（HTTP 429）
    - `AIError.timeout_error()` 用于超时
    - `AIError.model_error()` 用于模型错误和空/null 内容
  - 设置 API 端点 URL
  - 对 HTTP 请求使用 120 秒超时

- [ ] **2. 在包中注册提供商**（`src/gac/providers/__init__.py`）

  - 添加导入：`from .<provider> import call_<provider>_api`
  - 添加到 `PROVIDER_REGISTRY` 字典：`"provider-name": call_<provider>_api`
  - 添加到 `__all__` 列表：`"call_<provider>_api"`

- [ ] **3. 更新示例配置**（`.gac.env.example`）

  - 以格式添加示例模型配置：`# GAC_MODEL=provider:model-name`
  - 添加 API 密钥条目：`# <PROVIDER>_API_KEY=your_key_here`
  - 保持条目按字母顺序排序
  - 如果适用，为可选密钥添加注释

- [ ] **4. 更新文档**（`README.md` 和 `docs/` 中所有 `README.md` 翻译）

  - 在所有 README 翻译的"支持的提供商"部分添加提供商名称
  - 在其要点中保持列表按字母顺序排序

- [ ] **5. 添加到交互式设置**（`src/gac/init_cli.py`）

  - 将元组添加到 `providers` 列表：`("Provider Name", "default-model-name")`
  - 保持列表按字母顺序排序
  - **重要**：如果你的提供商使用非标准的 API 密钥名称（不是自动生成的 `{PROVIDER_UPPERCASE}_API_KEY`），请添加特殊处理：

    ```python
    elif provider_key == "your-provider-key":
        api_key_name = "YOUR_CUSTOM_API_KEY_NAME"
    ```

    示例：`kimi-for-coding` 使用 `KIMI_CODING_API_KEY`，`moonshot-ai` 使用 `MOONSHOT_API_KEY`

- [ ] **6. 创建全面的测试**（`tests/providers/test_<provider>.py`）

  - 按照命名约定创建测试文件
  - 包括这些测试类：
    - `Test<Provider>Imports` - 测试模块和函数导入
    - `Test<Provider>APIKeyValidation` - 测试缺少 API 密钥错误
    - `Test<Provider>ProviderMocked(BaseProviderTest)` - 从 `BaseProviderTest` 继承以获得 9 个标准测试
    - `Test<Provider>EdgeCases` - 测试 null 内容和其他边缘情况
    - `Test<Provider>Integration` - 真实 API 调用测试（标记为 `@pytest.mark.integration`）
  - 在模拟测试类中实现所需的属性：
    - `provider_name` - 提供商名称（小写）
    - `provider_module` - 完整模块路径
    - `api_function` - API 函数引用
    - `api_key_env_var` - API 密钥的环境变量名称（对于本地提供商为 None）
    - `model_name` - 用于测试的默认模型名称
    - `success_response` - 模拟成功的 API 响应
    - `empty_content_response` - 模拟空内容响应

- [ ] **7. 升级版本**（`src/gac/__version__.py`）
  - 增加**次要**版本（例如，1.10.2 → 1.11.0）
  - 添加提供商是一个新功能，需要次要版本升级

### 示例实现

参见 MiniMax 提供商实现作为参考：

- 提供商：`src/gac/providers/minimax.py`
- 测试：`tests/providers/test_minimax.py`

### 关键点

1. **错误处理**：始终为不同的错误场景使用适当的 `AIError` 类型
2. **Null/空内容**：始终检查响应中的 `None` 和空字符串内容
3. **测试**：`BaseProviderTest` 类提供每个提供商应该继承的 9 个标准测试
4. **字母顺序**：保持提供商列表按字母顺序排序以便于维护
5. **API 密钥命名**：使用格式 `<PROVIDER>_API_KEY`（全大写，空格用下划线）
6. **提供商注册**：仅修改 `src/gac/providers/__init__.py` 和 `src/gac/init_cli.py`——`ai.py` 和 `ai_utils.py` 会自动从注册表中读取
7. **提供商名称格式**：对多词名称使用带连字符的小写（例如，"lm-studio"）
8. **版本升级**：添加提供商需要**次要**版本升级（新功能）

## 编码标准

- 目标 Python 3.10+（3.10、3.11、3.12、3.13、3.14）
- 对所有函数参数和返回值使用类型提示
- 保持代码清洁、紧凑和可读
- 避免不必要的复杂性
- 使用日志记录而不是 print 语句
- 格式化由 `ruff` 处理（linting、格式化和导入排序一体化工具；最大行长度：120）
- 使用 `pytest` 编写最少、有效的测试

## Git 钩子（Lefthook）

本项目使用 [Lefthook](https://github.com/evilmartians/lefthook) 保持代码质量检查快速且一致。配置的钩子镜像了我们以前的 pre-commit 设置：

- `ruff` - Python linting 和格式化（替代 black、isort 和 flake8）
- `markdownlint-cli2` - Markdown linting
- `prettier` - 文件格式化（markdown、yaml、json）
- `check-upstream` - 自定义钩子以检查上游更改

### 设置

**推荐方法：**

```bash
make dev
```

**手动设置（如果你更喜欢分步骤）：**

1. 安装 Lefthook（选择与你的设置匹配的选项）：

   ```sh
   brew install lefthook          # macOS (Homebrew)
   # 或
   cargo install lefthook         # Rust 工具链
   # 或
   asdf plugin add lefthook && asdf install lefthook latest
   ```

2. 安装 git 钩子：

   ```sh
   lefthook install
   ```

3. （可选）对所有文件运行：

   ```sh
   lefthook run pre-commit --all
   ```

钩子现在将在每次提交时自动运行。如果任何检查失败，你需要在提交之前修复问题。

### 跳过 Git 钩子

如果你需要暂时跳过 Lefthook 检查，使用 `--no-verify` 标志：

```sh
git commit --no-verify -m "你的提交信息"
```

注意：这应该仅在绝对必要时使用，因为它绕过了重要的代码质量检查。

## 测试指南

项目使用 pytest 进行测试。添加新功能或修复错误时，请包括涵盖你更改的测试。

注意，`scripts/` 目录包含用于无法使用 pytest 轻松测试的功能的测试脚本。
可以随意在此处添加脚本以测试复杂场景或难以使用标准 pytest 框架实现的集成测试。

### 运行测试

```sh
# 运行标准测试（不包括真实 API 调用的集成测试）
make test

# 仅运行提供商集成测试（需要 API 密钥）
make test-integration

# 运行所有测试，包括提供商集成测试
make test-all

# 运行带覆盖率的测试
make test-cov

# 运行特定测试文件
uv run -- pytest tests/test_prompt.py

# 运行特定测试
uv run -- pytest tests/test_prompt.py::TestExtractRepositoryContext::test_extract_repository_context_with_docstring
```

#### 提供商集成测试

提供商集成测试进行真实的 API 调用以验证提供商实现与实际 API 正确工作。这些测试标记为 `@pytest.mark.integration` 并默认跳过以：

- 避免在常规开发期间消耗 API 积分
- 防止未配置 API 密钥时测试失败
- 保持测试执行快速以进行快速迭代

要运行提供商集成测试：

1. **为你想测试的提供商设置 API 密钥**：

   ```sh
   export ANTHROPIC_API_KEY="your-key"
   export CEREBRAS_API_KEY="your-key"
   export GEMINI_API_KEY="your-key"
   export GROQ_API_KEY="your-key"
   export OPENAI_API_KEY="your-key"
   export OPENROUTER_API_KEY="your-key"
   export STREAMLAKE_API_KEY="your-key"
   export ZAI_API_KEY="your-key"
   # LM Studio 和 Ollama 需要运行本地实例
   # LM Studio 和 Ollama 的 API 密钥是可选的，除非你的部署强制执行身份验证
   ```

2. **运行提供商测试**：

   ```sh
   make test-integration
   ```

对于未配置 API 密钥的提供商，测试将跳过。这些测试有助于及早检测 API 更改并确保与提供商 API 的兼容性。

## 行为准则

要尊重和建设性。不会容忍骚扰或辱骂行为。

## 许可证

通过贡献，你同意你的贡献将在与项目相同的许可证下获得许可。

---

## 获取帮助

- 有关故障排除，请参阅 [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- 有关使用和 CLI 选项，请参阅 [USAGE.md](../USAGE.md)
- 有关许可证详细信息，请参阅 [../../LICENSE](../../LICENSE)

感谢你帮助改进 gac！
