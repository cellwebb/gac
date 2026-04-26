# 将 GAC 用作 MCP 服务器

[English](../en/MCP.md) | **简体中文** | [繁體中文](../zh-TW/MCP.md) | [日本語](../ja/MCP.md) | [한국어](../ko/MCP.md) | [हिन्दी](../hi/MCP.md) | [Tiếng Việt](../vi/MCP.md) | [Français](../fr/MCP.md) | [Русский](../ru/MCP.md) | [Español](../es/MCP.md) | [Português](../pt/MCP.md) | [Norsk](../no/MCP.md) | [Svenska](../sv/MCP.md) | [Deutsch](../de/MCP.md) | [Nederlands](../nl/MCP.md) | [Italiano](../it/MCP.md)

GAC 可以作为 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 服务器运行，允许 AI 代理和编辑器通过结构化工具调用而非 shell 命令来生成提交。

## 目录

- [将 GAC 用作 MCP 服务器](#将-gac-用作-mcp-服务器)
  - [目录](#目录)
  - [什么是 MCP？](#什么是-mcp)
  - [优势](#优势)
  - [设置](#设置)
    - [Claude Code](#claude-code)
    - [Cursor](#cursor)
    - [其他 MCP 客户端](#其他-mcp-客户端)
  - [可用工具](#可用工具)
    - [gac_status](#gac_status)
    - [gac_commit](#gac_commit)
  - [工作流](#工作流)
    - [基本提交](#基本提交)
    - [提交前预览](#提交前预览)
    - [分组提交](#分组提交)
    - [带上下文的提交](#带上下文的提交)
  - [配置](#配置)
  - [故障排除](#故障排除)
  - [另请参阅](#另请参阅)

## 什么是 MCP？

Model Context Protocol 是一个开放标准，允许 AI 应用程序通过结构化接口调用外部工具。通过将 GAC 作为 MCP 服务器运行，任何兼容 MCP 的客户端都可以检查仓库状态并创建 AI 驱动的提交，而无需直接调用 shell 命令。

## 优势

- **结构化交互**：代理调用带有验证参数的类型化工具，而非解析 shell 输出
- **双工具工作流**：`gac_status` 用于检查，`gac_commit` 用于操作 — 天然适合代理推理
- **完整的 GAC 功能**：AI 提交信息、分组提交、密钥扫描和推送 — 全部通过 MCP 可用
- **零配置**：服务器使用你现有的 GAC 配置（`~/.gac.env`、提供商设置等）

## 设置

MCP 服务器通过 `gac serve` 启动，并通过 stdio（标准 MCP 传输）进行通信。

### Claude Code

添加到你的项目 `.mcp.json` 或全局 `~/.claude/claude_code_config.json`：

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

或者如果你已经全局安装了 GAC：

```json
{
  "mcpServers": {
    "gac": {
      "command": "gac",
      "args": ["serve"]
    }
  }
}
```

### Cursor

添加到你的 Cursor MCP 设置（`.cursor/mcp.json`）：

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

### 其他 MCP 客户端

任何兼容 MCP 的客户端都可以使用 GAC。服务器入口点为：

```text
command: uvx
args: ["gac", "serve"]
transport: stdio
```

如果你已经安装了 GAC（通过 `uv tool install gac`），可以直接使用 `gac` 而非 `uvx gac`。

## 可用工具

服务器公开两个工具：

### gac_status

检查仓库状态。在提交之前使用此工具了解将要提交的内容。

**参数：**

| 参数                | 类型                                    | 默认值      | 描述                             |
| ------------------- | --------------------------------------- | ----------- | -------------------------------- |
| `format`            | `"summary"` \| `"detailed"` \| `"json"` | `"summary"` | 输出格式                         |
| `include_diff`      | bool                                    | `false`     | 包含完整的 diff 内容             |
| `include_stats`     | bool                                    | `true`      | 包含行更改统计信息               |
| `include_history`   | int                                     | `0`         | 要包含的最近提交数量             |
| `staged_only`       | bool                                    | `false`     | 仅显示已暂存的更改               |
| `include_untracked` | bool                                    | `true`      | 包含未跟踪的文件                 |
| `max_diff_lines`    | int                                     | `500`       | 限制 diff 输出大小（0 = 无限制） |

**返回：** 分支名称、文件状态（已暂存/未暂存/未跟踪/冲突）、可选的 diff 内容、可选的统计信息和可选的提交历史。

### gac_commit

生成 AI 驱动的提交信息并可选地执行提交。

**参数：**

| 参数               | 类型           | 默认值  | 描述                                  |
| ------------------ | -------------- | ------- | ------------------------------------- |
| `stage_all`        | bool           | `false` | 在提交前暂存所有更改（`git add -A`）  |
| `files`            | list[str]      | `[]`    | 要暂存的特定文件                      |
| `dry_run`          | bool           | `false` | 预览但不执行                          |
| `message_only`     | bool           | `false` | 仅生成信息而不提交                    |
| `push`             | bool           | `false` | 提交后推送到远程                      |
| `group`            | bool           | `false` | 将更改拆分为多个逻辑提交              |
| `one_liner`        | bool           | `false` | 单行提交信息                          |
| `scope`            | string \| null | `null`  | 常规提交范围（未提供时自动检测）      |
| `hint`             | string         | `""`    | 用于生成更好信息的额外上下文          |
| `model`            | string \| null | `null`  | 覆盖 AI 模型（`provider:model_name`） |
| `language`         | string \| null | `null`  | 覆盖提交信息语言                      |
| `skip_secret_scan` | bool           | `false` | 跳过安全扫描                          |
| `no_verify`        | bool           | `false` | 跳过 pre-commit 钩子                  |
| `auto_confirm`     | bool           | `false` | 跳过确认提示（代理必需）              |

**返回：** 成功状态、生成的提交信息、提交哈希（如果已提交）、更改的文件列表以及任何警告。

## 工作流

### 基本提交

```text
1. gac_status()                              → 查看已更改的内容
2. gac_commit(stage_all=true, auto_confirm=true)  → 暂存、生成信息并提交
```

### 提交前预览

```text
1. gac_status(include_diff=true, include_stats=true)  → 详细审查更改
2. gac_commit(stage_all=true, dry_run=true)            → 预览提交信息
3. gac_commit(stage_all=true, auto_confirm=true)       → 执行提交
```

### 分组提交

```text
1. gac_status()                                           → 查看所有更改
2. gac_commit(stage_all=true, group=true, dry_run=true)   → 预览逻辑分组
3. gac_commit(stage_all=true, group=true, auto_confirm=true)  → 执行分组提交
```

### 带上下文的提交

```text
1. gac_status(include_history=5)  → 查看最近提交以参考风格
2. gac_commit(
     stage_all=true,
     hint="Fixes login timeout bug from issue #42",
     scope="auth",
     auto_confirm=true
   )
```

## 配置

MCP 服务器使用你现有的 GAC 配置。除以下内容外，不需要额外设置：

1. **提供商和模型**：运行 `gac init` 或 `gac model` 配置你的 AI 提供商
2. **API 密钥**：存储在 `~/.gac.env` 中（在 `gac init` 期间设置）
3. **可选设置**：所有 GAC 环境变量均适用（`GAC_LANGUAGE`、`GAC_VERBOSE` 等）

有关所有配置选项，请参阅[主要文档](USAGE.md#配置说明)。

## 故障排除

### "No model configured"

在使用 MCP 服务器之前，运行 `gac init` 设置你的 AI 提供商和模型。

### "No staged changes found"

手动暂存文件（`git add`）或在 `gac_commit` 调用中使用 `stage_all=true`。

### 服务器无法启动

验证 GAC 是否已安装且可访问：

```bash
uvx gac --version
# or
gac --version
```

如果使用 `uvx`，请确保 `uv` 已安装并在你的 PATH 中。

### 代理无法找到服务器

确保 MCP 配置文件位于客户端的正确位置，并且 `command` 路径可从你的 shell 环境访问。

### Rich 输出损坏

MCP 服务器会自动将所有 Rich 控制台输出重定向到 stderr，以防止 stdio 协议损坏。如果你看到乱码输出，请确保在使用 MCP 时运行 `gac serve`（而非直接运行 `gac`）。

## 另请参阅

- [主要文档](USAGE.md)
- [Claude Code OAuth 设置](CLAUDE_CODE.md)
- [故障排除指南](TROUBLESHOOTING.md)
- [MCP 规范](https://modelcontextprotocol.io/)
