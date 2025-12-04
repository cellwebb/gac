[English](../en/QWEN.md) | **简体中文** | [繁體中文](../zh-TW/QWEN.md) | [日本語](../ja/QWEN.md) | [한국어](../ko/QWEN.md) | [हिन्दी](../hi/QWEN.md) | [Tiếng Việt](../vi/QWEN.md) | [Français](../fr/QWEN.md) | [Русский](../ru/QWEN.md) | [Español](../es/QWEN.md) | [Português](../pt/QWEN.md) | [Norsk](../no/QWEN.md) | [Svenska](../sv/QWEN.md) | [Deutsch](../de/QWEN.md) | [Nederlands](../nl/QWEN.md) | [Italiano](../it/QWEN.md)

# 在 GAC 中使用 Qwen.ai

GAC 支持通过 Qwen.ai OAuth 进行身份验证，允许您使用 Qwen.ai 帐户生成提交消息。这使用了 OAuth 设备流身份验证，提供无缝的登录体验。

## 什么是 Qwen.ai？

Qwen.ai 是阿里云的 AI 平台，提供对 Qwen 系列大型语言模型的访问。GAC 支持基于 OAuth 的身份验证，允许您使用 Qwen.ai 帐户，而无需手动管理 API 密钥。

## 优势

- **轻松验证**：OAuth 设备流 - 只需使用浏览器登录
- **无需 API 密钥管理**：自动处理身份验证
- **访问 Qwen 模型**：使用强大的 Qwen 模型生成提交消息

## 设置

GAC 包含使用设备流的 Qwen.ai 内置 OAuth 身份验证。设置过程将显示代码并打开浏览器进行身份验证。

### 选项 1：初始设置期间（推荐）

运行 `gac init` 时，只需从提供商列表中选择 "Qwen.ai (OAuth)"：

```bash
gac init
```

向导将：

1. 要求您从提供商列表中选择 "Qwen.ai (OAuth)"
2. 显示设备代码并打开浏览器
3. 您将在 Qwen.ai 上进行身份验证并输入代码
4. 安全保存您的访问令牌
5. 设置默认模型

### 选项 2：稍后切换到 Qwen.ai

如果您已经使用其他提供商配置了 GAC，并希望切换到 Qwen.ai：

```bash
gac model
```

然后：

1. 从提供商列表中选择 "Qwen.ai (OAuth)"
2. 按照设备代码身份验证流程操作
3. 令牌安全保存到 `~/.gac/oauth/qwen.json`
4. 自动配置模型

### 选项 3：直接登录

您也可以使用以下命令直接进行身份验证：

```bash
gac auth qwen login
```

这将：

1. 显示设备代码
2. 打开浏览器访问 Qwen.ai 身份验证页面
3. 身份验证后，令牌将自动保存

### 正常使用 GAC

验证后，像往常一样使用 GAC：

```bash
# 暂存更改
git add .

# 使用 Qwen.ai 生成并提交
gac

# 或为单个提交覆盖模型
gac -m qwen:qwen3-coder-plus
```

## 可用模型

Qwen.ai OAuth 集成使用：

- `qwen3-coder-plus` - 针对编码任务进行了优化（默认）

这是通过 portal.qwen.ai OAuth 端点可用的模型。对于其他 Qwen 模型，请考虑使用 OpenRouter 提供商，它提供更多 Qwen 模型选项。

## 身份验证命令

GAC 提供了几个用于管理 Qwen.ai 身份验证的命令：

```bash
# 登录到 Qwen.ai
gac auth qwen login

# 检查身份验证状态
gac auth qwen status

# 注销并删除存储的令牌
gac auth qwen logout

# 检查所有 OAuth 提供商状态
gac auth
```

### 登录选项

```bash
# 标准登录（自动打开浏览器）
gac auth qwen login

# 不打开浏览器登录（显示手动访问的 URL）
gac auth qwen login --no-browser

# 安静模式（最小输出）
gac auth qwen login --quiet
```

## 故障排除

### 令牌过期

如果看到身份验证错误，可能是您的令牌已过期。通过运行以下命令重新验证：

```bash
gac auth qwen login
```

设备代码流将开始，您的浏览器将打开以进行重新验证。

### 检查身份验证状态

要检查您当前是否已通过身份验证：

```bash
gac auth qwen status
```

或一次检查所有提供商：

```bash
gac auth
```

### 注销

要删除存储的令牌：

```bash
gac auth qwen logout
```

### "未找到 Qwen 身份验证"

这意味着 GAC 找不到您的访问令牌。通过运行以下命令进行身份验证：

```bash
gac auth qwen login
```

或运行 `gac model` 并从提供商列表中选择 "Qwen.ai (OAuth)"。

### "身份验证失败"

如果 OAuth 身份验证失败：

1. 确保您拥有 Qwen.ai 帐户
2. 检查浏览器是否正确打开
3. 验证您是否正确输入了设备代码
4. 如果问题仍然存在，请尝试使用其他浏览器
5. 验证到 `qwen.ai` 的网络连接

### 设备代码不起作用

如果设备代码身份验证不起作用：

1. 确保代码未过期（代码在有限时间内有效）
2. 尝试再次运行 `gac auth qwen login` 获取新代码
3. 如果浏览器打开失败，请使用 `--no-browser` 标志并手动访问 URL

## 安全说明

- **切勿将访问令牌提交**到版本控制
- GAC 自动将令牌存储在 `~/.gac/oauth/qwen.json`（项目目录之外）
- 令牌文件具有受限权限（仅所有者可读）
- 令牌可能会过期，需要重新验证
- OAuth 设备流专为无头系统上的安全身份验证而设计

## 另请参阅

- [主要文档](USAGE.md)
- [Claude Code 设置](CLAUDE_CODE.md)
- [故障排除指南](TROUBLESHOOTING.md)
- [Qwen.ai 文档](https://qwen.ai)
