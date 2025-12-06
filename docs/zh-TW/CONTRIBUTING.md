# 為 gac 貢獻

[English](../en/CONTRIBUTING.md) | [简体中文](../zh-CN/CONTRIBUTING.md) | **繁體中文** | [日本語](../ja/CONTRIBUTING.md) | [한국어](../ko/CONTRIBUTING.md) | [हिन्दी](../hi/CONTRIBUTING.md) | [Tiếng Việt](../vi/CONTRIBUTING.md) | [Français](../fr/CONTRIBUTING.md) | [Русский](../ru/CONTRIBUTING.md) | [Español](../es/CONTRIBUTING.md) | [Português](../pt/CONTRIBUTING.md) | [Norsk](../no/CONTRIBUTING.md) | [Svenska](../sv/CONTRIBUTING.md) | [Deutsch](../de/CONTRIBUTING.md) | [Nederlands](../nl/CONTRIBUTING.md) | [Italiano](../it/CONTRIBUTING.md)

感謝你有興趣為本專案做出貢獻！我們非常感謝你的幫助。請遵循這些指南，使每個人的流程都順暢。

## 目錄

- [為 gac 貢獻](#為-gac-貢獻)
  - [目錄](#目錄)
  - [開發環境設定](#開發環境設定)
    - [快速設定](#快速設定)
    - [備選設定（如果你更喜歡分步驟）](#備選設定如果你更喜歡分步驟)
    - [可用命令](#可用命令)
  - [版本升級](#版本升級)
    - [如何升級版本](#如何升級版本)
    - [發布流程](#發布流程)
    - [使用 bump-my-version（可選）](#使用-bump-my-version可選)
  - [編碼標準](#編碼標準)
  - [Git 鉤子（Lefthook）](#git-鉤子lefthook)
    - [設定](#設定)
    - [跳過 Git 鉤子](#跳過-git-鉤子)
  - [測試指南](#測試指南)
    - [執行測試](#執行測試)
      - [提供者整合測試](#提供者整合測試)
  - [行為準則](#行為準則)
  - [授權](#授權)
  - [獲取幫助](#獲取幫助)

## 開發環境設定

本專案使用 `uv` 進行依賴管理，並提供 Makefile 用於常見開發任務：

### 快速設定

```bash
# 一條命令設定所有內容，包括 Lefthook 鉤子
make dev
```

此命令將：

- 安裝開發依賴項
- 安裝 git 鉤子
- 在所有檔案上執行 Lefthook 鉤子以修復任何現有問題

### 備選設定（如果你更喜歡分步驟）

```bash
# 建立虛擬環境並安裝依賴項
make setup

# 安裝開發依賴項
make dev

# 安裝 Lefthook 鉤子
brew install lefthook  # 或參見下面的文件了解替代方案
lefthook install
lefthook run pre-commit --all
```

### 可用命令

- `make setup` - 建立虛擬環境並安裝所有依賴項
- `make dev` - **完整的開發設定** - 包括 Lefthook 鉤子
- `make test` - 執行標準測試（不包括整合測試）
- `make test-integration` - 僅執行整合測試（需要 API 密鑰）
- `make test-all` - 執行所有測試
- `make test-cov` - 執行帶覆蓋率報告的測試
- `make lint` - 檢查程式碼品質（ruff、prettier、markdownlint）
- `make format` - 自動修復程式碼格式問題

## 版本升級

**重要**：當 PR 包含應該發布的變更時，應該在 `src/gac/__version__.py` 中包含版本升級。

### 如何升級版本

1. 編輯 `src/gac/__version__.py` 並增加版本號
2. 遵循 [語義化版本](https://semver.org/)：
   - **修補**（1.6.X）：錯誤修復、小改進
   - **次要**（1.X.0）：新功能、向後相容的變更（例如，新增新提供者）
   - **主要**（X.0.0）：破壞性變更

### 發布流程

通過推送版本標籤觸發發布：

1. 將帶有版本升級的 PR 合併到 main
2. 建立標籤：`git tag v1.6.1`
3. 推送標籤：`git push origin v1.6.1`
4. GitHub Actions 自動發布到 PyPI

範例：

```python
# src/gac/__version__.py
__version__ = "1.6.1"  # 從 1.6.0 升級
```

### 使用 bump-my-version（可選）

如果你安裝了 `bump-my-version`，你可以在本機使用它：

```bash
# 對於錯誤修復：
bump-my-version bump patch

# 對於新功能：
bump-my-version bump minor

# 對於破壞性變更：
bump-my-version bump major
```

## 編碼標準

- 目標 Python 3.10+（3.10、3.11、3.12、3.13、3.14）
- 對所有函式參數和返回值使用類型提示
- 保持程式碼清潔、緊湊和可讀
- 避免不必要的複雜性
- 使用日誌記錄而不是 print 陳述式
- 格式化由 `ruff` 處理（linting、格式化和匯入排序一體化工具；最大行長度：120）
- 使用 `pytest` 編寫最少、有效的測試

## Git 鉤子（Lefthook）

本專案使用 [Lefthook](https://github.com/evilmartians/lefthook) 保持程式碼品質檢查快速且一致。設定的鉤子鏡像了我們以前的 pre-commit 設定：

- `ruff` - Python linting 和格式化（替代 black、isort 和 flake8）
- `markdownlint-cli2` - Markdown linting
- `prettier` - 檔案格式化（markdown、yaml、json）
- `check-upstream` - 自訂鉤子以檢查上游變更

### 設定

**推薦方法：**

```bash
make dev
```

**手動設定（如果你更喜歡分步驟）：**

1. 安裝 Lefthook（選擇與你的設定匹配的選項）：

   ```sh
   brew install lefthook          # macOS (Homebrew)
   # 或
   cargo install lefthook         # Rust 工具鏈
   # 或
   asdf plugin add lefthook && asdf install lefthook latest
   ```

2. 安裝 git 鉤子：

   ```sh
   lefthook install
   ```

3. （可選）對所有檔案執行：

   ```sh
   lefthook run pre-commit --all
   ```

鉤子現在將在每次提交時自動執行。如果任何檢查失敗，你需要在提交之前修復問題。

### 跳過 Git 鉤子

如果你需要暫時跳過 Lefthook 檢查，使用 `--no-verify` 標誌：

```sh
git commit --no-verify -m "你的提交訊息"
```

注意：這應該僅在絕對必要時使用，因為它繞過了重要的程式碼品質檢查。

## 測試指南

專案使用 pytest 進行測試。新增新功能或修復錯誤時，請包括涵蓋你變更的測試。

注意，`scripts/` 目錄包含用於無法使用 pytest 輕鬆測試的功能的測試指令碼。
可以隨意在此處新增指令碼以測試複雜場景或難以使用標準 pytest 框架實現的整合測試。

### 執行測試

```sh
# 執行標準測試（不包括真實 API 呼叫的整合測試）
make test

# 僅執行提供者整合測試（需要 API 密鑰）
make test-integration

# 執行所有測試，包括提供者整合測試
make test-all

# 執行帶覆蓋率的測試
make test-cov

# 執行特定測試檔案
uv run -- pytest tests/test_prompt.py

# 執行特定測試
uv run -- pytest tests/test_prompt.py::TestExtractRepositoryContext::test_extract_repository_context_with_docstring
```

#### 提供者整合測試

提供者整合測試進行真實的 API 呼叫以驗證提供者實作與實際 API 正確工作。這些測試標記為 `@pytest.mark.integration` 並預設跳過以：

- 避免在常規開發期間消耗 API 積分
- 防止未設定 API 密鑰時測試失敗
- 保持測試執行快速以進行快速迭代

要執行提供者整合測試：

1. **為你想測試的提供者設定 API 密鑰**：

   ```sh
   export ANTHROPIC_API_KEY="your-key"
   export CEREBRAS_API_KEY="your-key"
   export GEMINI_API_KEY="your-key"
   export GROQ_API_KEY="your-key"
   export OPENAI_API_KEY="your-key"
   export OPENROUTER_API_KEY="your-key"
   export STREAMLAKE_API_KEY="your-key"
   export ZAI_API_KEY="your-key"
   # LM Studio 和 Ollama 需要執行本機實例
   # LM Studio 和 Ollama 的 API 密鑰是可選的，除非你的部署強制執行身份驗證
   ```

2. **執行提供者測試**：

   ```sh
   make test-integration
   ```

對於未設定 API 密鑰的提供者，測試將跳過。這些測試有助於及早檢測 API 變更並確保與提供者 API 的相容性。

## 行為準則

要尊重和建設性。不會容忍騷擾或辱罵行為。

## 授權

通過貢獻，你同意你的貢獻將在與專案相同的授權下獲得授權。

---

## 獲取幫助

- 有關故障排除，請參閱 [TROUBLESHOOTING.md](../en/TROUBLESHOOTING.md)
- 有關使用和 CLI 選項，請參閱 [../../USAGE.md](../../USAGE.md)
- 有關授權詳細資訊，請參閱 [../../LICENSE](../../LICENSE)

感謝你幫助改進 gac！
