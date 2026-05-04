# 使用 ChatGPT OAuth 與 GAC

**English** | [简体中文](../zh-CN/CHATGPT_OAUTH.md) | [繁體中文](../zh-TW/CHATGPT_OAUTH.md) | [日本語](../ja/CHATGPT_OAUTH.md) | [한국어](../ko/CHATGPT_OAUTH.md) | [हिन्दी](../hi/CHATGPT_OAUTH.md) | [Tiếng Việt](../vi/CHATGPT_OAUTH.md) | [Français](../fr/CHATGPT_OAUTH.md) | [Русский](../ru/CHATGPT_OAUTH.md) | [Español](../es/CHATGPT_OAUTH.md) | [Português](../pt/CHATGPT_OAUTH.md) | [Norsk](../no/CHATGPT_OAUTH.md) | [Svenska](../sv/CHATGPT_OAUTH.md) | [Deutsch](../de/CHATGPT_OAUTH.md) | [Nederlands](../nl/CHATGPT_OAUTH.md) | [Italiano](../it/CHATGPT_OAUTH.md)

GAC 支援透過 ChatGPT OAuth 進行身份驗證，讓您可以使用 ChatGPT 訂閱來存取 OpenAI 的 Codex API，而無需單獨支付 OpenAI API 金鑰費用。這與 OpenAI 的 Codex CLI 使用的 OAuth 流程相同。

