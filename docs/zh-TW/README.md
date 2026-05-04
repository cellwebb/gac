<!-- markdownlint-disable MD013 -->
<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

# 🚀 Git Auto Commit (gac)

[![PyPI version](https://img.shields.io/pypi/v/gac.svg)](https://pypi.org/project/gac/)
[![Python](https://img.shields.io/badge/python-3.10--3.14-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://github.com/cellwebb/gac/actions/workflows/ci.yml/badge.svg)](https://github.com/cellwebb/gac/actions)
[![codecov](https://codecov.io/gh/cellwebb/gac/branch/main/graph/badge.svg)](https://app.codecov.io/gh/cellwebb/gac)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy-lang.org/)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](docs/zh-TW/CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](../../README.md) | [简体中文](../zh-CN/README.md) | **繁體中文** | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [हिन्दी](../hi/README.md) | [Tiếng Việt](../vi/README.md) | [Français](../fr/README.md) | [Русский](../ru/README.md) | [Español](../es/README.md) | [Português](../pt/README.md) | [Norsk](../no/README.md) | [Svenska](../sv/README.md) | [Deutsch](../de/README.md) | [Nederlands](../nl/README.md) | [Italiano](../it/README.md)

**能理解你程式碼的 LLM 驅動的提交訊息！**

**自動化你的提交！**用 `gac` 替代 `git commit -m "..."`，生成由大型語言模型建立的上下文相關、格式良好的提交訊息！

---

## 你將獲得

智慧的、上下文相關的訊息，解釋你變更背後的**原因**：

![GAC 生成上下文提交訊息](../../assets/gac-simple-usage.zh-TW.png)

---

</div>

<!-- markdownlint-enable MD033 MD036 -->

## 快速開始

### 無需安裝直接使用 gac

```bash
uvx gac init   # 設定提供者、模型和語言
uvx gac  # 使用 LLM 生成並提交
```

就是這麼簡單！檢視生成的訊息並用 `y` 確認。

### 安裝並使用 gac

```bash
uv tool install gac
gac init
gac
```

### 升級已安裝的 gac

```bash
uv tool upgrade gac
```

---

## 核心特性

### 🌐 **支援的 25+ 提供者**

- **Anthropic** • **Azure OpenAI** • **Cerebras** • **Chutes.ai** • **Claude Code (OAuth)**
- **DeepSeek** • **Fireworks** • **Gemini** • **Groq** • **Kimi for Coding** • **LM Studio**
- **MiniMax.io** • **Mistral AI** • **Moonshot AI** • **Ollama** • **OpenAI** • **OpenRouter**
- **Qwen Cloud (CN & INTL)** • **Replicate** • **Streamlake** • **Synthetic.new** • **Together AI**
- **Wafer.ai** • **Z.AI** • **Z.AI Coding** • **Custom Endpoints (Anthropic/OpenAI)**

### 🧠 **智慧 LLM 分析**

- **理解意圖**：分析程式碼結構、邏輯和模式，理解你變更背後的「原因」，而不僅僅是改變了什麼
- **語義感知**：識別重構、錯誤修復、新特性和破壞性變更，生成上下文適當的訊息
- **智慧過濾**：優先考慮有意義的變更，同時忽略產生的檔案、依賴項目和構件
- **智慧提交分組** - 使用 `--group` 自動將相關變更分組為多個邏輯提交

### 📝 **多種訊息格式**

- **單行**（-o 標誌）：遵循常規提交格式的單行提交訊息
- **標準**（預設）：帶有解釋實作細節的要點的摘要
- **詳細**（-v 標誌）：包括動機、技術方法和影響分析的全面解釋
- **50/72 規則**（--50-72 標誌）：強制使用經典的提交訊息格式，以便在 git log 和 GitHub UI 中獲得最佳可讀性
- **DCO/Signoff**（--signoff 標誌）：新增 Signed-off-by 行以符合開發者原產地證書（Cherry Studio、Linux 核心及其他專案要求）

### 🌍 **多語言支援**

- **25+ 種語言**：生成英語、中文、日語、韓語、西班牙語、法語、德語等 20 多種語言的提交訊息
- **彈性翻譯**：選擇保持常規提交前綴為英語以保持工具相容性，或完全翻譯它們
- **多種工作流程**：使用 `gac language` 設定預設語言，或使用 `-l <語言>` 標誌進行一次性覆蓋
- **原生文字支援**：完全支援非拉丁文字，包括中日韓、西里爾文、泰文等

### 💻 **開發者體驗**

- **互動式回饋**：輸入 `r` 重新生成，`e` 編輯（預設就地 TUI，或設定了 `$GAC_EDITOR` 時使用該編輯器），或直接輸入你的回饋，如 `讓它更短` 或 `專注於錯誤修復`
- **互動式提問**：使用 `--interactive` (`-i`) 回答有關你更改的定向問題，以獲得更多上下文的提交訊息
- **單命令工作流程**：使用 `gac -ayp`（暫存所有、自動確認、推送）等標誌完成完整工作流程
- **Git 整合**：尊重 pre-commit 和 lefthook 鉤子，在昂貴的 LLM 操作之前執行它們
- **MCP 伺服器**：執行 `gac serve` 透過 [Model Context Protocol](https://modelcontextprotocol.io/) 向 AI 代理公開提交工具

### 📊 **使用統計**

- **追蹤你的 gac 使用**：檢視你用 gac 做了多少次提交、當前連續使用天數、每日/每週活動峰值和熱門專案
- **Token 追蹤**：按日、週、專案和模型統計的提示 + 完成令牌總數 — 令牌使用量也有高分獎盃
- **熱門模型**：檢視你最常用的模型以及每個模型消耗的令牌數
- **專案級統計**：使用 `gac stats project` 檢視當前倉庫的統計資訊
- **高分慶祝**：🏆 在你創造新的每日、每週、令牌或連續使用紀錄時獲得獎盃；🥈 在追平紀錄時獲得
- **設定時選擇加入**：`gac init` 會詢問是否啟用統計，並詳細說明儲存的內容
- **隨時退出**：設定 `GAC_DISABLE_STATS=true`（或 `1`/`yes`/`on`）以停用。設定為 `false`/`0`/`no`（或取消設定）則保持統計啟用
- **隱私優先**：本地儲存在 `~/.gac_stats.json`。僅儲存計數、日期、專案名稱和模型名稱 — 不含提交訊息、程式碼或個人資料。無遙測

### 🛡️ **內建安全**

- **自動密鑰檢測**：在提交前掃描 API 密鑰、密碼和權杖
- **互動式保護**：在提交潛在敏感資料之前提示，並提供清晰的補救選項
- **智慧過濾**：忽略範例檔案、範本檔案和佔位符文字以減少誤報

---

## 使用範例

### 基本工作流程

```bash
# 暫存你的變更
git add .

# 使用 LLM 生成並提交
gac

# 檢視 → y（提交）| n（取消）| r（重新生成）| e（編輯）| 或輸入回饋
```

### 常用命令

| 命令            | 描述                                           |
| --------------- | ---------------------------------------------- |
| `gac`           | 生成提交訊息                                   |
| `gac -y`        | 自動確認（無需檢視）                           |
| `gac -a`        | 在生成提交訊息之前暫存所有內容                 |
| `gac -o`        | 用於瑣碎變更的單行訊息                         |
| `gac -v`        | 包含動機、技術方法和影響分析的詳細格式         |
| `gac -h "提示"` | 為 LLM 新增上下文（例如，`gac -h "錯誤修復"`） |
| `gac -s`        | 包括範圍（例如，feat(auth):）                  |
| `gac -i`        | 詢問有關更改的問題以獲得更好的上下文           |
| `gac -g`        | 將更改分組為多個邏輯提交                       |
| `gac -p`        | 提交並推送                                     |
| `gac stats`     | 檢視你的 gac 使用統計                          |

### 進階使用者範例

```bash
# 一條命令完成完整工作流程
# 檢視你的提交統計
gac stats

# 僅檢視當前專案的統計
gac stats project

gac -ayp -h "發布準備"

# 帶範圍的詳細解釋
gac -v -s

# 小變更的快速單行
gac -o

# 將變更分組為邏輯相關的提交
gac -ag

# 帶詳細輸出的互動模式用於詳細解釋
gac -iv

# 偵錯 LLM 看到的內容
gac --show-prompt

# 跳過安全掃描（謹慎使用）
gac --skip-secret-scan

# 新增 signoff 以符合 DCO（Cherry Studio、Linux 核心等）
gac --signoff
```

### 互動式回饋系統

對結果不滿意？你有幾個選項：

```bash
# 簡單重新生成（無回饋）
r

# 編輯提交訊息
e
# 預設：帶 vi/emacs 鍵繫結的就地 TUI
# 按 Esc+Enter 或 Ctrl+S 提交，Ctrl+C 取消

# 設定 GAC_EDITOR 以開啟您偏好的編輯器：
# GAC_EDITOR=code gac → 開啟 VS Code（--wait 自動新增）
# GAC_EDITOR=vim gac → 開啟 vim
# GAC_EDITOR=nano gac → 開啟 nano

# 或者直接輸入你的回饋！
讓它更短並專注於效能改進
使用帶範圍的常規提交格式
解釋安全影響

# 在空輸入上按 Enter 再次檢視提示
```

編輯功能（`e`）允許你精煉提交訊息：

- **預設（就地 TUI）**：使用 vi/emacs 鍵繫結進行多行編輯 — 糾正拼寫錯誤、調整措辭、重組
- **設定 `GAC_EDITOR`**：開啟您偏好的編輯器（`code`、`vim`、`nano` 等） — 完整的編輯器功能，包括尋找/取代、巨集等

VS Code 等 GUI 編輯器會自動處理：gac 會插入 `--wait`，使程序在關閉編輯器分頁前一直阻塞。無需額外設定。

---

## 設定

執行 `gac init` 以互動方式設定你的提供者，或設定環境變數：

想要在之後僅更新提供者或模型且不修改語言？使用 `gac model`，它會跳過語言相關的提示。

```bash
# 範例設定
GAC_MODEL=anthropic:your-model-name
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

檢視 `.gac.env.example` 了解所有可用選項。

**想要其他語言的提交訊息？**執行 `gac language` 從 25 多種語言中選擇，包括 Español、Français、日本語 等。

**想要自訂提交訊息風格？**請參閱 [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/zh-TW/CUSTOM_SYSTEM_PROMPTS.md) 了解編寫自訂系統提示的指導。

---

## 獲取協助

- **完整文件**：[USAGE.md](docs/zh-TW/USAGE.md) - 完整的 CLI 參考
- **MCP 伺服器**：[MCP.md](MCP.md) - 將 GAC 用作 AI 代理的 MCP 伺服器
- **Claude Code OAuth**：[docs/CLAUDE_CODE.md](docs/zh-TW/CLAUDE_CODE.md) - Claude Code 設定與驗證
- **自訂提示**：[CUSTOM_SYSTEM_PROMPTS.md](docs/zh-TW/CUSTOM_SYSTEM_PROMPTS.md) - 自訂提交訊息風格
- **使用統計**：參見 `gac stats --help` 或[完整文件](docs/zh-TW/USAGE.md#使用統計)
- **故障排除**：[TROUBLESHOOTING.md](docs/zh-TW/TROUBLESHOOTING.md) - 常見問題和解決方案
- **貢獻**：[CONTRIBUTING.md](docs/zh-TW/CONTRIBUTING.md) - 開發設定和指南

---

<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

[⭐ 在 GitHub 上給我們點星](https://github.com/cellwebb/gac) • [🐛 報告問題](https://github.com/cellwebb/gac/issues) • [📖 完整文件](docs/zh-TW/USAGE.md)

</div>

<!-- markdownlint-enable MD033 MD036 -->
