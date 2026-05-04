# 使用 ChatGPT OAuth 与 GAC

**English** | [简体中文](../zh-CN/CHATGPT_OAUTH.md) | [繁體中文](../zh-TW/CHATGPT_OAUTH.md) | [日本語](../ja/CHATGPT_OAUTH.md) | [한국어](../ko/CHATGPT_OAUTH.md) | [हिन्दी](../hi/CHATGPT_OAUTH.md) | [Tiếng Việt](../vi/CHATGPT_OAUTH.md) | [Français](../fr/CHATGPT_OAUTH.md) | [Русский](../ru/CHATGPT_OAUTH.md) | [Español](../es/CHATGPT_OAUTH.md) | [Português](../pt/CHATGPT_OAUTH.md) | [Norsk](../no/CHATGPT_OAUTH.md) | [Svenska](../sv/CHATGPT_OAUTH.md) | [Deutsch](../de/CHATGPT_OAUTH.md) | [Nederlands](../nl/CHATGPT_OAUTH.md) | [Italiano](../it/CHATGPT_OAUTH.md)

GAC 支持通过 ChatGPT OAuth 进行身份验证，让您可以使用 ChatGPT 订阅来访问 OpenAI 的 Codex API，而无需单独支付 OpenAI API 密钥费用。这与 OpenAI 的 Codex CLI 使用的 OAuth 流程相同。

