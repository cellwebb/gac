# 使用 GitHub Copilot 與 GAC

[English](../en/GITHUB_COPILOT.md) | [简体中文](../zh-CN/GITHUB_COPILOT.md) | **繁體中文** | [日本語](../ja/GITHUB_COPILOT.md) | [한국어](../ko/GITHUB_COPILOT.md) | [हिन्दी](../hi/GITHUB_COPILOT.md) | [Tiếng Việt](../vi/GITHUB_COPILOT.md) | [Français](../fr/GITHUB_COPILOT.md) | [Русский](../ru/GITHUB_COPILOT.md) | [Español](../es/GITHUB_COPILOT.md) | [Português](../pt/GITHUB_COPILOT.md) | [Norsk](../no/GITHUB_COPILOT.md) | [Svenska](../sv/GITHUB_COPILOT.md) | [Deutsch](../de/GITHUB_COPILOT.md) | [Nederlands](../nl/GITHUB_COPILOT.md) | [Italiano](../it/GITHUB_COPILOT.md)

GAC 支援透過 GitHub Copilot 進行身份驗證，讓您可以使用 Copilot 訂閱來存取 OpenAI、Anthropic、Google 等的模型——所有這些都包含在您的 GitHub Copilot 方案中。

## 什麼是 GitHub Copilot OAuth？

GitHub Copilot OAuth 使用 **Device Flow**——一種安全的、基於瀏覽器的身份驗證方法，不需要本機回呼伺服器。您造訪一個 URL，輸入一次性代碼，並授權 GAC 使用您的 Copilot 存取權限。在幕後，GAC 將您長期有效的 GitHub OAuth 權杖交換為短期 Copilot 工作階段權杖（約30分鐘），以授予對 Copilot API 的存取權限。

這使您可以透過單一訂閱存取多個提供商的模型：

- **OpenAI** — `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`
- **Anthropic** — `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5`
- **Google** — `gemini-2.5-pro`, `gemini-2.5-flash`

## 優勢

- **多提供商存取**：透過單一訂閱使用 OpenAI、Anthropic 和 Google 的模型
- **成本效益**：使用現有的 Copilot 訂閱，無需單獨支付 API 金鑰費用
- **無需管理 API 金鑰**：Device Flow 身份驗證——無需輪換或儲存金鑰
- **GitHub Enterprise 支援**：透過 `--host` 標誌支援 GHE 實例

## 設定

### 選項 1：初始設定期間（推薦）

執行 `gac init` 時，只需選擇"Copilot"作為您的提供商：

```bash
gac init
```

精靈將：

1. 要求您從提供商清單中選擇"Copilot"
2. 顯示一次性代碼並開啟您的瀏覽器進行 Device Flow 身份驗證
3. 將您的 OAuth 權杖儲存到 `~/.gac/oauth/copilot.json`
4. 設定預設模型

### 選項 2：稍後切換到 Copilot

如果您已經將 GAC 設定為另一個提供商：

```bash
gac model
```

然後從提供商清單中選擇"Copilot"並進行身份驗證。

### 選項 3：直接登入

直接進行身份驗證，無需更改預設模型：

```bash
gac auth copilot login
```

### 正常使用 GAC

身份驗證後，像往常一樣使用 GAC：

```bash
# 暫存您的變更
git add .

# 使用 Copilot 生成並提交
gac

# 或者為單次提交覆蓋模型
gac -m copilot:gpt-4.1
gac -m copilot:claude-sonnet-4.5
gac -m copilot:gemini-2.5-pro
```

## 可用模型

Copilot 提供對多個提供商模型的存取。目前模型包括：

| 提供商    | 模型                                                                                           |
| --------- | ---------------------------------------------------------------------------------------------- |
| OpenAI    | `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`                                           |
| Anthropic | `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5` |
| Google    | `gemini-2.5-pro`, `gemini-2.5-flash`                                                           |

