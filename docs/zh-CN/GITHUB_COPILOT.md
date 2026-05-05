# 使用 GitHub Copilot 与 GAC

[English](../en/GITHUB_COPILOT.md) | **简体中文** | [繁體中文](../zh-TW/GITHUB_COPILOT.md) | [日本語](../ja/GITHUB_COPILOT.md) | [한국어](../ko/GITHUB_COPILOT.md) | [हिन्दी](../hi/GITHUB_COPILOT.md) | [Tiếng Việt](../vi/GITHUB_COPILOT.md) | [Français](../fr/GITHUB_COPILOT.md) | [Русский](../ru/GITHUB_COPILOT.md) | [Español](../es/GITHUB_COPILOT.md) | [Português](../pt/GITHUB_COPILOT.md) | [Norsk](../no/GITHUB_COPILOT.md) | [Svenska](../sv/GITHUB_COPILOT.md) | [Deutsch](../de/GITHUB_COPILOT.md) | [Nederlands](../nl/GITHUB_COPILOT.md) | [Italiano](../it/GITHUB_COPILOT.md)

GAC 支持通过 GitHub Copilot 进行身份验证，让您可以使用 Copilot 订阅来访问 OpenAI、Anthropic、Google 等的模型——所有这些都包含在您的 GitHub Copilot 计划中。

## 什么是 GitHub Copilot OAuth？

GitHub Copilot OAuth 使用 **Device Flow**——一种安全的、基于浏览器的身份验证方法，不需要本地回调服务器。您访问一个 URL，输入一次性代码，并授权 GAC 使用您的 Copilot 访问权限。在幕后，GAC 将您长期有效的 GitHub OAuth 令牌交换为短期 Copilot 会话令牌（约30分钟），以授予对 Copilot API 的访问权限。

这使您可以通过单一订阅访问多个提供商的模型：

- **OpenAI** — `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`
- **Anthropic** — `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5`
- **Google** — `gemini-2.5-pro`, `gemini-2.5-flash`

## 优势

- **多提供商访问**：通过单一订阅使用 OpenAI、Anthropic 和 Google 的模型
- **成本效益**：使用现有的 Copilot 订阅，无需单独支付 API 密钥费用
- **无需管理 API 密钥**：Device Flow 身份验证——无需轮换或存储密钥
- **GitHub Enterprise 支持**：通过 `--host` 标志支持 GHE 实例

## 设置

### 选项 1：初始设置期间（推荐）

运行 `gac init` 时，只需选择"Copilot"作为您的提供商：

```bash
gac init
```

向导将：

1. 要求您从提供商列表中选择"Copilot"
2. 显示一次性代码并打开您的浏览器进行 Device Flow 身份验证
3. 将您的 OAuth 令牌保存到 `~/.gac/oauth/copilot.json`
4. 设置默认模型

### 选项 2：稍后切换到 Copilot

如果您已经将 GAC 配置为另一个提供商：

```bash
gac model
```

然后从提供商列表中选择"Copilot"并进行身份验证。

### 选项 3：直接登录

直接进行身份验证，无需更改默认模型：

```bash
gac auth copilot login
```

### 正常使用 GAC

身份验证后，像往常一样使用 GAC：

```bash
# 暂存您的更改
git add .

# 使用 Copilot 生成并提交
gac

# 或者为单次提交覆盖模型
gac -m copilot:gpt-4.1
gac -m copilot:claude-sonnet-4.5
gac -m copilot:gemini-2.5-pro
```

## 可用模型

Copilot 提供对多个提供商模型的访问。当前模型包括：

| 提供商    | 模型                                                                                           |
| --------- | ---------------------------------------------------------------------------------------------- |
| OpenAI    | `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`                                           |
| Anthropic | `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5` |
| Google    | `gemini-2.5-pro`, `gemini-2.5-flash`                                                           |

