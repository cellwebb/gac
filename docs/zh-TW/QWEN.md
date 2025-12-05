[English](../en/QWEN.md) | [简体中文](../zh-CN/QWEN.md) | **繁體中文** | [日本語](../ja/QWEN.md) | [한국어](../ko/QWEN.md) | [हिन्दी](../hi/QWEN.md) | [Tiếng Việt](../vi/QWEN.md) | [Français](../fr/QWEN.md) | [Русский](../ru/QWEN.md) | [Español](../es/QWEN.md) | [Português](../pt/QWEN.md) | [Norsk](../no/QWEN.md) | [Svenska](../sv/QWEN.md) | [Deutsch](../de/QWEN.md) | [Nederlands](../nl/QWEN.md) | [Italiano](../it/QWEN.md)

# 在 GAC 中使用 Qwen.ai

GAC 支援透過 Qwen.ai OAuth 進行身份驗證，允許您使用 Qwen.ai 帳戶生成提交訊息。這使用了 OAuth 裝置流程身份驗證，提供無縫的登入體驗。

## 什麼是 Qwen.ai？

Qwen.ai 是阿里雲的 AI 平台，提供對 Qwen 系列大型語言模型的存取。GAC 支援基於 OAuth 的身份驗證，允許您使用 Qwen.ai 帳戶，而無需手動管理 API 金鑰。

## 優勢

- **輕鬆驗證**：OAuth 裝置流程 - 只需使用瀏覽器登入
- **無需 API 金鑰管理**：自動處理身份驗證
- **存取 Qwen 模型**：使用強大的 Qwen 模型生成提交訊息

## 設定

GAC 包含使用裝置流程的 Qwen.ai 內建 OAuth 身份驗證。設定過程將顯示代碼並打開瀏覽器進行身份驗證。

### 選項 1：初始設定期間（推薦）

執行 `gac init` 時，只需從提供者列表中選擇 "Qwen.ai (OAuth)"：

```bash
gac init
```

精靈將：

1. 要求您從提供者列表中選擇 "Qwen.ai (OAuth)"
2. 顯示裝置代碼並打開瀏覽器
3. 您將在 Qwen.ai 上進行身份驗證並輸入代碼
4. 安全儲存您的存取權杖
5. 設定預設模型

### 選項 2：稍後切換到 Qwen.ai

如果您已經使用其他提供者配置了 GAC，並希望切換到 Qwen.ai：

```bash
gac model
```

然後：

1. 從提供者列表中選擇 "Qwen.ai (OAuth)"
2. 按照裝置代碼身份驗證流程操作
3. 權杖安全儲存到 `~/.gac/oauth/qwen.json`
4. 自動配置模型

### 選項 3：直接登入

您也可以使用以下命令直接進行身份驗證：

```bash
gac auth qwen login
```

這將：

1. 顯示裝置代碼
2. 打開瀏覽器存取 Qwen.ai 身份驗證頁面
3. 身份驗證後，權杖將自動儲存

### 正常使用 GAC

驗證後，像往常一樣使用 GAC：

```bash
# 暫存變更
git add .

# 使用 Qwen.ai 生成並提交
gac

# 或為單個提交覆蓋模型
gac -m qwen:qwen3-coder-plus
```

## 可用模型

Qwen.ai OAuth 整合使用：

- `qwen3-coder-plus` - 針對編碼任務進行了最佳化（預設）

這是透過 portal.qwen.ai OAuth 端點可用的模型。對於其他 Qwen 模型，請考慮使用 OpenRouter 提供者，它提供更多 Qwen 模型選項。

## 身份驗證命令

GAC 提供了幾個用於管理 Qwen.ai 身份驗證的命令：

```bash
# 登入到 Qwen.ai
gac auth qwen login

# 檢查身份驗證狀態
gac auth qwen status

# 登出並刪除儲存的權杖
gac auth qwen logout

# 檢查所有 OAuth 提供者狀態
gac auth
```

### 登入選項

```bash
# 標準登入（自動打開瀏覽器）
gac auth qwen login

# 不打開瀏覽器登入（顯示手動存取的 URL）
gac auth qwen login --no-browser

# 安靜模式（最小輸出）
gac auth qwen login --quiet
```

## 故障排除

### 權杖過期

如果看到身份驗證錯誤，可能是您的權杖已過期。透過執行以下命令重新驗證：

```bash
gac auth qwen login
```

裝置代碼流程將開始，您的瀏覽器將打開以進行重新驗證。

### 檢查身份驗證狀態

要檢查您目前是否已透過身份驗證：

```bash
gac auth qwen status
```

或一次檢查所有提供者：

```bash
gac auth
```

### 登出

要刪除儲存的權杖：

```bash
gac auth qwen logout
```

### "未找到 Qwen 身份驗證"

這意味著 GAC 找不到您的存取權杖。透過執行以下命令進行身份驗證：

```bash
gac auth qwen login
```

或執行 `gac model` 並從提供者列表中選擇 "Qwen.ai (OAuth)"。

### "身份驗證失敗"

如果 OAuth 身份驗證失敗：

1. 確保您擁有 Qwen.ai 帳戶
2. 檢查瀏覽器是否正確打開
3. 驗證您是否正確輸入了裝置代碼
4. 如果問題仍然存在，請嘗試使用其他瀏覽器
5. 驗證到 `qwen.ai` 的網路連線

### 裝置代碼不起作用

如果裝置代碼身份驗證不起作用：

1. 確保代碼未過期（代碼在有限時間內有效）
2. 嘗試再次執行 `gac auth qwen login` 獲取新代碼
3. 如果瀏覽器打開失敗，請使用 `--no-browser` 標誌並手動存取 URL

## 安全說明

- **切勿將存取權杖提交**到版本控制
- GAC 自動將權杖儲存在 `~/.gac/oauth/qwen.json`（專案目錄之外）
- 權杖檔案具有受限權限（僅擁有者可讀）
- 權杖可能會過期，需要重新驗證
- OAuth 裝置流程專為無頭系統上的安全身份驗證而設計

## 另請參閱

- [主要文件](USAGE.md)
- [Claude Code 設定](CLAUDE_CODE.md)
- [故障排除指南](TROUBLESHOOTING.md)
- [Qwen.ai 文件](https://qwen.ai)