> **注意：** 登入後顯示的模型清單僅供參考，可能會隨著 GitHub 新增新模型而過時。請查看 [GitHub Copilot 文件](https://docs.github.com/en/copilot) 取得最新的可用模型。

## GitHub Enterprise

要使用 GitHub Enterprise 實例進行身份驗證：

```bash
gac auth copilot login --host ghe.mycompany.com
```

GAC 將自動使用適合您 GHE 實例的 Device Flow 和 API 端點。工作階段權杖按主機快取，因此不同的 GHE 實例會獨立處理。

## CLI 命令

GAC 提供專用的 CLI 命令用於 Copilot 身份驗證管理：

### 登入

使用 GitHub Copilot 進行身份驗證或重新身份驗證：

```bash
gac auth copilot login
```

您的瀏覽器將開啟一個 Device Flow 頁面，您需要在其中輸入一次性代碼。如果您已經過身份驗證，將詢問您是否要重新身份驗證。

對於 GitHub Enterprise：

```bash
gac auth copilot login --host ghe.mycompany.com
```

### 登出

刪除儲存的 Copilot 權杖：

```bash
gac auth copilot logout
```

這將刪除儲存在 `~/.gac/oauth/copilot.json` 的權杖檔案和工作階段快取。

### 狀態

檢查您目前的 Copilot 身份驗證狀態：

```bash
gac auth copilot status
```

或一次檢查所有提供商：

```bash
gac auth
```

## 工作原理

Copilot 身份驗證流程與 ChatGPT 和 Claude Code OAuth 不同：

1. **Device Flow** — GAC 從 GitHub 請求裝置代碼並顯示它
2. **瀏覽器授權** — 您造訪 URL 並輸入代碼
3. **權杖輪詢** — GAC 輪詢 GitHub 直到您完成授權
4. **工作階段權杖交換** — GitHub OAuth 權杖被交換為短期 Copilot 工作階段權杖
5. **自動重新整理** — 工作階段權杖（約30分鐘）從快取的 OAuth 權杖自動重新整理

與基於 PKCE 的 OAuth（ChatGPT/Claude Code）不同，Device Flow 不需要本機回呼伺服器或連接埠管理。

## 疑難排解

### 「未找到 Copilot 身份驗證」

執行登入命令進行身份驗證：

```bash
gac auth copilot login
```

### 「無法取得 Copilot 工作階段權杖」

這意味著 GAC 取得了 GitHub OAuth 權杖，但無法將其交換為 Copilot 工作階段權杖。通常這意味著：

1. **沒有 Copilot 訂閱** — 您的 GitHub 帳戶沒有活躍的 Copilot 訂閱
2. **權杖被撤銷** — OAuth 權杖已被撤銷；使用 `gac auth copilot login` 重新身份驗證

### 工作階段權杖過期

工作階段權杖在大約30分鐘後過期。GAC 從快取的 OAuth 權杖自動重新整理它們，因此您不需要頻繁重新身份驗證。如果自動重新整理失敗：

```bash
gac auth copilot login
```

### 「無效或不安全的主機名稱」

`--host` 標誌嚴格驗證主機名稱以防止 SSRF 攻擊。如果您看到此錯誤：

- 確保主機名稱不包含連接埠（例如，使用 `ghe.company.com` 而不是 `ghe.company.com:8080`）
- 不要包含協定或路徑（例如，使用 `ghe.company.com` 而不是 `https://ghe.company.com/api`）
- 出於安全考量，私有 IP 位址和 `localhost` 被阻止

### GitHub Enterprise 問題

如果 GHE 身份驗證失敗：

1. 驗證您的 GHE 實例已啟用 Copilot
2. 檢查您的 GHE 主機名稱是否可以從您的機器存取
3. 確保您的 GHE 帳戶擁有 Copilot 授權
4. 嘗試明確使用 `--host` 標誌：`gac auth copilot login --host ghe.mycompany.com`

## 與其他 OAuth 提供商的區別

| 特性         | ChatGPT OAuth            | Claude Code          | Copilot                                 |
| ------------ | ------------------------ | -------------------- | --------------------------------------- |
| 身份驗證方法 | PKCE（瀏覽器回呼）       | PKCE（瀏覽器回呼）   | Device Flow（一次性代碼）               |
| 回呼伺服器   | 連接埠 1455-1465         | 連接埠 8765-8795     | 不需要                                  |
| 權杖生命週期 | 長期有效（自動重新整理） | 過期（重新身份驗證） | 工作階段約30分鐘（自動重新整理）        |
| 模型         | Codex 優化的 OpenAI      | Claude 系列          | 多提供商（OpenAI + Anthropic + Google） |
| GHE 支援     | 否                       | 否                   | 是（`--host` 標誌）                     |

## 安全說明

- **切勿將您的 OAuth 權杖提交**到版本控制
- GAC 將 OAuth 權杖儲存在 `~/.gac/oauth/copilot.json`（在專案目錄之外）
- 工作階段權杖快取在 `~/.gac/oauth/copilot_session.json` 中，權限為 `0o600`
- 主機名稱經過嚴格驗證以防止 SSRF 和 URL 注入攻擊
- 私有 IP 位址、回環位址和 `localhost` 作為主機名稱被阻止
- Device Flow 不暴露任何本機連接埠，減少了攻擊面

## 另請參閱

- [主要文件](USAGE.md)
- [疑難排解指南](TROUBLESHOOTING.md)
- [ChatGPT OAuth 指南](CHATGPT_OAUTH.md)
- [Claude Code 指南](CLAUDE_CODE.md)
- [GitHub Copilot 文件](https://docs.github.com/en/copilot)
