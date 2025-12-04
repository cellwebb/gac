# gac 命令列使用

[English](../en/USAGE.md) | [简体中文](../zh-CN/USAGE.md) | **繁體中文** | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | [Tiếng Việt](../vi/USAGE.md) | [Français](../fr/USAGE.md) | [Русский](../ru/USAGE.md) | [Español](../es/USAGE.md) | [Português](../pt/USAGE.md) | [Norsk](../no/USAGE.md) | [Svenska](../sv/USAGE.md) | [Deutsch](../de/USAGE.md) | [Nederlands](../nl/USAGE.md) | [Italiano](../it/USAGE.md)

本文件介紹了 `gac` CLI 工具的所有可用標誌和選項。

## 目錄

- [gac 命令列使用](#gac-命令列使用)
  - [目錄](#目錄)
  - [基本使用](#基本使用)
  - [核心工作流程標誌](#核心工作流程標誌)
  - [訊息客製化](#訊息客製化)
  - [輸出和詳細程度](#輸出和詳細程度)
  - [說明和版本](#說明和版本)
  - [範例工作流程](#範例工作流程)
  - [進階](#進階)
    - [跳過 Pre-commit 和 Lefthook 鉤子](#跳過-pre-commit-和-lefthook-鉤子)
    - [安全掃描](#安全掃描)
  - [設定說明](#設定說明)
    - [進階設定選項](#進階設定選項)
    - [設定子命令](#設定子命令)
  - [互動模式](#互動模式)
    - [工作原理](#工作原理)
    - [何時使用互動模式](#何時使用互動模式)
    - [使用範例](#使用範例)
    - [問答工作流程](#問答工作流程)
    - [與其他標誌組合](#與其他標誌組合)
    - [最佳實踐](#最佳實踐)
  - [獲取協助](#獲取協助)

## 基本使用

```sh
gac init
# 然後按照提示以互動方式設定你的提供者、模型和 API 金鑰
gac
```

為暫存的變更生成 LLM 驅動的提交訊息並提示確認。確認提示接受：

- `y` 或 `yes` - 繼續提交
- `n` 或 `no` - 取消提交
- `r` 或 `reroll` - 使用相同的上下文重新生成提交訊息
- `e` 或 `edit` - 使用豐富的終端機編輯就地編輯提交訊息（vi/emacs 鍵繫結）
- 任何其他文字 - 使用該文字作為回饋重新生成（例如，`讓它更短`，`專注於效能`）
- 空輸入（只按 Enter）- 再次顯示提示

---

## 核心工作流程標誌

| 標誌 / 選項          | 簡寫 | 描述                                            |
| -------------------- | ---- | ----------------------------------------------- |
| `--add-all`          | `-a` | 在提交之前暫存所有變更                          |
| `--group`            | `-g` | 將暫存的變更分組為多個邏輯提交                  |
| `--push`             | `-p` | 提交後推送變更到遠端                            |
| `--yes`              | `-y` | 自動確認提交而不提示                            |
| `--dry-run`          |      | 顯示會發生什麼而不進行任何變更                  |
| `--message-only`     |      | 只輸出產生的提交訊息，本身不對 git 進行任何提交 |
| `--no-verify`        |      | 提交時跳過 pre-commit 和 lefthook 鉤子          |
| `--skip-secret-scan` |      | 跳過暫存變更中的密鑰安全掃描                    |
| `--interactive`      | `-i` | 就變更提問以獲得更好的提交                      |

**注意：**組合 `-a` 和 `-g`（即 `-ag`）以先暫存所有變更，然後將它們分組為提交。

**注意：**使用 `--group` 時，最大輸出權杖限制會根據正在提交的檔案數量自動縮放（1-9 個檔案為 2 倍，10-19 個檔案為 3 倍，20-29 個檔案為 4 倍，30+ 個檔案為 5 倍）。這確保 LLM 有足夠的權杖來生成所有分組提交而不會被截斷，即使對於大型變更集也是如此。

**注意：**`--message-only` 與 `--group` 是互斥的。需要將提交訊息提供給外部腳本或工具處理時，請使用 `--message-only`；需要在目前的 git 工作流程中組織多個提交時，請使用 `--group`。

**注意：**`--interactive` 標誌透過就你的變更提問，為 LLM 提供額外上下文，從而產生更準確、更詳細的提交訊息。這特別適用於複雜變更，或者當你希望確保提交訊息捕捉到工作的完整上下文時。

## 訊息客製化

| 標誌 / 選項         | 簡寫 | 描述                                                   |
| ------------------- | ---- | ------------------------------------------------------ |
| `--one-liner`       | `-o` | 生成單行提交訊息                                       |
| `--verbose`         | `-v` | 生成包含動機、架構和影響的詳細提交訊息                 |
| `--hint <text>`     | `-h` | 新增提示以引導 LLM                                     |
| `--model <model>`   | `-m` | 指定用於此次提交的模型                                 |
| `--language <lang>` | `-l` | 覆蓋語言（名稱或代碼：'Spanish'、'es'、'zh-CN'、'ja'） |
| `--scope`           | `-s` | 為提交推斷適當的範圍                                   |

**注意：**你可以透過在確認提示符處簡單地輸入來互動式提供回饋 - 無需前綴 'r'。輸入 `r` 進行簡單的重新生成，`e` 使用 vi/emacs 鍵繫結就地編輯，或直接輸入你的回饋，如 `讓它更短`。

## 輸出和詳細程度

| 標誌 / 選項           | 簡寫 | 描述                                        |
| --------------------- | ---- | ------------------------------------------- |
| `--quiet`             | `-q` | 抑制除錯誤外的所有輸出                      |
| `--log-level <level>` |      | 設定日誌級別（debug、info、warning、error） |
| `--show-prompt`       |      | 列印用於提交訊息生成的 LLM 提示             |

## 說明和版本

| 標誌 / 選項 | 簡寫 | 描述                |
| ----------- | ---- | ------------------- |
| `--version` |      | 顯示 gac 版本並退出 |
| `--help`    |      | 顯示說明訊息並退出  |

---

## 範例工作流程

- **暫存所有變更並提交：**

  ```sh
  gac -a
  ```

- **一步提交並推送：**

  ```sh
  gac -ap
  ```

- **生成單行提交訊息：**

  ```sh
  gac -o
  ```

- **生成包含結構化部分的詳細提交訊息：**

  ```sh
  gac -v
  ```

- **為 LLM 新增提示：**

  ```sh
  gac -h "重構身份驗證邏輯"
  ```

- **為提交推斷範圍：**

  ```sh
  gac -s
  ```

- **將暫存的變更分組為邏輯提交：**

  ```sh
  gac -g
  # 僅分組你已經暫存的檔案
  ```

- **分組所有變更（暫存 + 未暫存）並自動確認：**

  ```sh
  gac -agy
  # 暫存所有內容，分組，並自動確認
  ```

- **僅為此次提交使用特定模型：**

  ```sh
  gac -m anthropic:claude-haiku-4-5
  ```

- **以特定語言生成提交訊息：**

  ```sh
  # 使用語言代碼（較短）
  gac -l zh-CN
  gac -l ja
  gac -l es

  # 使用完整名稱
  gac -l "Simplified Chinese"
  gac -l Japanese
  gac -l Spanish
  ```

- **演練（檢視會發生什麼）：**

  ```sh
  gac --dry-run
  ```

- **只取得提交訊息（供腳本整合使用）：**

  ```sh
  gac --message-only
  # 範例輸出：feat: add user authentication system
  ```

- **以單行格式取得提交訊息：**

  ```sh
  gac --message-only --one-liner
  # 範例輸出：feat: add user authentication system
  ```

- **使用互動模式提供上下文：**

  ```sh
  gac -i
  # 這些變更的主要目的是什麼？
  # 你在解決什麼問題？
  # 有什麼實作細節值得一提嗎？
  ```

- **互動模式配合詳細輸出：**

  ```sh
  gac -i -v
  # 提問並生成詳細的提交訊息
  ```

## 進階

- 組合標誌以獲得更強大的工作流程（例如，`gac -ayp` 以暫存、自動確認和推送）
- 使用 `--show-prompt` 偵錯或檢視傳送給 LLM 的提示
- 使用 `--log-level` 或 `--quiet` 調整詳細程度

### 跳過 Pre-commit 和 Lefthook 鉤子

`--no-verify` 標誌允許你跳過專案中設定的任何 pre-commit 或 lefthook 鉤子：

```sh
gac --no-verify  # 跳過所有 pre-commit 和 lefthook 鉤子
```

**在以下情況下使用 `--no-verify`：**

- Pre-commit 或 lefthook 鉤子暫時失敗
- 使用耗時的鉤子
- 提交尚未通過所有檢查的進行中工作程式碼

**注意：**謹慎使用，因為這些鉤子維護程式碼品質標準。

### 安全掃描

gac 包含內建的安全掃描，在提交之前自動檢測暫存變更中的潛在密鑰和 API 金鑰。這有助於防止意外提交敏感資訊。

**跳過安全掃描：**

```sh
gac --skip-secret-scan  # 為此次提交跳過安全掃描
```

**要永久停用：**在你的 `.gac.env` 檔案中設定 `GAC_SKIP_SECRET_SCAN=true`。

**何時跳過：**

- 提交帶有佔位符密鑰的範例程式碼
- 使用包含虛擬憑證的測試裝置
- 當你已經驗證變更是安全的

**注意：**掃描程式使用模式比對來檢測常見的密鑰格式。在提交之前，始終檢視你的暫存變更。

## 設定說明

- 設定 gac 的推薦方法是執行 `gac init` 並按照互動式提示操作。
- 已經設定好語言，只想切換提供者或模型？執行 `gac model`，它會跳過所有語言相關的問題。
- **使用 Claude Code？** 請參閱[Claude Code 設定指南](CLAUDE_CODE.md)取得 OAuth 驗證說明。
- **使用 Qwen.ai？** 請參閱 [Qwen.ai 設定指南](QWEN.md) 了解 OAuth 驗證說明。
- gac 按以下優先順序順序載入設定：
  1. CLI 標誌
  2. 環境變數
  3. 專案級 `.gac.env`
  4. 使用者級 `~/.gac.env`

### 進階設定選項

你可以使用這些可選的環境變數自訂 gac 的行為：

- `GAC_ALWAYS_INCLUDE_SCOPE=true` - 自動推斷並在提交訊息中包含範圍（例如，`feat(auth):` vs `feat:`）
- `GAC_VERBOSE=true` - 生成包含動機、架構和影響部分的詳細提交訊息
- `GAC_TEMPERATURE=0.7` - 控制 LLM 創造力（0.0-1.0，較低 = 更專注）
- `GAC_MAX_OUTPUT_TOKENS=4096` - 生成訊息的最大權杖數（使用 `--group` 時根據檔案數量自動縮放 2-5 倍；覆蓋以提高或降低）
- `GAC_WARNING_LIMIT_TOKENS=4096` - 當提示超過此權杖數時發出警告
- `GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt` - 使用自訂系統提示進行提交訊息生成
- `GAC_LANGUAGE=Spanish` - 以特定語言生成提交訊息（例如，Spanish、French、Japanese、German）。支援完整名稱或 ISO 代碼（es、fr、ja、de、zh-CN）。使用 `gac language` 進行互動式選擇
- `GAC_TRANSLATE_PREFIXES=true` - 將常規提交前綴（feat、fix 等）翻譯為目標語言（預設值：false，保持前綴為英語）
- `GAC_SKIP_SECRET_SCAN=true` - 停用暫存變更中的密鑰自動安全掃描（謹慎使用）
- `GAC_NO_TIKTOKEN=true` - 透過繞過 `tiktoken` 下載步驟並使用內建的粗略令牌估算器來保持完全離線

檢視 `.gac.env.example` 了解完整的設定範本。

有關建立自訂系統提示的詳細指導，請參閱 [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md)。

### 設定子命令

以下子命令可用：

- `gac init` — 提供者、模型和語言設定的互動式設定精靈
- `gac model` — 提供者/模型/API 金鑰設定，無語言提示（適合快速切換）
- `gac auth` — 顯示所有提供者的 OAuth 驗證狀態
- `gac auth claude-code login` — 使用 OAuth 登入 Claude Code（開啟瀏覽器）
- `gac auth claude-code logout` — 從 Claude Code 登出並移除儲存的令牌
- `gac auth claude-code status` — 檢查 Claude Code 驗證狀態
- `gac auth qwen login` — 使用 OAuth 裝置流程登入 Qwen（開啟瀏覽器）
- `gac auth qwen logout` — 從 Qwen 登出並移除儲存的令牌
- `gac auth qwen status` — 檢查 Qwen 驗證狀態
- `gac config show` — 顯示目前設定
- `gac config set KEY VALUE` — 在 `$HOME/.gac.env` 中設定設定金鑰
- `gac config get KEY` — 獲取設定值
- `gac config unset KEY` — 從 `$HOME/.gac.env` 中刪除設定金鑰
- `gac language`（或 `gac lang`）— 提交訊息的互動式語言選擇器（設定 GAC_LANGUAGE）
- `gac diff` — 顯示過濾的 git diff，具有暫存/未暫存變更、顏色和截斷選項

## 互動模式

`--interactive` (`-i`) 標誌透過就你的變更提出有針對性的問題，改進 gac 的提交訊息生成。這種額外的上下文幫助 LLM 創建更準確、詳細且符合上下文的提交訊息。

### 工作原理

當你使用 `--interactive` 時，gac 會提出如下問題：

- **這些變更的主要目的是什麼？** - 幫助理解高層目標
- **你在解決什麼問題？** - 提供關於動機的上下文
- **有什麼實作細節值得一提嗎？** - 捕獲技術規格
- **有破壞性變更嗎？** - 識別潛在的影響問題
- **這與某個 issue 或 ticket 相關嗎？** - 連接到專案管理

### 何時使用互動模式

互動模式特別適用於：

- **複雜變更**，僅從 diff 無法清楚了解上下文
- **重構工作**，跨越多個檔案和概念
- **新功能**，需要解釋總體目的
- **錯誤修復**，根本原因不是立即可見
- **效能優化**，邏輯不直觀
- **程式碼審查準備** - 問題幫助你思考你的變更

### 使用範例

**基本互動模式：**

```sh
gac -i
```

這將：

1. 顯示暫存變更的摘要
2. 就變更提出問題
3. 使用你的答案生成提交訊息
4. 請求確認（或與 `-y` 組合時自動確認）

**互動模式配合暫存變更：**

```sh
gac -ai
# 暫存所有變更，然後提問以獲得更好的上下文
```

**互動模式配合特定提示：**

```sh
gac -i -h "使用者設定檔的資料庫遷移"
# 在提供特定提示以聚焦 LLM 的同時提問
```

**互動模式配合詳細輸出：**

```sh
gac -i -v
# 提問並生成詳細、結構化的提交訊息
```

**自動確認的互動模式：**

```sh
gac -i -y
# 提問但自動確認生成的提交
```

### 問答工作流程

互動工作流程遵循此模式：

1. **變更審查** - gac 顯示你正在提交的內容摘要
2. **回答問題** - 用相關細節回答每個提示
3. **上下文改進** - 你的答案被添加到 LLM 提示中
4. **訊息生成** - LLM 創建具有完整上下文的提交訊息
5. **確認** - 審查並確認提交（或用 `-y` 自動確認）

**有用答案的技巧：**

- **簡潔但完整** - 提供重要細節而不過於冗長
- **專注於"為什麼"** - 解釋你變更背后的推理
- **提及限制** - 注意限制或特殊考慮
- **連結到外部上下文** - 引用 issues、文件或設計文件
- **空答案也可以** - 如果問題不適用，只需按 Enter

### 與其他標誌組合

互動模式與大多數其他標誌配合良好：

```sh
# 暫存所有變更並提問
gac -ai

# 提問並配合詳細輸出
gac -i -v
```

### 最佳實踐

- **用於複雜的 PR** - 特別適用於需要詳細解釋的 pull requests
- **團隊協作** - 問題幫助你思考其他人將要審查的變更
- **文件準備** - 你的答案可以幫助形成發布說明的基礎
- **學習工具** - 問題強化提交訊息的良好實踐
- **跳過簡單變更** - 對於瑣碎的修復，基本模式可能更快

## 獲取協助

- 有關自訂系統提示，請參閱 [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md)
- 有關故障排除和進階提示，請參閱 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- 有關安裝和設定，請參閱 [README.md#installation-and-configuration](README.md#installation-and-configuration)
- 要貢獻，請參閱 [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- 授權資訊：[LICENSE](LICENSE)