> ⚠️ **注意 — 未经授权的使用：** 这使用了与 OpenAI 的 Codex CLI 相同的 OAuth 流程，虽然目前可以工作，但 OpenAI 可能随时限制第三方令牌使用。GAC 足够小，到目前为止还没有引起注意，但在这里使用 ChatGPT OAuth **并未获得官方批准**用于第三方工具，可能随时停止工作。如果您需要可靠的提交消息生成，请使用直接 API 提供商（`openai` 等）。有关当前政策，请参阅 [OpenAI 的 Codex 文档](https://openai.com/codex)。

## 什么是 ChatGPT OAuth？

ChatGPT OAuth 让您可以利用现有的 ChatGPT Plus 或 Pro 订阅来访问 Codex API 以生成提交消息。无需管理 API 密钥和按令牌计费，您只需通过浏览器进行一次身份验证，GAC 就会自动处理令牌生命周期。

## 优势

- **成本效益**：使用现有的 ChatGPT Plus/Pro 订阅，无需单独支付 API 访问费用
- **相同模型**：访问 Codex 优化模型（`gpt-5.5`、`gpt-5.4`、`gpt-5.3-codex`）
- **无需管理 API 密钥**：基于浏览器的 OAuth 意味着无需轮换或存储 API 密钥
- **独立计费**：ChatGPT OAuth 使用与直接 OpenAI API 计费分开

## 设置

GAC 包含用于 ChatGPT 的内置 OAuth 身份验证。设置过程完全自动化，将打开您的浏览器进行身份验证。

### 选项 1：初始设置期间（推荐）

运行 `gac init` 时，只需选择 "ChatGPT OAuth" 作为您的提供商：

```bash
gac init
```

向导将：

1. 要求您从提供商列表中选择 "ChatGPT OAuth"
2. 自动打开您的浏览器进行 OAuth 身份验证
3. 将您的访问令牌保存到 `~/.gac/oauth/chatgpt-oauth.json`
4. 设置默认模型

### 选项 2：稍后切换到 ChatGPT OAuth

如果您已经将 GAC 配置为另一个提供商并想切换到 ChatGPT OAuth：

```bash
gac model
```

然后：

1. 从提供商列表中选择 "ChatGPT OAuth"
2. 您的浏览器将自动打开进行 OAuth 身份验证
3. 令牌保存到 `~/.gac/oauth/chatgpt-oauth.json`
4. 模型自动配置

### 正常使用 GAC

身份验证后，像往常一样使用 GAC：

```bash
# 暂存您的更改
git add .

# 使用 ChatGPT OAuth 生成并提交
gac

# 或者为单次提交覆盖模型
gac -m chatgpt-oauth:gpt-5.5
```

## 可用模型

ChatGPT OAuth 提供对 Codex 优化模型的访问。当前模型包括：

- `gpt-5.5` — 最新且最强大的 Codex 模型
- `gpt-5.4` — 上一代 Codex 模型
- `gpt-5.3-codex` — 第三代 Codex 模型

查看 [OpenAI 文档](https://platform.openai.com/docs/models) 获取可用模型的完整列表。

## CLI 命令

GAC 提供专用的 CLI 命令用于 ChatGPT OAuth 管理：

### 登录

使用 ChatGPT OAuth 进行身份验证或重新身份验证：

```bash
gac auth chatgpt login
```

您的浏览器将自动打开以完成 OAuth 流程。如果您已经过身份验证，这将刷新您的令牌。

### 登出

删除存储的 ChatGPT OAuth 令牌：

```bash
gac auth chatgpt logout
```

这将删除存储在 `~/.gac/oauth/chatgpt-oauth.json` 的令牌文件。

### 状态

检查您当前的 ChatGPT OAuth 身份验证状态：

```bash
gac auth chatgpt status
```

或一次检查所有提供商：

```bash
gac auth
```

## 故障排除

### 令牌已过期

如果您看到身份验证错误，您的令牌可能已过期。通过运行以下命令重新身份验证：

```bash
gac auth chatgpt login
```

您的浏览器将自动打开进行新的 OAuth 身份验证。GAC 在可能时会自动使用刷新令牌来续订访问而无需重新身份验证。

### 检查身份验证状态

要检查您当前是否已身份验证：

```bash
gac auth chatgpt status
```

或一次检查所有提供商：

```bash
gac auth
```

### 登出

要删除存储的令牌：

```bash
gac auth chatgpt logout
```

### "未找到 ChatGPT OAuth 令牌"

这意味着 GAC 找不到您的访问令牌。通过运行以下命令进行身份验证：

```bash
gac model
```

然后从提供商列表中选择 "ChatGPT OAuth"。OAuth 流程将自动启动。

### "身份验证失败"

如果 OAuth 身份验证失败：

1. 确保您拥有有效的 ChatGPT Plus 或 Pro 订阅
2. 检查您的浏览器是否正确打开
3. 如果问题仍然存在，请尝试其他浏览器
4. 验证与 `auth.openai.com` 的网络连接
5. 检查端口 1455-1465 是否可用于本地回调服务器

### 端口已被占用

OAuth 回调服务器会自动尝试端口 1455-1465。如果所有端口都被占用：

```bash
# 在 macOS/Linux 上：
lsof -ti:1455-1465 | xargs kill -9

# 在 Windows (PowerShell) 上：
Get-NetTCPConnection -LocalPort 1455,1456,1457,1458,1459,1460,1461,1462,1463,1464,1465 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

然后重新运行 `gac auth chatgpt login`。

## 与 OpenAI 提供商的区别

| 特性     | OpenAI (`openai:`)          | ChatGPT OAuth (`chatgpt-oauth:`)          |
| -------- | --------------------------- | ----------------------------------------- |
| 身份验证 | API 密钥 (`OPENAI_API_KEY`) | OAuth（自动化浏览器流程）                 |
| 计费     | 按令牌 API 计费             | 基于订阅（ChatGPT Plus/Pro）              |
| 设置     | 手动输入 API 密钥           | 通过 `gac init` 或 `gac model` 自动 OAuth |
| 令牌管理 | 长期有效的 API 密钥         | OAuth 令牌（使用刷新令牌自动刷新）        |
| 模型     | 所有 OpenAI 模型            | Codex 优化模型                            |

## 安全说明

- **切勿将访问令牌提交**到版本控制
- GAC 将 OAuth 令牌存储在 `~/.gac/oauth/chatgpt-oauth.json`（在项目目录之外）
- OAuth 流程使用 PKCE（代码交换证明密钥）以增强安全性
- 本地回调服务器仅在 localhost 上运行（端口 1455-1465）
- 使用刷新令牌自动续订访问而无需重新身份验证

## 另请参阅

- [主要文档](USAGE.md)
- [故障排除指南](TROUBLESHOOTING.md)
- [OpenAI 的 Codex 文档](https://openai.com/codex)
