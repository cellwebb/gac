# 在 GAC 中使用 Claude Code

[English](../en/CLAUDE_CODE.md) | **简体中文** | [繁體中文](../zh-TW/CLAUDE_CODE.md) | [日本語](../ja/CLAUDE_CODE.md) | [한국어](../ko/CLAUDE_CODE.md) | [हिन्दी](../hi/CLAUDE_CODE.md) | [Tiếng Việt](../vi/CLAUDE_CODE.md) | [Français](../fr/CLAUDE_CODE.md) | [Русский](../ru/CLAUDE_CODE.md) | [Español](../es/CLAUDE_CODE.md) | [Português](../pt/CLAUDE_CODE.md) | [Norsk](../no/CLAUDE_CODE.md) | [Svenska](../sv/CLAUDE_CODE.md) | [Deutsch](../de/CLAUDE_CODE.md) | [Nederlands](../nl/CLAUDE_CODE.md) | [Italiano](../it/CLAUDE_CODE.md)

GAC 支持通过 Claude Code 订阅进行身份验证，允许您使用 Claude Code 订阅而不是支付昂贵的 Anthropic API 费用。这对于已经通过订阅获得 Claude Code 访问权限的用户来说是完美的选择。

## 什么是 Claude Code？

Claude Code 是 Anthropic 的订阅服务，提供基于 OAuth 的 Claude 模型访问。与使用 API 密钥（按令牌计费）不同，Claude Code 使用您订阅中的 OAuth 令牌。

## 优势

- **成本效益**：使用您现有的 Claude Code 订阅，而不是单独支付 API 访问费用
- **相同模型**：访问相同的 Claude 模型（例如 `claude-sonnet-4-5`）
- **独立计费**：Claude Code 使用与 Anthropic API 计费分离

## 设置

GAC 包含内置的 Claude Code OAuth 身份验证。设置过程完全自动化，将打开您的浏览器进行身份验证。

### 选项 1：在初始设置期间（推荐）

运行 `gac init` 时，只需选择"Claude Code"作为您的提供商：

```bash
gac init
```

向导将：

1. 要求您从提供商列表中选择"Claude Code"
2. 自动打开您的浏览器进行 OAuth 身份验证
3. 将您的访问令牌保存到 `~/.gac.env`
4. 设置默认模型

### 选项 2：稍后切换到 Claude Code

如果您已经配置了另一个提供商的 GAC 并想切换到 Claude Code：

```bash
gac model
```

然后：

1. 从提供商列表中选择"Claude Code"
2. 您的浏览器将自动打开进行 OAuth 身份验证
3. 令牌保存到 `~/.gac.env`
4. 模型自动配置

### 正常使用 GAC

身份验证后，像往常一样使用 GAC：

```bash
# 暂存您的更改
git add .

# 使用 Claude Code 生成和提交
gac

# 或者为单次提交覆盖模型
gac -m claude-code:claude-sonnet-4-5
```

## 可用模型

Claude Code 提供与 Anthropic API 相同的模型访问权限。当前的 Claude 4.5 系列模型包括：

- `claude-sonnet-4-5` - 最新且最智能的 Sonnet 模型，最适合编码
- `claude-haiku-4-5` - 快速高效
- `claude-opus-4-1` - 最复杂推理的最强能力模型

查看 [Claude 文档](https://docs.claude.com/en/docs/about-claude/models/overview) 获取可用模型的完整列表。

## 故障排除

### 令牌已过期

如果您看到身份验证错误，您的令牌可能已过期。通过运行重新身份验证：

```bash
gac model
```

然后选择"Claude Code"并选择"重新身份验证（获取新令牌）"。您的浏览器将打开进行新的 OAuth 身份验证。

### "未找到 CLAUDE_CODE_ACCESS_TOKEN"

这意味着 GAC 找不到您的访问令牌。通过运行身份验证：

```bash
gac model
```

然后从提供商列表中选择"Claude Code"。OAuth 流程将自动开始。

### "身份验证失败"

如果 OAuth 身份验证失败：

1. 确保您有活跃的 Claude Code 订阅
2. 检查您的浏览器是否正确打开
3. 如果问题持续存在，尝试不同的浏览器
4. 验证到 `claude.ai` 的网络连接
5. 检查端口 8765-8795 是否可用于本地回调服务器

## 与 Anthropic 提供商的差异

| 功能     | Anthropic (`anthropic:`)       | Claude Code (`claude-code:`)                          |
| -------- | ------------------------------ | ----------------------------------------------------- |
| 身份验证 | API 密钥 (`ANTHROPIC_API_KEY`) | OAuth（自动浏览器流程）                               |
| 计费     | 按令牌 API 计费                | 基于订阅                                              |
| 设置     | 手动 API 密钥输入              | 通过 `gac init` 或 `gac model` 自动 OAuth             |
| 令牌管理 | 长期 API 密钥                  | OAuth 令牌（可能过期，通过 `model` 易于重新身份验证） |
| 模型     | 相同模型                       | 相同模型                                              |

## 安全说明

- **永远不要提交您的访问令牌**到版本控制
- GAC 自动将令牌存储在 `~/.gac.env` 中（在您的项目目录外）
- 令牌可能过期，需要通过 `gac model` 重新身份验证
- OAuth 流程使用 PKCE（Proof Key for Code Exchange）增强安全性
- 本地回调服务器仅在本地主机运行（端口 8765-8795）

## 另请参阅

- [主要文档](USAGE.md)
- [故障排除指南](TROUBLESHOOTING.md)
- [Claude Code 文档](https://claude.ai/code)
