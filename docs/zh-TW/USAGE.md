# gac 命令列使用

[English](../en/USAGE.md) | [简体中文](../zh-CN/USAGE.md) | **繁體中文** | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | [Tiếng Việt](../vi/USAGE.md) | [Français](../fr/USAGE.md) | [Русский](../ru/USAGE.md) | [Español](../es/USAGE.md) | [Português](../pt/USAGE.md) | [Deutsch](../de/USAGE.md) | [Nederlands](../nl/USAGE.md)

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

| 標誌 / 選項          | 簡寫 | 描述                                   |
| -------------------- | ---- | -------------------------------------- |
| `--add-all`          | `-a` | 在提交之前暫存所有變更                 |
| `--group`            | `-g` | 將暫存的變更分組為多個邏輯提交         |
| `--push`             | `-p` | 提交後推送變更到遠端                   |
| `--yes`              | `-y` | 自動確認提交而不提示                   |
| `--dry-run`          |      | 顯示會發生什麼而不進行任何變更         |
| `--no-verify`        |      | 提交時跳過 pre-commit 和 lefthook 鉤子 |
| `--skip-secret-scan` |      | 跳過暫存變更中的密鑰安全掃描           |

**注意：**組合 `-a` 和 `-g`（即 `-ag`）以先暫存所有變更，然後將它們分組為提交。

**注意：**使用 `--group` 時，最大輸出權杖限制會根據正在提交的檔案數量自動縮放（1-9 個檔案為 2 倍，10-19 個檔案為 3 倍，20-29 個檔案為 4 倍，30+ 個檔案為 5 倍）。這確保 LLM 有足夠的權杖來生成所有分組提交而不會被截斷，即使對於大型變更集也是如此。

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
  gac -m anthropic:claude-3-5-haiku-latest
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

檢視 `.gac.env.example` 了解完整的設定範本。

有關建立自訂系統提示的詳細指導，請參閱 [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md)。

### 設定子命令

以下子命令可用：

- `gac init` — 提供者、模型和語言設定的互動式設定精靈
- `gac model` — 只更新提供者/模型/API Key 的快捷精靈（跳過語言提示）
- `gac config show` — 顯示目前設定
- `gac config set KEY VALUE` — 在 `$HOME/.gac.env` 中設定設定金鑰
- `gac config get KEY` — 獲取設定值
- `gac config unset KEY` — 從 `$HOME/.gac.env` 中刪除設定金鑰
- `gac language`（或 `gac lang`）— 提交訊息的互動式語言選擇器（設定 GAC_LANGUAGE）
- `gac diff` — 顯示過濾的 git diff，具有暫存/未暫存變更、顏色和截斷選項

## 獲取協助

- 有關自訂系統提示，請參閱 [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md)
- 有關故障排除和進階提示，請參閱 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- 有關安裝和設定，請參閱 [README.md#installation-and-configuration](README.md#installation-and-configuration)
- 要貢獻，請參閱 [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- 授權資訊：[LICENSE](LICENSE)
