# gac 命令行使用

[English](USAGE.md) | 简体中文 | [繁體中文](USAGE.zh-TW.md)

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
    - [跳过 Pre-commit 和 Lefthook 钩子](#跳过-pre-commit-和-lefthook-钩子)
    - [安全扫描](#安全扫描)
  - [配置说明](#配置说明)
    - [高级配置选项](#高级配置选项)
    - [配置子命令](#配置子命令)
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
| `--no-verify`        |      | 提交时跳过 pre-commit 和 lefthook 钩子 |
| `--skip-secret-scan` |      | 跳过暂存更改中的密钥安全扫描           |

**注意：**组合 `-a` 和 `-g`（即 `-ag`）以先暂存所有更改，然后将它们分组为提交。

**注意：**使用 `--group` 时，最大输出令牌限制会根据正在提交的文件数量自动缩放（1-9 个文件为 2 倍，10-19 个文件为 3 倍，20-29 个文件为 4 倍，30+ 个文件为 5 倍）。这确保 LLM 有足够的令牌来生成所有分组提交而不会被截断，即使对于大型变更集也是如此。

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
  gac -m anthropic:claude-3-5-haiku-latest
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

## 高级

- 组合标志以获得更强大的工作流（例如，`gac -ayp` 以暂存、自动确认和推送）
- 使用 `--show-prompt` 调试或查看发送给 LLM 的提示
- 使用 `--log-level` 或 `--quiet` 调整详细程度

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

## 配置说明

- 设置 gac 的推荐方法是运行 `gac init` 并按照交互式提示操作。
- 已经配置好语言，只想切换提供商或模型？运行 `gac model`，它会跳过所有语言相关的问题。
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

查看 `.gac.env.example` 了解完整的配置模板。

有关创建自定义系统提示的详细指导，请参阅 [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md)。

### 配置子命令

以下子命令可用：

- `gac init` — 提供商、模型和语言配置的交互式设置向导
- `gac model` — 只更新提供商/模型/API Key 的快捷向导（跳过语言提示）
- `gac config show` — 显示当前配置
- `gac config set KEY VALUE` — 在 `$HOME/.gac.env` 中设置配置键
- `gac config get KEY` — 获取配置值
- `gac config unset KEY` — 从 `$HOME/.gac.env` 中删除配置键
- `gac language`（或 `gac lang`）— 提交信息的交互式语言选择器（设置 GAC_LANGUAGE）
- `gac diff` — 显示过滤的 git diff，具有暂存/未暂存更改、颜色和截断选项

## 获取帮助

- 有关自定义系统提示，请参阅 [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md)
- 有关故障排除和高级提示，请参阅 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- 有关安装和配置，请参阅 [README.md#installation-and-configuration](README.md#installation-and-configuration)
- 要贡献，请参阅 [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- 许可证信息：[LICENSE](LICENSE)
