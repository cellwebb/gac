<!-- markdownlint-disable MD013 -->
<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

# 🚀 Git Auto Commit (`gac`)

[![PyPI version](https://img.shields.io/pypi/v/gac.svg)](https://pypi.org/project/gac/)
[![Changelog](https://img.shields.io/badge/changelog-kittylog-10b981)](https://kittylog.app/c/thomwebb/gac)
[![Python](https://img.shields.io/badge/python-3.10--3.14-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://github.com/cellwebb/gac/actions/workflows/ci.yml/badge.svg)](https://github.com/cellwebb/gac/actions)
[![codecov](https://codecov.io/gh/cellwebb/gac/branch/main/graph/badge.svg)](https://app.codecov.io/gh/cellwebb/gac)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy-lang.org/)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](docs/zh-CN/CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](../../README.md) | **简体中文** | [繁體中文](../zh-TW/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [हिन्दी](../hi/README.md) | [Tiếng Việt](../vi/README.md) | [Français](../fr/README.md) | [Русский](../ru/README.md) | [Español](../es/README.md) | [Português](../pt/README.md) | [Norsk](../no/README.md) | [Svenska](../sv/README.md) | [Deutsch](../de/README.md) | [Nederlands](../nl/README.md) | [Italiano](../it/README.md)

**能理解你代码的 LLM 驱动的提交信息！**

**自动化你的提交！**用 `gac` 替代 `git commit -m "..."`，生成由大型语言模型创建的上下文相关、格式良好的提交信息！

---

## 你将获得

智能的、上下文相关的信息，解释你更改背后的**原因**：

![GAC 生成上下文提交信息](../../assets/gac-simple-usage.zh-CN.png)

---

</div>

<!-- markdownlint-enable MD033 MD036 -->

## 快速开始

### 无需安装直接使用 gac

```bash
uvx gac init   # 配置提供商、模型和语言
uvx gac  # 使用 LLM 生成并提交
```

就是这么简单！查看生成的信息并用 `y` 确认。

### 安装并使用 gac

```bash
uv tool install gac
gac init
gac
```

### 升级已安装的 gac

```bash
uv tool upgrade gac
```

---

## 核心特性

### 🌐 **支持的 25+ 提供商**

- **Anthropic** • **Azure OpenAI** • **Cerebras** • **ChatGPT (OAuth)** • **Chutes.ai**
- **Claude Code (OAuth)** • **DeepSeek** • **Fireworks** • **Gemini** • **GitHub Copilot**
- **Groq** • **Kimi for Coding** • **LM Studio** • **MiniMax.io** • **Mistral AI** • **Moonshot AI**
- **Ollama** • **OpenAI** • **OpenRouter** • **Qwen Cloud (CN & INTL)** • **Replicate**
- **Streamlake/Vanchin** • **Synthetic.new** • **Together AI** • **Wafer.ai**
- **Z.AI** • **Z.AI Coding** • **Custom Endpoints (Anthropic/OpenAI)**

### 🧠 **智能 LLM 分析**

- **理解意图**：分析代码结构、逻辑和模式，理解你更改背后的"原因"，而不仅仅是改变了什么
- **语义感知**：识别重构、错误修复、新特性和破坏性更改，生成上下文适当的信息
- **智能过滤**：优先考虑有意义的更改，同时忽略生成的文件、依赖项和构件
- **智能提交分组** - 使用 `--group` 自动将相关更改分组为多个逻辑提交

### 📝 **多种信息格式**

- **单行**（-o 标志）：遵循常规提交格式的单行提交信息
- **标准**（默认）：带有解释实现细节的要点的摘要
- **详细**（-v 标志）：包括动机、技术方法和影响分析的全面解释
- **50/72 规则**（--50-72 标志）：强制使用经典的提交信息格式，以便在 git log 和 GitHub UI 中获得最佳可读性
- **DCO/Signoff**（--signoff 标志）：添加 Signed-off-by 行以符合开发者原产地证书（Cherry Studio、Linux 内核及其他项目要求）

### 🌍 **多语言支持**

- **25+ 种语言**：生成英语、中文、日语、韩语、西班牙语、法语、德语等 20 多种语言的提交信息
- **灵活翻译**：选择保持常规提交前缀为英语以保持工具兼容性，或完全翻译它们
- **多种工作流**：使用 `gac language` 设置默认语言，或使用 `-l <语言>` 标志进行一次性覆盖
- **原生脚本支持**：完全支持非拉丁文字，包括中日韩、西里尔文、泰文等

### 💻 **开发者体验**

- **交互式反馈**：输入 `r` 重新生成，`e` 编辑（默认就地 TUI，或设置了 `$GAC_EDITOR` 时使用该编辑器），或直接输入你的反馈，如 `让它更短` 或 `专注于错误修复`
- **交互式提问**：使用 `--interactive` (`-i`) 回答有关你更改的定向问题，以获得更多上下文的提交信息
- **单命令工作流**：使用 `gac -ayp`（暂存所有、自动确认、推送）等标志完成完整工作流
- **Git 集成**：尊重 pre-commit 和 lefthook 钩子，在昂贵的 LLM 操作之前运行它们
- **MCP 服务器**：运行 `gac serve` 通过 [Model Context Protocol](https://modelcontextprotocol.io/) 向 AI 代理公开提交工具

### 📊 **使用统计**

- **追踪你的 gac 使用**：查看你用 gac 做了多少次提交、当前连续使用天数、每日/每周活动峰值和热门项目
- **Token 追踪**：按日、周、项目和模型统计的提示 + 完成令牌总数 — 令牌使用量也有高分奖杯
- **热门模型**：查看你最常用的模型以及每个模型消耗的令牌数
- **项目级统计**：使用 `gac stats projects` 查看所有仓库的统计信息
- **高分庆祝**：🏆 在你创造新的每日、每周、令牌或连续使用记录时获得奖杯；🥈 在追平记录时获得
- **设置时选择加入**：`gac init` 会询问是否启用统计，并详细说明存储的内容
- **随时退出**：设置 `GAC_DISABLE_STATS=true`（或 `1`/`yes`/`on`）以禁用。设置为 `false`/`0`/`no`（或取消设置）则保持统计启用
- **隐私优先**：本地存储在 `~/.gac_stats.json`。仅存储计数、日期、项目名称和模型名称 — 不含提交信息、代码或个人数据。无遥测

### 🛡️ **内置安全**

- **自动密钥检测**：在提交前扫描 API 密钥、密码和令牌
- **交互式保护**：在提交潜在敏感数据之前提示，并提供清晰的补救选项
- **智能过滤**：忽略示例文件、模板文件和占位符文本以减少误报

---

## 使用示例

### 基本工作流

```bash
# 暂存你的更改
git add .

# 使用 LLM 生成并提交
gac

# 查看 → y（提交）| n（取消）| r（重新生成）| e（编辑）| 或输入反馈
```

### 常用命令

| 命令            | 描述                                           |
| --------------- | ---------------------------------------------- |
| `gac`           | 生成提交信息                                   |
| `gac -y`        | 自动确认（无需查看）                           |
| `gac -a`        | 在生成提交信息之前暂存所有内容                 |
| `gac -S`        | 交互式选择要暂存的文件                         |
| `gac -o`        | 用于琐碎更改的单行信息                         |
| `gac -v`        | 包含动机、技术方法和影响分析的详细格式         |
| `gac -h "提示"` | 为 LLM 添加上下文（例如，`gac -h "错误修复"`） |
| `gac -s`        | 包括范围（例如，feat(auth):）                  |
| `gac -i`        | 询问有关更改的问题以获得更好的上下文           |
| `gac -g`        | 将更改分组为多个逻辑提交                       |
| `gac -p`        | 提交并推送                                     |
| `gac stats`     | 查看你的 gac 使用统计                          |

### 高级用户示例

```bash
# 一条命令完成完整工作流
# 查看你的提交统计
gac stats

# 所有项目的统计
gac stats projects

gac -ayp -h "发布准备"

# 带范围的详细解释
gac -v -s

# 小更改的快速单行
gac -o

# 将更改分组为逻辑相关的提交
gac -ag

# 带详细输出的交互模式用于详细解释
gac -iv

# 调试 LLM 看到的内容
gac --show-prompt

# 跳过安全扫描（谨慎使用）
gac --skip-secret-scan

# 添加 signoff 以符合 DCO（Cherry Studio、Linux 内核等）
gac --signoff
```

### 交互式反馈系统

对结果不满意？你有几个选项：

```bash
# 简单重新生成（无反馈）
r

# 编辑提交信息
e
# 默认：带 vi/emacs 键绑定的就地 TUI
# 按 Esc+Enter 或 Ctrl+S 提交，Ctrl+C 取消

# 设置 GAC_EDITOR 以打开您偏好的编辑器：
# GAC_EDITOR=code gac → 打开 VS Code（--wait 自动添加）
# GAC_EDITOR=vim gac → 打开 vim
# GAC_EDITOR=nano gac → 打开 nano

# 或者直接输入你的反馈！
让它更短并专注于性能改进
使用带范围的常规提交格式
解释安全影响

# 在空输入上按 Enter 再次查看提示
```

编辑功能（`e`）允许你精炼提交信息：

- **默认（就地 TUI）**：使用 vi/emacs 键绑定进行多行编辑 — 纠正拼写错误、调整措辞、重组
- **设置 `GAC_EDITOR`**：打开您偏好的编辑器（`code`、`vim`、`nano` 等） — 完整的编辑器功能，包括查找/替换、宏等

VS Code 等 GUI 编辑器会自动处理：gac 会插入 `--wait`，使进程在关闭编辑器标签页前一直阻塞。无需额外配置。

---

## 配置

运行 `gac init` 以交互方式配置你的提供商，或设置环境变量：

想要在之后仅更新提供商或模型且不修改语言？使用 `gac model`，它会跳过语言相关的提示。

```bash
# 示例配置
GAC_MODEL=anthropic:your-model-name
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

查看 `.gac.env.example` 了解所有可用选项。

**想要其他语言的提交信息？**运行 `gac language` 从 25 多种语言中选择，包括 Español、Français、日本語 等。

**想要自定义提交信息风格？**请参阅 [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/zh-CN/CUSTOM_SYSTEM_PROMPTS.md) 了解编写自定义系统提示的指导。

---

## 获取帮助

- **完整文档**：[USAGE.md](docs/zh-CN/USAGE.md) - 完整的 CLI 参考
- **MCP 服务器**：[MCP.md](MCP.md) - 将 GAC 用作 AI 代理的 MCP 服务器
- **Claude Code OAuth**：[docs/CLAUDE_CODE.md](docs/zh-CN/CLAUDE_CODE.md) - Claude Code 设置与认证
- **ChatGPT OAuth**：[docs/CHATGPT_OAUTH.md](docs/zh-CN/CHATGPT_OAUTH.md) - ChatGPT OAuth 设置与认证
- **自定义提示**：[CUSTOM_SYSTEM_PROMPTS.md](docs/zh-CN/CUSTOM_SYSTEM_PROMPTS.md) - 自定义提交信息风格
- **使用统计**：参见 `gac stats --help` 或[完整文档](docs/zh-CN/USAGE.md#使用统计)
- **故障排除**：[TROUBLESHOOTING.md](docs/zh-CN/TROUBLESHOOTING.md) - 常见问题和解决方案
- **贡献**：[CONTRIBUTING.md](docs/zh-CN/CONTRIBUTING.md) - 开发设置和指南

---

<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

[⭐ 在 GitHub 上给我们点星](https://github.com/cellwebb/gac) • [🐛 报告问题](https://github.com/cellwebb/gac/issues) • [📖 完整文档](docs/zh-CN/USAGE.md)

</div>

<!-- markdownlint-enable MD033 MD036 -->
