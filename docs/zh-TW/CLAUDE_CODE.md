# 在 GAC 中使用 Claude Code

[English](../en/CLAUDE_CODE.md) | [简体中文](../zh-CN/CLAUDE_CODE.md) | **繁體中文** | [日本語](../ja/CLAUDE_CODE.md) | [한국어](../ko/CLAUDE_CODE.md) | [हिन्दी](../hi/CLAUDE_CODE.md) | [Tiếng Việt](../vi/CLAUDE_CODE.md) | [Français](../fr/CLAUDE_CODE.md) | [Русский](../ru/CLAUDE_CODE.md) | [Español](../es/CLAUDE_CODE.md) | [Português](../pt/CLAUDE_CODE.md) | [Norsk](../no/CLAUDE_CODE.md) | [Svenska](../sv/CLAUDE_CODE.md) | [Deutsch](../de/CLAUDE_CODE.md) | [Nederlands](../nl/CLAUDE_CODE.md) | [Italiano](../it/CLAUDE_CODE.md)

GAC 支援透過 Claude Code 訂閱進行身份驗證，允許您使用 Claude Code 訂閱而不是支付昂貴的 Anthropic API 費用。這對於已經透過訂閱獲得 Claude Code 存取權限的用戶來說是完美的選擇。

## 什麼是 Claude Code？

Claude Code 是 Anthropic 的訂閱服務，提供基於 OAuth 的 Claude 模型存取。與使用 API 金鑰（按令牌計費）不同，Claude Code 使用您訂閱中的 OAuth 令牌。

## 優勢

- **成本效益**：使用您現有的 Claude Code 訂閱，而不是單獨支付 API 存取費用
- **相同模型**：存取相同的 Claude 模型（例如 `claude-sonnet-4-5`）
- **獨立計費**：Claude Code 使用與 Anthropic API 計費分離

## 設定

GAC 包含內建的 Claude Code OAuth 身份驗證。設定過程完全自動化，將打開您的瀏覽器進行身份驗證。

### 選項 1：在初始設定期間（推薦）

執行 `gac init` 時，只需選擇"Claude Code"作為您的提供者：

```bash
gac init
```

精靈將：

1. 要求您從提供者列表中選擇"Claude Code"
2. 自動打開您的瀏覽器進行 OAuth 身份驗證
3. 將您的存取令牌儲存到 `~/.gac.env`
4. 設定預設模型

### 選項 2：稍後切換到 Claude Code

如果您已經設定另一個提供者的 GAC 並想切換到 Claude Code：

```bash
gac model
```

然後：

1. 從提供者列表中選擇"Claude Code"
2. 您的瀏覽器將自動打開進行 OAuth 身份驗證
3. 令牌儲存到 `~/.gac.env`
4. 模型自動設定

### 正常使用 GAC

身份驗證後，像往常一樣使用 GAC：

```bash
# 暫存您的變更
git add .

# 使用 Claude Code 生成和提交
gac

# 或者為單次提交覆蓋模型
gac -m claude-code:claude-sonnet-4-5
```

## 可用模型

Claude Code 提供與 Anthropic API 相同的模型存取權限。當前的 Claude 4.5 系列模型包括：

- `claude-sonnet-4-5` - 最新且最智能的 Sonnet 模型，最適合編碼
- `claude-haiku-4-5` - 快速高效
- `claude-opus-4-1` - 最複雜推理的最強能力模型

查看 [Claude 文檔](https://docs.claude.com/en/docs/about-claude/models/overview) 獲取可用模型的完整列表。

## 故障排除

### 令牌已過期

如果您看到身份驗證錯誤，您的令牌可能已過期。透過執行重新身份驗證：

```bash
gac auth
```

您的瀏覽器將自動打開進行新的 OAuth 身份驗證。或者，您可以執行 `gac model`，選擇 "Claude Code"，然後選擇 "重新身份驗證（取得新令牌）"。

### "未找到 CLAUDE_CODE_ACCESS_TOKEN"

這表示 GAC 找不到您的存取令牌。透過執行身份驗證：

```bash
gac model
```

然後從提供者列表中選擇"Claude Code"。OAuth 流程將自動開始。

### "身份驗證失敗"

如果 OAuth 身份驗證失敗：

1. 確保您有活躍的 Claude Code 訂閱
2. 檢查您的瀏覽器是否正確打開
3. 如果問題持續存在，嘗試不同的瀏覽器
4. 驗證到 `claude.ai` 的網路連線
5. 檢查埠 8765-8795 是否可用於本地回呼伺服器

## 與 Anthropic 提供者的差異

| 功能     | Anthropic (`anthropic:`)       | Claude Code (`claude-code:`)                          |
| -------- | ------------------------------ | ----------------------------------------------------- |
| 身份驗證 | API 金鑰 (`ANTHROPIC_API_KEY`) | OAuth（自動瀏覽器流程）                               |
| 計費     | 按令牌 API 計費                | 基於訂閱                                              |
| 設定     | 手動 API 金鑰輸入              | 透過 `gac init` 或 `gac model` 自動 OAuth             |
| 令牌管理 | 長期 API 金鑰                  | OAuth 令牌（可能過期，透過 `model` 易於重新身份驗證） |
| 模型     | 相同模型                       | 相同模型                                              |

## 安全說明

- **永遠不要提交您的存取令牌**到版本控制
- GAC 自動將令牌儲存在 `~/.gac.env` 中（在您的專案目錄外）
- 令牌可能過期，需要透過 `gac model` 重新身份驗證
- OAuth 流程使用 PKCE（Proof Key for Code Exchange）增強安全性
- 本地回呼伺服器僅在本地主機執行（埠 8765-8795）

## 另請參閱

- [主要文件](USAGE.md)
- [故障排除指南](TROUBLESHOOTING.md)
- [Claude Code 文件](https://claude.ai/code)
