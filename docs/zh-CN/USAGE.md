# gac 命令行使用

[English](../en/USAGE.md) | **简体中文** | [繁體中文](../zh-TW/USAGE.md) | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | [Tiếng Việt](../vi/USAGE.md) | [Français](../fr/USAGE.md) | [Русский](../ru/USAGE.md) | [Español](../es/USAGE.md) | [Português](../pt/USAGE.md) | [Norsk](../no/USAGE.md) | [Svenska](../sv/USAGE.md) | [Deutsch](../de/USAGE.md) | [Nederlands](../nl/USAGE.md) | [Italiano](../it/USAGE.md)

本文档介绍了 `gac` CLI 工具的所有可用标志和选项。

## 目录

- [gac 命令行使用](#gac-命令行使用)
  - [目录](#目录)
  - [基本使用](#基本使用)
  - [核心工作流标志](#核心工作流标志)
  - [信息定制](#信息定制)
  - [输出和详细程度](#输出和详细程度)
  - [帮助和版本](#帮助和版本)
  - [示例工作流](#示例工作流)
  - [高级](#高级)
    - [脚本集成和外部处理](#脚本集成和外部处理)
    - [跳过 Pre-commit 和 Lefthook 钩子](#跳过-pre-commit-和-lefthook-钩子)
    - [安全扫描](#安全扫描)
    - [SSL 证书验证](#ssl-证书验证)
  - [配置说明](#配置说明)
    - [高级配置选项](#高级配置选项)
    - [配置子命令](#配置子命令)
  - [交互模式](#交互模式)
    - [工作原理](#工作原理)
    - [何时使用交互模式](#何时使用交互模式)
    - [使用示例](#使用示例)
    - [问答工作流](#问答工作流)
    - [与其他标志组合](#与其他标志组合)
    - [最佳实践](#最佳实践)
  - [获取帮助](#获取帮助)

## 基本使用

```sh
gac init
# 然后按照提示以交互方式配置你的提供商、模型和 API 密钥
gac
```

为暂存的更改生成 LLM 驱动的提交信息并提示确认。确认提示接受：

- `y` 或 `yes` - 继续提交
- `n` 或 `no` - 取消提交
- `r` 或 `reroll` - 使用相同的上下文重新生成提交信息
- `e` 或 `edit` - 使用丰富的终端编辑就地编辑提交信息（vi/emacs 键绑定）
- 任何其他文本 - 使用该文本作为反馈重新生成（例如，`让它更短`，`专注于性能`）
- 空输入（只按 Enter）- 再次显示提示

---

## 核心工作流标志

| 标志 / 选项          | 简写 | 描述                                   |
| -------------------- | ---- | -------------------------------------- |
| `--add-all`          | `-a` | 在提交之前暂存所有更改                 |
| `--group`            | `-g` | 将暂存的更改分组为多个逻辑提交         |
| `--push`             | `-p` | 提交后推送更改到远程                   |
| `--yes`              | `-y` | 自动确认提交而不提示                   |
| `--dry-run`          |      | 显示会发生什么而不进行任何更改         |
| `--message-only`     |      | 仅输出生成的提交信息，而不实际执行提交 |
| `--no-verify`        |      | 提交时跳过 pre-commit 和 lefthook 钩子 |
| `--skip-secret-scan` |      | 跳过暂存更改中的密钥安全扫描           |
| `--no-verify-ssl`    |      | 跳过 SSL 证书验证（适用于企业代理）    |
| `--interactive`      | `-i` | 就更改提问以获得更好的提交             |

**注意：**组合 `-a` 和 `-g`（即 `-ag`）以先暂存所有更改，然后将它们分组为提交。

**注意：**使用 `--group` 时，最大输出令牌限制会根据正在提交的文件数量自动缩放（1-9 个文件为 2 倍，10-19 个文件为 3 倍，20-29 个文件为 4 倍，30+ 个文件为 5 倍）。这确保 LLM 有足够的令牌来生成所有分组提交而不会被截断，即使对于大型变更集也是如此。

**注意：**`--message-only` 和 `--group` 互斥。需要获取提交信息供外部处理时请使用 `--message-only`，而在当前 git 工作流中组织多个提交时请使用 `--group`。

**注意：**`--interactive` 标志通过就你的更改提问，为 LLM 提供额外上下文，从而产生更准确、更详细的提交信息。这特别适用于复杂更改，或者当你希望确保提交信息捕捉到工作的完整上下文时。

## 信息定制

| 标志 / 选项         | 简写 | 描述                                                   |
| ------------------- | ---- | ------------------------------------------------------ |
| `--one-liner`       | `-o` | 生成单行提交信息                                       |
| `--verbose`         | `-v` | 生成包含动机、架构和影响的详细提交信息                 |
| `--hint <text>`     | `-h` | 添加提示以引导 LLM                                     |
| `--model <model>`   | `-m` | 指定用于此次提交的模型                                 |
| `--language <lang>` | `-l` | 覆盖语言（名称或代码：'Spanish'、'es'、'zh-CN'、'ja'） |
| `--scope`           | `-s` | 为提交推断适当的范围                                   |

**注意：**你可以通过在确认提示符处简单地输入来交互式提供反馈 - 无需前缀 'r'。输入 `r` 进行简单的重新生成，`e` 使用 vi/emacs 键绑定就地编辑，或直接输入你的反馈，如 `让它更短`。

## 输出和详细程度

| 标志 / 选项           | 简写 | 描述                                        |
| --------------------- | ---- | ------------------------------------------- |
| `--quiet`             | `-q` | 抑制除错误外的所有输出                      |
| `--log-level <level>` |      | 设置日志级别（debug、info、warning、error） |
| `--show-prompt`       |      | 打印用于提交信息生成的 LLM 提示             |

## 帮助和版本

| 标志 / 选项 | 简写 | 描述                |
| ----------- | ---- | ------------------- |
| `--version` |      | 显示 gac 版本并退出 |
| `--help`    |      | 显示帮助信息并退出  |

---

## 示例工作流

- **暂存所有更改并提交：**

  ```sh
  gac -a
  ```

- **一步提交并推送：**

  ```sh
  gac -ap
  ```

- **生成单行提交信息：**

  ```sh
  gac -o
  ```

- **生成包含结构化部分的详细提交信息：**

  ```sh
  gac -v
  ```

- **为 LLM 添加提示：**

  ```sh
  gac -h "重构身份验证逻辑"
  ```

- **为提交推断范围：**

  ```sh
  gac -s
  ```

- **将暂存的更改分组为逻辑提交：**

  ```sh
  gac -g
  # 仅分组你已经暂存的文件
  ```

- **分组所有更改（暂存 + 未暂存）并自动确认：**

  ```sh
  gac -agy
  # 暂存所有内容，分组，并自动确认
  ```

- **仅为此次提交使用特定模型：**

  ```sh
  gac -m anthropic:claude-haiku-4-5
  ```

- **以特定语言生成提交信息：**

  ```sh
  # 使用语言代码（较短）
  gac -l zh-CN
  gac -l ja
  gac -l es

  # 使用完整名称
  gac -l "Simplified Chinese"
  gac -l Japanese
  gac -l Spanish
  ```

- **演练（查看会发生什么）：**

  ```sh
  gac --dry-run
  ```

- **仅获取提交信息（用于脚本集成）：**

  ```sh
  gac --message-only
  # 输出示例：feat: add user authentication system
  ```

- **以单行格式获取提交信息：**

  ```sh
  gac --message-only --one-liner
  # 输出示例：feat: add user authentication system
  ```

- **使用交互模式提供上下文：**

  ```sh
  gac -i
  # 这些更改的主要目的是什么？
  # 你在解决什么问题？
  # 有什么实现细节值得一提吗？
  ```

- **交互模式配合详细输出：**

  ```sh
  gac -i -v
  # 提问并生成详细的提交信息
  ```

## 高级

- 组合标志以获得更强大的工作流（例如，`gac -ayp` 以暂存、自动确认和推送）
- 使用 `--show-prompt` 调试或查看发送给 LLM 的提示
- 使用 `--log-level` 或 `--quiet` 调整详细程度
- 使用 `--message-only` 进行脚本集成和自动化工作流

### 脚本集成和外部处理

`--message-only` 标志专为脚本集成和外部工具工作流设计。它仅输出原始提交信息，不包含任何额外的格式、加载动画或 UI 元素。

**适用场景：**

- **Agent 集成：** 让 AI Agent 获取提交信息并自行处理提交
- **替代版本控制系统：** 在其他版本控制系统（Mercurial、Jujutsu 等）中使用生成的消息
- **自定义提交工作流：** 在执行提交前对消息进行处理或修改
- **CI/CD 流水线：** 提取提交信息以用于自动化流程

**脚本使用示例：**

```sh
#!/bin/bash
# 获取提交信息并配合自定义提交函数使用
MESSAGE=$(gac --message-only --add-all --yes)
git commit -m "$MESSAGE"
```

```python
# Python 集成示例
import subprocess


def get_commit_message() -> str:
    result = subprocess.run(
        ["gac", "--message-only", "--yes"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


message = get_commit_message()
print(f"Generated message: {message}")
```

**适用于脚本的关键特性：**

- 输出干净，不含 Rich 格式或加载动画
- 自动跳过确认提示
- 不会实际执行 git 提交
- 可与 `--one-liner` 配合以获取简化输出
- 可与 `--hint`、`--model` 等其他标志组合使用

### 跳过 Pre-commit 和 Lefthook 钩子

`--no-verify` 标志允许你跳过项目中配置的任何 pre-commit 或 lefthook 钩子：

```sh
gac --no-verify  # 跳过所有 pre-commit 和 lefthook 钩子
```

**在以下情况下使用 `--no-verify`：**

- Pre-commit 或 lefthook 钩子暂时失败
- 使用耗时的钩子
- 提交尚未通过所有检查的进行中工作代码

**注意：**谨慎使用，因为这些钩子维护代码质量标准。

### 安全扫描

gac 包含内置的安全扫描，在提交之前自动检测暂存更改中的潜在密钥和 API 密钥。这有助于防止意外提交敏感信息。

**跳过安全扫描：**

```sh
gac --skip-secret-scan  # 为此次提交跳过安全扫描
```

**要永久禁用：**在你的 `.gac.env` 文件中设置 `GAC_SKIP_SECRET_SCAN=true`。

**何时跳过：**

- 提交带有占位符密钥的示例代码
- 使用包含虚拟凭据的测试装置
- 当你已经验证更改是安全的

**注意：**扫描程序使用模式匹配来检测常见的密钥格式。在提交之前，始终查看你的暂存更改。

### SSL 证书验证

gac 支持跳过 SSL 证书验证，适用于企业代理拦截 SSL 流量并导致证书验证失败的环境。

**跳过 SSL 验证：**

```sh
gac --no-verify-ssl  # 为此次提交跳过 SSL 验证
```

**要永久禁用：**在你的 `.gac.env` 文件中设置 `GAC_NO_VERIFY_SSL=true`，或在配置中添加 `no_verify_ssl=true`。

**何时使用：**

- 使用 SSL 拦截代理的企业环境
- 使用自签名证书的开发环境
- 当你遇到 SSL 证书验证错误时

**注意：**禁用 SSL 验证会降低安全性。仅在必要时并在受信任的网络环境中使用此选项。

## 配置说明

- 设置 gac 的推荐方法是运行 `gac init` 并按照交互式提示操作。
- 已经配置好语言，只想切换提供商或模型？运行 `gac model`，它会跳过所有语言相关的问题。
- **使用 Claude Code？** 请参阅[Claude Code 设置指南](CLAUDE_CODE.md)获取 OAuth 认证说明。
- **使用 Qwen.ai？** 请参阅 [Qwen.ai 设置指南](QWEN.md) 了解 OAuth 身份验证说明。
- gac 按以下优先级顺序加载配置：
  1. CLI 标志
  2. 环境变量
  3. 项目级 `.gac.env`
  4. 用户级 `~/.gac.env`

### 高级配置选项

你可以使用这些可选的环境变量自定义 gac 的行为：

- `GAC_ALWAYS_INCLUDE_SCOPE=true` - 自动推断并在提交信息中包含范围（例如，`feat(auth):` vs `feat:`）
- `GAC_VERBOSE=true` - 生成包含动机、架构和影响部分的详细提交信息
- `GAC_TEMPERATURE=0.7` - 控制 LLM 创造力（0.0-1.0，较低 = 更专注）
- `GAC_MAX_OUTPUT_TOKENS=4096` - 生成信息的最大令牌数（使用 `--group` 时根据文件数量自动缩放 2-5 倍；覆盖以提高或降低）
- `GAC_WARNING_LIMIT_TOKENS=4096` - 当提示超过此令牌数时发出警告
- `GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt` - 使用自定义系统提示进行提交信息生成
- `GAC_LANGUAGE=Spanish` - 以特定语言生成提交信息（例如，Spanish、French、Japanese、German）。支持完整名称或 ISO 代码（es、fr、ja、de、zh-CN）。使用 `gac language` 进行交互式选择
- `GAC_TRANSLATE_PREFIXES=true` - 将常规提交前缀（feat、fix 等）翻译为目标语言（默认值：false，保持前缀为英语）
- `GAC_SKIP_SECRET_SCAN=true` - 禁用暂存更改中的密钥自动安全扫描（谨慎使用）
- `GAC_NO_VERIFY_SSL=true` - 跳过 API 调用的 SSL 证书验证（适用于拦截 SSL 流量的企业代理）
- `GAC_NO_TIKTOKEN=true` - 通过绕过 `tiktoken` 下载步骤并使用内置的粗略令牌估算器来保持完全离线

查看 `.gac.env.example` 了解完整的配置模板。

有关创建自定义系统提示的详细指导，请参阅 [docs/CUSTOM_SYSTEM_PROMPTS.md](../CUSTOM_SYSTEM_PROMPTS.md)。

### 配置子命令

以下子命令可用：

- `gac init` — 提供商、模型和语言配置的交互式设置向导
- `gac model` — 提供商/模型/API 密钥设置，无语言提示（适合快速切换）
- `gac auth` — 显示所有提供商的 OAuth 身份验证状态
- `gac auth claude-code login` — 使用 OAuth 登录 Claude Code（打开浏览器）
- `gac auth claude-code logout` — 从 Claude Code 注销并删除存储的令牌
- `gac auth claude-code status` — 检查 Claude Code 身份验证状态
- `gac auth qwen login` — 使用 OAuth 设备流程登录 Qwen（打开浏览器）
- `gac auth qwen logout` — 从 Qwen 注销并删除存储的令牌
- `gac auth qwen status` — 检查 Qwen 身份验证状态
- `gac config show` — 显示当前配置
- `gac config set KEY VALUE` — 在 `$HOME/.gac.env` 中设置配置键
- `gac config get KEY` — 获取配置值
- `gac config unset KEY` — 从 `$HOME/.gac.env` 中删除配置键
- `gac language`（或 `gac lang`）— 提交消息的交互式语言选择器（设置 GAC_LANGUAGE）
- `gac diff` — 显示过滤的 git diff，具有暂存/未暂存更改、颜色和截断选项

## 交互模式

`--interactive` (`-i`) 标志通过就你的更改提出有针对性的问题，改进 gac 的提交信息生成。这种额外的上下文帮助 LLM 创建更准确、详细且符合上下文的提交信息。

### 工作原理

当你使用 `--interactive` 时，gac 会提出如下问题：

- **这些更改的主要目的是什么？** - 帮助理解高层目标
- **你在解决什么问题？** - 提供关于动机的上下文
- **有什么实现细节值得一提吗？** - 捕获技术规格
- **有破坏性更改吗？** - 识别潜在的影响问题
- **这与某个 issue 或 ticket 相关吗？** - 连接到项目管理

### 何时使用交互模式

交互模式特别适用于：

- **复杂更改**，仅从 diff 无法清楚了解上下文
- **重构工作**，跨越多个文件和概念
- **新功能**，需要解释总体目的
- **错误修复**，根本原因不是立即可见
- **性能优化**，逻辑不直观
- **代码审查准备** - 问题帮助你思考你的更改

### 使用示例

**基本交互模式：**

```sh
gac -i
```

这将：

1. 显示暂存更改的摘要
2. 就更改提出问题
3. 使用你的答案生成提交信息
4. 请求确认（或在与 `-y` 组合时自动确认）

**交互模式配合暂存更改：**

```sh
gac -ai
# 暂存所有更改，然后提问以获得更好的上下文
```

**交互模式配合特定提示：**

```sh
gac -i -h "用户配置文件的数据库迁移"
# 在提供特定提示以聚焦 LLM 的同时提问
```

**交互模式配合详细输出：**

```sh
gac -i -v
# 提问并生成详细、结构化的提交信息
```

**自动确认的交互模式：**

```sh
gac -i -y
# 提问但自动确认生成的提交
```

### 问答工作流

交互工作流遵循此模式：

1. **更改审查** - gac 显示你正在提交的内容摘要
2. **回答问题** - 用相关细节回答每个提示
3. **上下文改进** - 你的答案被添加到 LLM 提示中
4. **信息生成** - LLM 创建具有完整上下文的提交信息
5. **确认** - 审查并确认提交（或用 `-y` 自动确认）

**有用答案的技巧：**

- **简洁但完整** - 提供重要细节而不过于冗长
- **专注于"为什么"** - 解释你更改背后的推理
- **提及限制** - 注意限制或特殊考虑
- **链接到外部上下文** - 引用 issues、文档或设计文档
- **空答案也可以** - 如果问题不适用，只需按 Enter

### 与其他标志组合

交互模式与大多数其他标志配合良好：

```sh
# 暂存所有更改并提问
gac -ai

# 提问并配合详细输出
gac -i -v
```

### 最佳实践

- **用于复杂的 PR** - 特别适用于需要详细解释的 pull requests
- **团队协作** - 问题帮助你思考其他人将要审查的更改
- **文档准备** - 你的答案可以帮助形成发布说明的基础
- **学习工具** - 问题强化提交信息的良好实践
- **跳过简单更改** - 对于琐碎的修复，基本模式可能更快

## 获取帮助

- 有关自定义系统提示，请参阅 [docs/CUSTOM_SYSTEM_PROMPTS.md](../CUSTOM_SYSTEM_PROMPTS.md)
- 有关故障排除和高级提示，请参阅 [docs/TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- 有关安装和配置，请参阅 [README.md#installation-and-configuration](../README.md#installation-and-configuration)
- 要贡献，请参阅 [docs/CONTRIBUTING.md](../CONTRIBUTING.md)
- 许可证信息：[LICENSE](../../LICENSE)
