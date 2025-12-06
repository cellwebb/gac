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
