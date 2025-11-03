# gac 故障排除

[English](TROUBLESHOOTING.md) | **简体中文** | [繁體中文](TROUBLESHOOTING.zh-TW.md) | [日本語](TROUBLESHOOTING.ja.md) | [Français](TROUBLESHOOTING.fr.md)

本指南涵盖了安装、配置和运行 gac 的常见问题和解决方案。

## 目录

- [gac 故障排除](#gac-故障排除)
  - [目录](#目录)
  - [1. 安装问题](#1-安装问题)
  - [2. 配置问题](#2-配置问题)
  - [3. 提供商/API 错误](#3-提供商api-错误)
  - [4. 提交分组问题](#4-提交分组问题)
  - [5. 安全和密钥检测](#5-安全和密钥检测)
  - [6. Pre-commit 和 Lefthook 钩子问题](#6-pre-commit-和-lefthook-钩子问题)
  - [7. 常见工作流问题](#7-常见工作流问题)
  - [8. 常规调试](#8-常规调试)
  - [仍然遇到问题？](#仍然遇到问题)
  - [获取更多帮助](#获取更多帮助)

## 1. 安装问题

**问题：** 安装后找不到 `gac` 命令

- 确保你使用 `uv tool install gac` 或 `uvx gac` 安装
- 如果你使用 `uv tool install`，用 `uv tool list` 验证安装
- 确保 `uv` 已安装并在你的 `$PATH` 中
- 安装后重启你的终端

**问题：** 权限被拒绝或无法写入文件

- 检查目录权限
- 尝试使用适当的权限运行或更改目录所有权

## 2. 配置问题

**问题：** gac 找不到你的 API 密钥或模型

- 如果你是新用户，运行 `gac init` 以交互方式设置你的提供商、模型和 API 密钥
- 确保你的 `.gac.env` 或环境变量设置正确
- 运行 `gac --log-level=debug` 查看加载了哪些配置文件并调试配置问题
- 检查变量名中的拼写错误（例如，`GAC_GROQ_API_KEY`）

**问题：** 用户级 `$HOME/.gac.env` 更改未生效

- 确保你正在编辑操作系统的正确文件：
  - 在 macOS/Linux 上：`$HOME/.gac.env`（通常是 `/Users/<your-username>/.gac.env` 或 `/home/<your-username>/.gac.env`）
  - 在 Windows 上：`$HOME/.gac.env`（通常是 `C:\Users\<your-username>\.gac.env` 或使用 `%USERPROFILE%`）
- 运行 `gac --log-level=debug` 确认加载了用户级配置
- 重启你的终端或重新运行你的 shell 以重新加载环境变量
- 如果仍然无效，检查拼写错误和文件权限

**问题：** 项目级 `.gac.env` 更改未生效

- 确保你的项目在根目录（`.git` 文件夹旁边）包含一个 `.gac.env` 文件
- 运行 `gac --log-level=debug` 确认加载了项目级配置
- 如果你编辑了 `.gac.env`，重启你的终端或重新运行你的 shell 以重新加载环境变量
- 如果仍然无效，检查拼写错误和文件权限

**问题：** 无法设置或更改提交信息的语言

- 运行 `gac language`（或 `gac lang`）以交互方式从 25+ 种支持的语言中选择
- 使用 `-l <语言>` 标志为单次提交覆盖语言（例如，`gac -l zh-CN`，`gac -l Spanish`）
- 使用 `gac config show` 检查你的配置以查看当前语言设置
- 语言设置存储在你的 `.gac.env` 文件中的 `GAC_LANGUAGE`

## 3. 提供商/API 错误

**问题：** 身份验证或 API 错误

- 确保你为所选模型设置了正确的 API 密钥（例如，`ANTHROPIC_API_KEY`，`GROQ_API_KEY`）
- 仔细检查你的 API 密钥和提供商账户状态
- 对于 Ollama 和 LM Studio，确认 API URL 与你的本地实例匹配。仅在启用身份验证时才需要 API 密钥。

**问题：** 模型不可用或不受支持

- Streamlake 使用推理端点 ID 而不是模型名称。确保你从其控制台提供端点 ID。
- 验证模型名称正确且受你的提供商支持
- 查看提供商文档以了解可用模型

## 4. 提交分组问题

**问题：** `--group` 标志未按预期工作

- `--group` 标志会自动分析暂存的更改，并可以创建多个逻辑提交
- 即使使用 `--group`，LLM 也可能决定为你的一组暂存更改创建单个提交
- 这是有意为之的行为 - LLM 基于逻辑关系而不仅仅是数量来分组更改
- 确保你暂存了多个不相关的更改（例如，错误修复 + 功能添加）以获得最佳结果
- 使用 `gac --show-prompt` 调试 LLM 看到的内容

**问题：** 提交分组不正确或未按预期分组

- 分组由 LLM 对你的更改的分析决定
- 如果 LLM 确定更改在逻辑上相关，它可能会创建单个提交
- 尝试使用 `-h "提示"` 添加提示以引导分组逻辑（例如，`-h "将错误修复与重构分开"`）
- 在确认之前查看生成的分组
- 如果分组不适合你的用例，请分别提交更改

## 5. 安全和密钥检测

**问题：** 误报：密钥扫描检测到非密钥

- 安全扫描程序会查找类似于 API 密钥、令牌和密码的模式
- 如果你提交的是示例代码、测试装置或带有占位符密钥的文档，你可能会看到误报
- 如果你确定更改是安全的，使用 `--skip-secret-scan` 绕过扫描
- 考虑从提交中排除测试/示例文件，或使用明确标记的占位符

**问题：** 密钥扫描未检测到实际密钥

- 扫描程序使用模式匹配，可能无法捕获所有密钥类型
- 在提交之前，始终使用 `git diff --staged` 查看你的暂存更改
- 考虑使用额外的安全工具，如 `git-secrets` 或 `gitleaks`，以获得全面保护
- 报告任何遗漏的模式作为问题，以帮助改进检测

**问题：** 需要永久禁用密钥扫描

- 在你的 `.gac.env` 文件中设置 `GAC_SKIP_SECRET_SCAN=true`
- 使用 `gac config set GAC_SKIP_SECRET_SCAN true`
- 注意：仅在你有其他安全措施时才禁用

## 6. Pre-commit 和 Lefthook 钩子问题

**问题：** Pre-commit 或 lefthook 钩子失败并阻止提交

- 使用 `gac --no-verify` 暂时跳过所有 pre-commit 和 lefthook 钩子
- 修复导致钩子失败的根本问题
- 如果钩子太严格，考虑调整你的 pre-commit 或 lefthook 配置

**问题：** Pre-commit 或 lefthook 钩子运行时间过长或干扰工作流

- 使用 `gac --no-verify` 暂时跳过所有 pre-commit 和 lefthook 钩子
- 考虑在 `.pre-commit-config.yaml` 或 `.lefthook.yml` 中配置 pre-commit 钩子或 lefthook 钩子，使其对你的工作流不那么激进
- 查看你的钩子配置以优化性能

## 7. 常见工作流问题

**问题：** 没有要提交的更改 / 没有暂存内容

- gac 需要暂存的更改来生成提交信息
- 使用 `git add <文件>` 暂存更改，或使用 `gac -a` 自动暂存所有更改
- 检查 `git status` 查看哪些文件已被修改
- 使用 `gac diff` 查看你的更改的过滤视图

**问题：** 提交信息不符合预期

- 使用交互式反馈系统：输入 `r` 重新生成，`e` 编辑，或提供自然语言反馈
- 使用 `-h "你的提示"` 添加上下文以引导 LLM
- 使用 `-o` 获取更简单的单行信息，或使用 `-v` 获取更详细的信息
- 使用 `--show-prompt` 查看 LLM 接收的信息

**问题：** gac 太慢

- 使用 `gac -y` 跳过确认提示
- 使用 `gac -q` 以静默模式减少输出
- 考虑为常规提交使用更快/更便宜的模型
- 如果钩子让你慢下来，使用 `gac --no-verify` 跳过钩子

**问题：** 生成信息后无法编辑或提供反馈

- 在提示符处，输入 `e` 进入编辑模式（支持 vi/emacs 键绑定）
- 输入 `r` 不提供反馈而重新生成
- 或者直接输入你的反馈（例如，"让它更短"，"专注于错误修复"）
- 在空输入上按 Enter 再次查看提示

## 8. 常规调试

- 使用 `gac init` 以交互方式重置或更新你的配置
- 使用 `gac --log-level=debug` 获取详细的调试输出和日志记录
- 使用 `gac --show-prompt` 查看发送给 LLM 的提示
- 使用 `gac --help` 查看所有可用的命令行标志
- 使用 `gac config show` 查看所有当前配置值
- 检查日志以查找错误消息和堆栈跟踪
- 查看主 [README.md](../README.md) 了解功能、示例和快速入门说明

## 仍然遇到问题？

- 在 [GitHub 仓库](https://github.com/cellwebb/gac)上搜索现有问题或打开新问题
- 包括有关你的操作系统、Python 版本、gac 版本、提供商和错误输出的详细信息
- 你提供的详细信息越多，问题就能越快得到解决

## 获取更多帮助

- 有关功能和使用示例，请参阅主 [README.md](../README.md)
- 有关自定义系统提示，请参阅 [CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md)
- 有关贡献指南，请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)
- 有关许可证信息，请参阅 [../LICENSE](../LICENSE)