> **注意：** 登录后显示的模型列表仅供参考，可能会随着 GitHub 添加新模型而过时。请查看 [GitHub Copilot 文档](https://docs.github.com/en/copilot) 获取最新的可用模型。

## GitHub Enterprise

要使用 GitHub Enterprise 实例进行身份验证：

```bash
gac auth copilot login --host ghe.mycompany.com
```

GAC 将自动使用适合您 GHE 实例的 Device Flow 和 API 端点。会话令牌按主机缓存，因此不同的 GHE 实例会独立处理。

## CLI 命令

GAC 提供专用的 CLI 命令用于 Copilot 身份验证管理：

### 登录

使用 GitHub Copilot 进行身份验证或重新身份验证：

```bash
gac auth copilot login
```

您的浏览器将打开一个 Device Flow 页面，您需要在其中输入一次性代码。如果您已经过身份验证，将询问您是否要重新身份验证。

对于 GitHub Enterprise：

```bash
gac auth copilot login --host ghe.mycompany.com
```

### 登出

删除存储的 Copilot 令牌：

```bash
gac auth copilot logout
```

这将删除存储在 `~/.gac/oauth/copilot.json` 的令牌文件和会话缓存。

### 状态

检查您当前的 Copilot 身份验证状态：

```bash
gac auth copilot status
```

或一次检查所有提供商：

```bash
gac auth
```

## 工作原理

Copilot 身份验证流程与 ChatGPT 和 Claude Code OAuth 不同：

1. **Device Flow** — GAC 从 GitHub 请求设备代码并显示它
2. **浏览器授权** — 您访问 URL 并输入代码
3. **令牌轮询** — GAC 轮询 GitHub 直到您完成授权
4. **会话令牌交换** — GitHub OAuth 令牌被交换为短期 Copilot 会话令牌
5. **自动刷新** — 会话令牌（约30分钟）从缓存的 OAuth 令牌自动刷新

与基于 PKCE 的 OAuth（ChatGPT/Claude Code）不同，Device Flow 不需要本地回调服务器或端口管理。

## 故障排除

### "未找到 Copilot 身份验证"

运行登录命令进行身份验证：

```bash
gac auth copilot login
```

### "无法获取 Copilot 会话令牌"

这意味着 GAC 获取了 GitHub OAuth 令牌，但无法将其交换为 Copilot 会话令牌。通常这意味着：

1. **没有 Copilot 订阅** — 您的 GitHub 账户没有活跃的 Copilot 订阅
2. **令牌被撤销** — OAuth 令牌已被撤销；使用 `gac auth copilot login` 重新身份验证

### 会话令牌过期

会话令牌在大约30分钟后过期。GAC 从缓存的 OAuth 令牌自动刷新它们，因此您不需要频繁重新身份验证。如果自动刷新失败：

```bash
gac auth copilot login
```

### "无效或不安全的主机名"

`--host` 标志严格验证主机名以防止 SSRF 攻击。如果您看到此错误：

- 确保主机名不包含端口（例如，使用 `ghe.company.com` 而不是 `ghe.company.com:8080`）
- 不要包含协议或路径（例如，使用 `ghe.company.com` 而不是 `https://ghe.company.com/api`）
- 出于安全考虑，私有 IP 地址和 `localhost` 被阻止

### GitHub Enterprise 问题

如果 GHE 身份验证失败：

1. 验证您的 GHE 实例已启用 Copilot
2. 检查您的 GHE 主机名是否可以从您的机器访问
3. 确保您的 GHE 账户拥有 Copilot 许可证
4. 尝试明确使用 `--host` 标志：`gac auth copilot login --host ghe.mycompany.com`

## 与其他 OAuth 提供商的区别

| 特性         | ChatGPT OAuth        | Claude Code          | Copilot                                 |
| ------------ | -------------------- | -------------------- | --------------------------------------- |
| 身份验证方法 | PKCE（浏览器回调）   | PKCE（浏览器回调）   | Device Flow（一次性代码）               |
| 回调服务器   | 端口 1455-1465       | 端口 8765-8795       | 不需要                                  |
| 令牌生命周期 | 长期有效（自动刷新） | 过期（重新身份验证） | 会话约30分钟（自动刷新）                |
| 模型         | Codex 优化的 OpenAI  | Claude 系列          | 多提供商（OpenAI + Anthropic + Google） |
| GHE 支持     | 否                   | 否                   | 是（`--host` 标志）                     |

## 安全说明

- **切勿将您的 OAuth 令牌提交**到版本控制
- GAC 将 OAuth 令牌存储在 `~/.gac/oauth/copilot.json`（在项目目录之外）
- 会话令牌缓存在 `~/.gac/oauth/copilot_session.json` 中，权限为 `0o600`
- 主机名经过严格验证以防止 SSRF 和 URL 注入攻击
- 私有 IP 地址、环回地址和 `localhost` 作为主机名被阻止
- Device Flow 不暴露任何本地端口，减少了攻击面

## 另请参阅

- [主要文档](USAGE.md)
- [故障排除指南](TROUBLESHOOTING.md)
- [ChatGPT OAuth 指南](CHATGPT_OAUTH.md)
- [Claude Code 指南](CLAUDE_CODE.md)
- [GitHub Copilot 文档](https://docs.github.com/en/copilot)