> ⚠️ **注意 — 未經授權的使用：** 這使用了與 OpenAI 的 Codex CLI 相同的 OAuth 流程，雖然目前可以工作，但 OpenAI 可能隨時限制第三方權杖使用。GAC 足夠小，到目前為止還沒有引起注意，但在這裡使用 ChatGPT OAuth **並未獲得官方批准**用於第三方工具，可能隨時停止工作。如果您需要可靠的提交訊息生成，請使用直接 API 提供商（`openai` 等）。有關目前政策，請參閱 [OpenAI 的 Codex 文件](https://openai.com/codex)。

## 什麼是 ChatGPT OAuth？

ChatGPT OAuth 讓您可以利用現有的 ChatGPT Plus 或 Pro 訂閱來存取 Codex API 以生成提交訊息。無需管理 API 金鑰和按權杖計費，您只需透過瀏覽器進行一次身份驗證，GAC 就會自動處理權杖生命週期。

## 優勢

- **成本效益**：使用現有的 ChatGPT Plus/Pro 訂閱，無需單獨支付 API 存取費用
- **相同模型**：存取 Codex 優化模型（`gpt-5.5`、`gpt-5.4`、`gpt-5.3-codex`）
- **無需管理 API 金鑰**：基於瀏覽器的 OAuth 意味著無需輪換或儲存 API 金鑰
- **獨立計費**：ChatGPT OAuth 使用與直接 OpenAI API 計費分開

## 設定

GAC 包含用於 ChatGPT 的內建 OAuth 身份驗證。設定過程完全自動化，將開啟您的瀏覽器進行身份驗證。

### 選項 1：初始設定期間（推薦）

執行 `gac init` 時，只需選擇 "ChatGPT OAuth" 作為您的提供商：

```bash
gac init
```

精靈將：

1. 要求您從提供商清單中選擇 "ChatGPT OAuth"
2. 自動開啟您的瀏覽器進行 OAuth 身份驗證
3. 將您的存取權杖儲存到 `~/.gac/oauth/chatgpt-oauth.json`
4. 設定預設模型

### 選項 2：稍後切換到 ChatGPT OAuth

如果您已經將 GAC 設定為另一個提供商並想切換到 ChatGPT OAuth：

```bash
gac model
```

然後：

1. 從提供商清單中選擇 "ChatGPT OAuth"
2. 您的瀏覽器將自動開啟進行 OAuth 身份驗證
3. 權杖儲存到 `~/.gac/oauth/chatgpt-oauth.json`
4. 模型自動設定

### 正常使用 GAC

身份驗證後，像往常一樣使用 GAC：

```bash
# 暫存您的變更
git add .

# 使用 ChatGPT OAuth 生成並提交
gac

# 或者為單次提交覆蓋模型
gac -m chatgpt-oauth:gpt-5.5
```

## 可用模型

ChatGPT OAuth 提供對 Codex 優化模型的存取。目前模型包括：

- `gpt-5.5` — 最新且最強大的 Codex 模型
- `gpt-5.4` — 上一代 Codex 模型
- `gpt-5.3-codex` — 第三代 Codex 模型

查看 [OpenAI 文件](https://platform.openai.com/docs/models) 取得可用模型的完整清單。

## CLI 命令

GAC 提供專用的 CLI 命令用於 ChatGPT OAuth 管理：

### 登入

使用 ChatGPT OAuth 進行身份驗證或重新身份驗證：

```bash
gac auth chatgpt login
```

您的瀏覽器將自動開啟以完成 OAuth 流程。如果您已經過身份驗證，這將重新整理您的權杖。

### 登出

刪除儲存的 ChatGPT OAuth 權杖：

```bash
gac auth chatgpt logout
```

這將刪除儲存在 `~/.gac/oauth/chatgpt-oauth.json` 的權杖檔案。

### 狀態

檢查您目前的 ChatGPT OAuth 身份驗證狀態：

```bash
gac auth chatgpt status
```

或一次檢查所有提供商：

```bash
gac auth
```

## 疑難排解

### 權杖已過期

如果您看到身份驗證錯誤，您的權杖可能已過期。透過執行以下命令重新身份驗證：

```bash
gac auth chatgpt login
```

您的瀏覽器將自動開啟進行新的 OAuth 身份驗證。GAC 在可能時會自動使用重新整理權杖來續訂存取而無需重新身份驗證。

### 檢查身份驗證狀態

要檢查您目前是否已身份驗證：

```bash
gac auth chatgpt status
```

或一次檢查所有提供商：

```bash
gac auth
```

### 登出

要刪除儲存的權杖：

```bash
gac auth chatgpt logout
```

### "未找到 ChatGPT OAuth 權杖"

這意味著 GAC 找不到您的存取權杖。透過執行以下命令進行身份驗證：

```bash
gac model
```

然後從提供商清單中選擇 "ChatGPT OAuth"。OAuth 流程將自動啟動。

### "身份驗證失敗"

如果 OAuth 身份驗證失敗：

1. 確保您擁有有效的 ChatGPT Plus 或 Pro 訂閱
2. 檢查您的瀏覽器是否正確開啟
3. 如果問題仍然存在，請嘗試其他瀏覽器
4. 驗證與 `auth.openai.com` 的網路連線
5. 檢查連接埠 1455-1465 是否可用於本機回呼伺服器

### 連接埠已被佔用

OAuth 回呼伺服器會自動嘗試連接埠 1455-1465。如果所有連接埠都被佔用：

```bash
# 在 macOS/Linux 上：
lsof -ti:1455-1465 | xargs kill -9

# 在 Windows (PowerShell) 上：
Get-NetTCPConnection -LocalPort 1455,1456,1457,1458,1459,1460,1461,1462,1463,1464,1465 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

然後重新執行 `gac auth chatgpt login`。

## 與 OpenAI 提供商的區別

| 特性     | OpenAI (`openai:`)          | ChatGPT OAuth (`chatgpt-oauth:`)           |
| -------- | --------------------------- | ------------------------------------------ |
| 身份驗證 | API 金鑰 (`OPENAI_API_KEY`) | OAuth（自動化瀏覽器流程）                  |
| 計費     | 按權杖 API 計費             | 基於訂閱（ChatGPT Plus/Pro）               |
| 設定     | 手動輸入 API 金鑰           | 透過 `gac init` 或 `gac model` 自動 OAuth  |
| 權杖管理 | 長期有效的 API 金鑰         | OAuth 權杖（使用重新整理權杖自動重新整理） |
| 模型     | 所有 OpenAI 模型            | Codex 優化模型                             |

## 安全說明

- **切勿將存取權杖提交**到版本控制
- GAC 將 OAuth 權杖儲存在 `~/.gac/oauth/chatgpt-oauth.json`（在專案目錄之外）
- OAuth 流程使用 PKCE（程式碼交換證明金鑰）以增強安全性
- 本機回呼伺服器僅在 localhost 上執行（連接埠 1455-1465）
- 使用重新整理權杖自動續訂存取而無需重新身份驗證

## 另請參閱

- [主要文件](USAGE.md)
- [疑難排解指南](TROUBLESHOOTING.md)
- [OpenAI 的 Codex 文件](https://openai.com/codex)
