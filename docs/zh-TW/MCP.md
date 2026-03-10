# 將 GAC 用作 MCP 伺服器

[English](../en/MCP.md) | [简体中文](../zh-CN/MCP.md) | **繁體中文** | [日本語](../ja/MCP.md) | [한국어](../ko/MCP.md) | [हिन्दी](../hi/MCP.md) | [Tiếng Việt](../vi/MCP.md) | [Français](../fr/MCP.md) | [Русский](../ru/MCP.md) | [Español](../es/MCP.md) | [Português](../pt/MCP.md) | [Norsk](../no/MCP.md) | [Svenska](../sv/MCP.md) | [Deutsch](../de/MCP.md) | [Nederlands](../nl/MCP.md) | [Italiano](../it/MCP.md)

GAC 可以作為 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 伺服器執行，允許 AI 代理和編輯器透過結構化工具呼叫而非 shell 命令來生成提交。

## 目錄

- [將 GAC 用作 MCP 伺服器](#將-gac-用作-mcp-伺服器)
  - [目錄](#目錄)
  - [什麼是 MCP？](#什麼是-mcp)
  - [優勢](#優勢)
  - [設定](#設定)
    - [Claude Code](#claude-code)
    - [Cursor](#cursor)
    - [其他 MCP 客戶端](#其他-mcp-客戶端)
  - [可用工具](#可用工具)
    - [gac_status](#gac_status)
    - [gac_commit](#gac_commit)
  - [工作流程](#工作流程)
    - [基本提交](#基本提交)
    - [提交前預覽](#提交前預覽)
    - [分組提交](#分組提交)
    - [帶上下文的提交](#帶上下文的提交)
  - [設定](#設定-1)
  - [故障排除](#故障排除)
  - [另請參閱](#另請參閱)

## 什麼是 MCP？

Model Context Protocol 是一個開放標準，允許 AI 應用程式透過結構化介面呼叫外部工具。透過將 GAC 作為 MCP 伺服器執行，任何相容 MCP 的客戶端都可以檢查倉庫狀態並建立 AI 驅動的提交，而無需直接呼叫 shell 命令。

## 優勢

- **結構化互動**：代理呼叫帶有驗證參數的型別化工具，而非解析 shell 輸出
- **雙工具工作流程**：`gac_status` 用於檢查，`gac_commit` 用於操作 — 天然適合代理推理
- **完整的 GAC 功能**：AI 提交訊息、分組提交、密鑰掃描和推送 — 全部透過 MCP 可用
- **零設定**：伺服器使用你現有的 GAC 設定（`~/.gac.env`、提供者設定等）

## 設定

MCP 伺服器透過 `gac serve` 啟動，並透過 stdio（標準 MCP 傳輸）進行通訊。

### Claude Code

新增到你的專案 `.mcp.json` 或全域 `~/.claude/claude_code_config.json`：

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

或者如果你已經全域安裝了 GAC：

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

新增到你的 Cursor MCP 設定（`.cursor/mcp.json`）：

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

### 其他 MCP 客戶端

任何相容 MCP 的客戶端都可以使用 GAC。伺服器進入點為：

```text
command: uvx
args: ["gac", "serve"]
transport: stdio
```

如果你已經安裝了 GAC（透過 `uv tool install gac`），可以直接使用 `gac` 而非 `uvx gac`。

## 可用工具

伺服器公開兩個工具：

### gac_status

檢查倉庫狀態。在提交之前使用此工具了解將要提交的內容。

**參數：**

| 參數                | 類型                                    | 預設值      | 描述                             |
| ------------------- | --------------------------------------- | ----------- | -------------------------------- |
| `format`            | `"summary"` \| `"detailed"` \| `"json"` | `"summary"` | 輸出格式                         |
| `include_diff`      | bool                                    | `false`     | 包含完整的 diff 內容             |
| `include_stats`     | bool                                    | `true`      | 包含行變更統計資訊               |
| `include_history`   | int                                     | `0`         | 要包含的最近提交數量             |
| `staged_only`       | bool                                    | `false`     | 僅顯示已暫存的變更               |
| `include_untracked` | bool                                    | `true`      | 包含未追蹤的檔案                 |
| `max_diff_lines`    | int                                     | `500`       | 限制 diff 輸出大小（0 = 無限制） |

**回傳：** 分支名稱、檔案狀態（已暫存/未暫存/未追蹤/衝突）、可選的 diff 內容、可選的統計資訊和可選的提交歷史。

### gac_commit

生成 AI 驅動的提交訊息並可選地執行提交。

**參數：**

| 參數               | 類型           | 預設值  | 描述                                  |
| ------------------ | -------------- | ------- | ------------------------------------- |
| `stage_all`        | bool           | `false` | 在提交前暫存所有變更（`git add -A`）  |
| `files`            | list[str]      | `[]`    | 要暫存的特定檔案                      |
| `dry_run`          | bool           | `false` | 預覽但不執行                          |
| `message_only`     | bool           | `false` | 僅生成訊息而不提交                    |
| `push`             | bool           | `false` | 提交後推送到遠端                      |
| `group`            | bool           | `false` | 將變更拆分為多個邏輯提交              |
| `one_liner`        | bool           | `false` | 單行提交訊息                          |
| `scope`            | string \| null | `null`  | 常規提交範圍（未提供時自動偵測）      |
| `hint`             | string         | `""`    | 用於生成更好訊息的額外上下文          |
| `model`            | string \| null | `null`  | 覆蓋 AI 模型（`provider:model_name`） |
| `language`         | string \| null | `null`  | 覆蓋提交訊息語言                      |
| `skip_secret_scan` | bool           | `false` | 跳過安全掃描                          |
| `no_verify`        | bool           | `false` | 跳過 pre-commit 鉤子                  |
| `auto_confirm`     | bool           | `false` | 跳過確認提示（代理必需）              |

**回傳：** 成功狀態、生成的提交訊息、提交雜湊（如果已提交）、變更的檔案清單以及任何警告。

## 工作流程

### 基本提交

```text
1. gac_status()                              → 檢視已變更的內容
2. gac_commit(stage_all=true, auto_confirm=true)  → 暫存、生成訊息並提交
```

### 提交前預覽

```text
1. gac_status(include_diff=true, include_stats=true)  → 詳細審查變更
2. gac_commit(stage_all=true, dry_run=true)            → 預覽提交訊息
3. gac_commit(stage_all=true, auto_confirm=true)       → 執行提交
```

### 分組提交

```text
1. gac_status()                                           → 檢視所有變更
2. gac_commit(stage_all=true, group=true, dry_run=true)   → 預覽邏輯分組
3. gac_commit(stage_all=true, group=true, auto_confirm=true)  → 執行分組提交
```

### 帶上下文的提交

```text
1. gac_status(include_history=5)  → 檢視最近提交以參考風格
2. gac_commit(
     stage_all=true,
     hint="Fixes login timeout bug from issue #42",
     scope="auth",
     auto_confirm=true
   )
```

## 設定

MCP 伺服器使用你現有的 GAC 設定。除以下內容外，不需要額外設定：

1. **提供者和模型**：執行 `gac init` 或 `gac model` 設定你的 AI 提供者
2. **API 金鑰**：儲存在 `~/.gac.env` 中（在 `gac init` 期間設定）
3. **可選設定**：所有 GAC 環境變數均適用（`GAC_LANGUAGE`、`GAC_VERBOSE` 等）

有關所有設定選項，請參閱[主要文件](USAGE.md#設定說明)。

## 故障排除

### "No model configured"

在使用 MCP 伺服器之前，執行 `gac init` 設定你的 AI 提供者和模型。

### "No staged changes found"

手動暫存檔案（`git add`）或在 `gac_commit` 呼叫中使用 `stage_all=true`。

### 伺服器無法啟動

驗證 GAC 是否已安裝且可存取：

```bash
uvx gac --version
# or
gac --version
```

如果使用 `uvx`，請確保 `uv` 已安裝並在你的 PATH 中。

### 代理無法找到伺服器

確保 MCP 設定檔位於客戶端的正確位置，並且 `command` 路徑可從你的 shell 環境存取。

### Rich 輸出損壞

MCP 伺服器會自動將所有 Rich 主控台輸出重新導向到 stderr，以防止 stdio 協定損壞。如果你看到亂碼輸出，請確保在使用 MCP 時執行 `gac serve`（而非直接執行 `gac`）。

## 另請參閱

- [主要文件](USAGE.md)
- [Claude Code OAuth 設定](CLAUDE_CODE.md)
- [Qwen.ai OAuth 設定](QWEN.md)
- [故障排除指南](TROUBLESHOOTING.md)
- [MCP 規範](https://modelcontextprotocol.io/)
