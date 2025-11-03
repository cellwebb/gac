# gac 故障排除

[English](TROUBLESHOOTING.md) | [简体中文](TROUBLESHOOTING.zh-CN.md) | 繁體中文

本指南涵蓋了安裝、設定和執行 gac 的常見問題和解決方案。

## 目錄

- [gac 故障排除](#gac-故障排除)
  - [目錄](#目錄)
  - [1. 安裝問題](#1-安裝問題)
  - [2. 設定問題](#2-設定問題)
  - [3. 提供者/API 錯誤](#3-提供者api-錯誤)
  - [4. 提交分組問題](#4-提交分組問題)
  - [5. 安全和密鑰檢測](#5-安全和密鑰檢測)
  - [6. Pre-commit 和 Lefthook 鉤子問題](#6-pre-commit-和-lefthook-鉤子問題)
  - [7. 常見工作流問題](#7-常見工作流問題)
  - [8. 常規除錯](#8-常規除錯)
  - [仍然遇到問題？](#仍然遇到問題)
  - [獲取更多幫助](#獲取更多幫助)

## 1. 安裝問題

**問題：** 安裝後找不到 `gac` 命令

- 確保你使用 `uv tool install gac` 或 `uvx gac` 安裝
- 如果你使用 `uv tool install`，用 `uv tool list` 驗證安裝
- 確保 `uv` 已安裝並在你的 `$PATH` 中
- 安裝後重新啟動你的終端機

**問題：** 權限被拒絕或無法寫入檔案

- 檢查目錄權限
- 嘗試使用適當的權限執行或更改目錄擁有權

## 2. 設定問題

**問題：** gac 找不到你的 API 密鑰或模型

- 如果你是新使用者，執行 `gac init` 以互動方式設定你的提供者、模型和 API 密鑰
- 確保你的 `.gac.env` 或環境變數設定正確
- 執行 `gac --log-level=debug` 查看載入了哪些設定檔並除錯設定問題
- 檢查變數名稱中的拼寫錯誤（例如，`GAC_GROQ_API_KEY`）

**問題：** 使用者級 `$HOME/.gac.env` 變更未生效

- 確保你正在編輯作業系統的正確檔案：
  - 在 macOS/Linux 上：`$HOME/.gac.env`（通常是 `/Users/<your-username>/.gac.env` 或 `/home/<your-username>/.gac.env`）
  - 在 Windows 上：`$HOME/.gac.env`（通常是 `C:\Users\<your-username>\.gac.env` 或使用 `%USERPROFILE%`）
- 執行 `gac --log-level=debug` 確認載入了使用者級設定
- 重新啟動你的終端機或重新執行你的 shell 以重新載入環境變數
- 如果仍然無效，檢查拼寫錯誤和檔案權限

**問題：** 專案級 `.gac.env` 變更未生效

- 確保你的專案在根目錄（`.git` 資料夾旁邊）包含一個 `.gac.env` 檔案
- 執行 `gac --log-level=debug` 確認載入了專案級設定
- 如果你編輯了 `.gac.env`，重新啟動你的終端機或重新執行你的 shell 以重新載入環境變數
- 如果仍然無效，檢查拼寫錯誤和檔案權限

**問題：** 無法設定或更改提交訊息的語言

- 執行 `gac language`（或 `gac lang`）以互動方式從 25+ 種支援的語言中選擇
- 使用 `-l <語言>` 標誌為單次提交覆寫語言（例如，`gac -l zh-TW`，`gac -l Spanish`）
- 使用 `gac config show` 檢查你的設定以查看當前語言設定
- 語言設定儲存在你的 `.gac.env` 檔案中的 `GAC_LANGUAGE`

## 3. 提供者/API 錯誤

**問題：** 身份驗證或 API 錯誤

- 確保你為所選模型設定了正確的 API 密鑰（例如，`ANTHROPIC_API_KEY`，`GROQ_API_KEY`）
- 仔細檢查你的 API 密鑰和提供者帳戶狀態
- 對於 Ollama 和 LM Studio，確認 API URL 與你的本地實例匹配。僅在啟用身份驗證時才需要 API 密鑰。

**問題：** 模型不可用或不受支援

- Streamlake 使用推理端點 ID 而不是模型名稱。確保你從其控制台提供端點 ID。
- 驗證模型名稱正確且受你的提供者支援
- 查看提供者文件以了解可用模型

## 4. 提交分組問題

**問題：** `--group` 標誌未按預期工作

- `--group` 標誌會自動分析暫存的變更，並可以建立多個邏輯提交
- 即使使用 `--group`，LLM 也可能決定為你的一組暫存變更建立單個提交
- 這是有意為之的行為 - LLM 基於邏輯關係而不僅僅是數量來分組變更
- 確保你暫存了多個不相關的變更（例如，錯誤修復 + 功能新增）以獲得最佳結果
- 使用 `gac --show-prompt` 除錯 LLM 看到的內容

**問題：** 提交分組不正確或未按預期分組

- 分組由 LLM 對你的變更的分析決定
- 如果 LLM 確定變更在邏輯上相關，它可能會建立單個提交
- 嘗試使用 `-h "提示"` 新增提示以引導分組邏輯（例如，`-h "將錯誤修復與重構分開"`）
- 在確認之前查看生成的分組
- 如果分組不適合你的用例，請分別提交變更

## 5. 安全和密鑰檢測

**問題：** 誤報：密鑰掃描檢測到非密鑰

- 安全掃描程式會尋找類似於 API 密鑰、權杖和密碼的模式
- 如果你提交的是範例程式碼、測試裝置或帶有佔位符密鑰的文件，你可能會看到誤報
- 如果你確定變更是安全的，使用 `--skip-secret-scan` 繞過掃描
- 考慮從提交中排除測試/範例檔案，或使用明確標記的佔位符

**問題：** 密鑰掃描未檢測到實際密鑰

- 掃描程式使用模式匹配，可能無法捕獲所有密鑰類型
- 在提交之前，始終使用 `git diff --staged` 查看你的暫存變更
- 考慮使用額外的安全工具，如 `git-secrets` 或 `gitleaks`，以獲得全面保護
- 報告任何遺漏的模式作為問題，以幫助改進檢測

**問題：** 需要永久停用密鑰掃描

- 在你的 `.gac.env` 檔案中設定 `GAC_SKIP_SECRET_SCAN=true`
- 使用 `gac config set GAC_SKIP_SECRET_SCAN true`
- 注意：僅在你有其他安全措施時才停用

## 6. Pre-commit 和 Lefthook 鉤子問題

**問題：** Pre-commit 或 lefthook 鉤子失敗並阻止提交

- 使用 `gac --no-verify` 暫時跳過所有 pre-commit 和 lefthook 鉤子
- 修復導致鉤子失敗的根本問題
- 如果鉤子太嚴格，考慮調整你的 pre-commit 或 lefthook 設定

**問題：** Pre-commit 或 lefthook 鉤子執行時間過長或干擾工作流

- 使用 `gac --no-verify` 暫時跳過所有 pre-commit 和 lefthook 鉤子
- 考慮在 `.pre-commit-config.yaml` 或 `.lefthook.yml` 中設定 pre-commit 鉤子或 lefthook 鉤子，使其對你的工作流不那麼激進
- 查看你的鉤子設定以最佳化效能

## 7. 常見工作流問題

**問題：** 沒有要提交的變更 / 沒有暫存內容

- gac 需要暫存的變更來生成提交訊息
- 使用 `git add <檔案>` 暫存變更，或使用 `gac -a` 自動暫存所有變更
- 檢查 `git status` 查看哪些檔案已被修改
- 使用 `gac diff` 查看你的變更的篩選視圖

**問題：** 提交訊息不符合預期

- 使用互動式反饋系統：輸入 `r` 重新生成，`e` 編輯，或提供自然語言反饋
- 使用 `-h "你的提示"` 新增上下文以引導 LLM
- 使用 `-o` 獲取更簡單的單行訊息，或使用 `-v` 獲取更詳細的訊息
- 使用 `--show-prompt` 查看 LLM 接收的訊息

**問題：** gac 太慢

- 使用 `gac -y` 跳過確認提示
- 使用 `gac -q` 以靜默模式減少輸出
- 考慮為常規提交使用更快/更便宜的模型
- 如果鉤子讓你慢下來，使用 `gac --no-verify` 跳過鉤子

**問題：** 生成訊息後無法編輯或提供反饋

- 在提示符處，輸入 `e` 進入編輯模式（支援 vi/emacs 鍵綁定）
- 輸入 `r` 不提供反饋而重新生成
- 或者直接輸入你的反饋（例如，"讓它更短"，"專注於錯誤修復"）
- 在空輸入上按 Enter 再次查看提示

## 8. 常規除錯

- 使用 `gac init` 以互動方式重置或更新你的設定
- 使用 `gac --log-level=debug` 獲取詳細的除錯輸出和日誌記錄
- 使用 `gac --show-prompt` 查看傳送給 LLM 的提示
- 使用 `gac --help` 查看所有可用的命令列標誌
- 使用 `gac config show` 查看所有當前設定值
- 檢查日誌以尋找錯誤訊息和堆疊追蹤
- 查看主 [README.md](../README.md) 了解功能、範例和快速入門說明

## 仍然遇到問題？

- 在 [GitHub 儲存庫](https://github.com/cellwebb/gac)上搜尋現有問題或開啟新問題
- 包括有關你的作業系統、Python 版本、gac 版本、提供者和錯誤輸出的詳細資訊
- 你提供的詳細資訊越多，問題就能越快得到解決

## 獲取更多幫助

- 有關功能和使用範例，請參閱主 [README.md](../README.md)
- 有關自訂系統提示，請參閱 [CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md)
- 有關貢獻指南，請參閱 [CONTRIBUTING.md](CONTRIBUTING.md)
- 有關授權資訊，請參閱 [../LICENSE](../LICENSE)
