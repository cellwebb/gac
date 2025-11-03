# 為 gac 貢獻

[English](../en/CONTRIBUTING.md) | [简体中文](../zh-CN/CONTRIBUTING.md) | **繁體中文** | [日本語](../ja/CONTRIBUTING.md) | [Français](../fr/CONTRIBUTING.md) | [Русский](../ru/CONTRIBUTING.md) | [Español](../es/CONTRIBUTING.md) | [Português](../pt/CONTRIBUTING.md) | [हिन्दी](../hi/CONTRIBUTING.md)

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
  - [新增新的 AI 提供者](#新增新的-ai-提供者)
    - [新增新提供者的清單](#新增新提供者的清單)
    - [範例實作](#範例實作)
    - [關鍵點](#關鍵點)
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

## 新增新的 AI 提供者

新增新的 AI 提供者時，你需要更新程式碼庫中的多個檔案。遵循此綜合清單：

### 新增新提供者的清單

- [ ] **1. 建立提供者實作**（`src/gac/providers/<provider_name>.py`）

  - 建立一個以提供者命名的新檔案（例如，`minimax.py`）
  - 實作 `call_<provider>_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str`
  - 如果提供者支援，使用 OpenAI 相容格式
  - 從環境變數 `<PROVIDER>_API_KEY` 處理 API 密鑰
  - 包括使用 `AIError` 類型的適當錯誤處理：
    - `AIError.authentication_error()` 用於身份驗證問題
    - `AIError.rate_limit_error()` 用於速率限制（HTTP 429）
    - `AIError.timeout_error()` 用於逾時
    - `AIError.model_error()` 用於模型錯誤和空/null 內容
  - 設定 API 端點 URL
  - 對 HTTP 請求使用 120 秒逾時

- [ ] **2. 在套件中註冊提供者**（`src/gac/providers/__init__.py`）

  - 新增匯入：`from .<provider> import call_<provider>_api`
  - 新增到 `__all__` 清單：`"call_<provider>_api"`

- [ ] **3. 在 AI 模組中註冊提供者**（`src/gac/ai.py`）

  - 在 `from gac.providers import (...)` 部分新增匯入
  - 新增到 `provider_funcs` 字典：`"provider-name": call_<provider>_api`

- [ ] **4. 新增到支援的提供者清單**（`src/gac/ai_utils.py`）

  - 將 `"provider-name"` 新增到 `generate_with_retries()` 中的 `supported_providers` 清單
  - 保持清單按字母順序排序

- [ ] **5. 新增到互動式設定**（`src/gac/init_cli.py`）

  - 將元組新增到 `providers` 清單：`("Provider Name", "default-model-name")`
  - 保持清單按字母順序排序
  - 如果需要，新增任何特殊處理（如 Ollama/LM Studio 的本機提供者）

- [ ] **6. 更新範例設定**（`.gac.env.example`）

  - 以格式新增範例模型設定：`# GAC_MODEL=provider:model-name`
  - 新增 API 密鑰條目：`# <PROVIDER>_API_KEY=your_key_here`
  - 保持條目按字母順序排序
  - 如果適用，為可選密鑰新增註解

- [ ] **7. 更新文件**（`README.md` 和 `README.zh-CN.md`）

  - 在英文和中文 README 的「支援的提供者」部分新增提供者名稱
  - 在其要點中保持清單按字母順序排序

- [ ] **8. 建立全面的測試**（`tests/providers/test_<provider>.py`）

  - 按照命名慣例建立測試檔案
  - 包括這些測試類別：
    - `Test<Provider>Imports` - 測試模組和函式匯入
    - `Test<Provider>APIKeyValidation` - 測試缺少 API 密鑰錯誤
    - `Test<Provider>ProviderMocked(BaseProviderTest)` - 從 `BaseProviderTest` 繼承以獲得 9 個標準測試
    - `Test<Provider>EdgeCases` - 測試 null 內容和其他邊緣情況
    - `Test<Provider>Integration` - 真實 API 呼叫測試（標記為 `@pytest.mark.integration`）
  - 在模擬測試類別中實作所需的屬性：
    - `provider_name` - 提供者名稱（小寫）
    - `provider_module` - 完整模組路徑
    - `api_function` - API 函式參考
    - `api_key_env_var` - API 密鑰的環境變數名稱（對於本機提供者為 None）
    - `model_name` - 用於測試的預設模型名稱
    - `success_response` - 模擬成功的 API 回應
    - `empty_content_response` - 模擬空內容回應

- [ ] **9. 升級版本**（`src/gac/__version__.py`）
  - 增加**次要**版本（例如，1.10.2 → 1.11.0）
  - 新增提供者是一個新功能，需要次要版本升級

### 範例實作

參見 MiniMax 提供者實作作為參考：

- 提供者：`src/gac/providers/minimax.py`
- 測試：`tests/providers/test_minimax.py`

### 關鍵點

1. **錯誤處理**：始終為不同的錯誤場景使用適當的 `AIError` 類型
2. **Null/空內容**：始終檢查回應中的 `None` 和空字串內容
3. **測試**：`BaseProviderTest` 類別提供每個提供者應該繼承的 9 個標準測試
4. **字母順序**：保持提供者清單按字母順序排序以便於維護
5. **API 密鑰命名**：使用格式 `<PROVIDER>_API_KEY`（全大寫，空格用底線）
6. **提供者名稱格式**：對多詞名稱使用帶連字號的小寫（例如，"lm-studio"）
7. **版本升級**：新增提供者需要**次要**版本升級（新功能）

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
