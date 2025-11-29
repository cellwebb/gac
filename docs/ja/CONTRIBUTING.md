# gac への貢献

[English](../en/CONTRIBUTING.md) | [简体中文](../zh-CN/CONTRIBUTING.md) | [繁體中文](../zh-TW/CONTRIBUTING.md) | **日本語** | [한국어](../ko/CONTRIBUTING.md) | [हिन्दी](../hi/CONTRIBUTING.md) | [Tiếng Việt](../vi/CONTRIBUTING.md) | [Français](../fr/CONTRIBUTING.md) | [Русский](../ru/CONTRIBUTING.md) | [Español](../es/CONTRIBUTING.md) | [Português](../pt/CONTRIBUTING.md) | [Norsk](../no/CONTRIBUTING.md) | [Svenska](../sv/CONTRIBUTING.md) | [Deutsch](../de/CONTRIBUTING.md) | [Nederlands](../nl/CONTRIBUTING.md) | [Italiano](../it/CONTRIBUTING.md)

このプロジェクトへの貢献にご興味をお持ちいただきありがとうございます！あなたの協力を感謝します。すべての人にとってプロセスがスムーズになるよう、これらのガイドラインに従ってください。

## 目次

- [gac への貢献](#gac-への貢献)
  - [目次](#目次)
  - [開発環境のセットアップ](#開発環境のセットアップ)
    - [クイックセットアップ](#クイックセットアップ)
    - [別のセットアップ方法（ステップバイステップを希望する場合）](#別のセットアップ方法ステップバイステップを希望する場合)
    - [利用可能なコマンド](#利用可能なコマンド)
  - [バージョンアップ](#バージョンアップ)
    - [バージョンをアップする方法](#バージョンをアップする方法)
    - [リリースプロセス](#リリースプロセス)
    - [bump-my-version の使用（オプション）](#bump-my-version-の使用オプション)
  - [新しい AI プロバイダーの追加](#新しい-ai-プロバイダーの追加)
    - [新しいプロバイダー追加のチェックリスト](#新しいプロバイダー追加のチェックリスト)
    - [実装例](#実装例)
    - [重要な点](#重要な点)
  - [コーディング標準](#コーディング標準)
  - [Git フック（Lefthook）](#git-フックlefthook)
    - [セットアップ](#セットアップ)
    - [Git フックのスキップ](#git-フックのスキップ)
  - [テストガイドライン](#テストガイドライン)
    - [テストの実行](#テストの実行)
      - [プロバイダー統合テスト](#プロバイダー統合テスト)
  - [行動規範](#行動規範)
  - [ライセンス](#ライセンス)
  - [ヘルプの入手先](#ヘルプの入手先)

## 開発環境のセットアップ

このプロジェクトは依存関係管理に `uv` を使用し、一般的な開発タスクのために Makefile を提供します：

### クイックセットアップ

```bash
# Lefthookフックを含めすべてを設定するワンコマンド
make dev
```

このコマンドは以下を実行します：

- 開発依存関係をインストール
- git フックをインストール
- すべてのファイルで Lefthook フックを実行して既存の問題を修正

### 別のセットアップ方法（ステップバイステップを希望する場合）

```bash
# 仮想環境を作成して依存関係をインストール
make setup

# 開発依存関係をインストール
make dev

# Lefthookフックをインストール
brew install lefthook  # または以下のドキュメントで代替案を参照
lefthook install
lefthook run pre-commit --all
```

### 利用可能なコマンド

- `make setup` - 仮想環境を作成してすべての依存関係をインストール
- `make dev` - **完全な開発セットアップ** - Lefthook フックを含む
- `make test` - 標準テストを実行（統合テストを除く）
- `make test-integration` - 統合テストのみを実行（API キーが必要）
- `make test-all` - すべてのテストを実行
- `make test-cov` - カバレッジレポート付きでテストを実行
- `make lint` - コード品質をチェック（ruff, prettier, markdownlint）
- `make format` - コードフォーマットの問題を自動修正

## バージョンアップ

**重要**: PR にはリリースされるべき変更が含まれる場合、`src/gac/__version__.py` のバージョンアップを含める必要があります。

### バージョンをアップする方法

1. `src/gac/__version__.py` を編集してバージョン番号を増やす
2. [セマンティックバージョニング](https://semver.org/)に従う：
   - **パッチ** (1.6.X): バグ修正、小さな改善
   - **マイナー** (1.X.0): 新機能、後方互換性のある変更（例: 新しいプロバイダーの追加）
   - **メジャー** (X.0.0): 後方互換性のない変更

### リリースプロセス

リリースはバージョンタグのプッシュによってトリガーされます：

1. バージョンアップを含む PR を main にマージ
2. タグを作成: `git tag v1.6.1`
3. タグをプッシュ: `git push origin v1.6.1`
4. GitHub Actions が自動的に PyPI に公開

例:

```python
# src/gac/__version__.py
__version__ = "1.6.1"  # 1.6.0からアップ
```

### bump-my-version の使用（オプション）

`bump-my-version` がインストールされている場合、ローカルで使用できます：

```bash
# バグ修正の場合:
bump-my-version bump patch

# 新機能の場合:
bump-my-version bump minor

# 破壊的変更の場合:
bump-my-version bump major
```

## 新しい AI プロバイダーの追加

新しい AI プロバイダーを追加する際、コードベース全体で複数のファイルを更新する必要があります。この包括的なチェックリストに従ってください：

### 新しいプロバイダー追加のチェックリスト

- [ ] **1. プロバイダー実装を作成** (`src/gac/providers/<provider_name>.py`)

  - プロバイダー名（例: `minimax.py`）で新しいファイルを作成
  - `call_<provider>_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str` を実装
  - プロバイダーがサポートしている場合は OpenAI 互換形式を使用
  - 環境変数 `<PROVIDER>_API_KEY` から API キーを処理
  - 適切な `AIError` タイプでエラーハンドリングを含める：
    - `AIError.authentication_error()` 認証問題用
    - `AIError.rate_limit_error()` レート制限用（HTTP 429）
    - `AIError.timeout_error()` タイムアウト用
    - `AIError.model_error()` モデルエラーと空/null コンテンツ用
  - API エンドポイント URL を設定
  - HTTP リクエストに 120 秒のタイムアウトを使用

- [ ] **2. パッケージにプロバイダーを登録** (`src/gac/providers/__init__.py`)

  - インポートを追加: `from .<provider> import call_<provider>_api`
  - `PROVIDER_REGISTRY` 辞書に追加: `"provider-name": call_<provider>_api`
  - `__all__` リストに追加: `"call_<provider>_api"`

- [ ] **3. 例設定を更新** (`.gac.env.example`)

  - 例モデル設定を形式で追加: `# GAC_MODEL=provider:model-name`
  - API キーエントリを追加: `# <PROVIDER>_API_KEY=your_key_here`
  - エントリをアルファベット順に保つ
  - 該用する場合はオプションキーのコメントを追加

- [ ] **4. ドキュメントを更新** (`README.md` と `docs/` 内のすべての `README.md` 翻訳)

  - すべての README 翻訳の「Supported Providers」セクションにプロバイダー名を追加
  - 箇条書き内でアルファベット順を保つ

- [ ] **5. 対話型セットアップに追加** (`src/gac/init_cli.py`)

  - `providers` リストにタプルを追加: `("Provider Name", "default-model-name")`
  - リストをアルファベット順に保つ
  - **重要**: プロバイダーが標準的でない API キー名（自動生成される `{PROVIDER_UPPERCASE}_API_KEY` ではない）を使用する場合、特別な処理を追加する：

    ```python
    elif provider_key == "your-provider-key":
        api_key_name = "YOUR_CUSTOM_API_KEY_NAME"
    ```

    例: `kimi-for-coding` は `KIMI_CODING_API_KEY` を使用し、`moonshot-ai` は `MOONSHOT_API_KEY` を使用

- [ ] **6. 包括的なテストを作成** (`tests/providers/test_<provider>.py`)

  - 命名規則に従ってテストファイルを作成
  - これらのテストクラスを含める：
    - `Test<Provider>Imports` - モジュールと関数のインポートをテスト
    - `Test<Provider>APIKeyValidation` - API キーなしエラーをテスト
    - `Test<Provider>ProviderMocked(BaseProviderTest)` - 9 つの標準テスト用に BaseProviderTest を継承
    - `Test<Provider>EdgeCases` - null コンテンツとその他のエッジケースをテスト
    - `Test<Provider>Integration` - リアル API コールテスト（`@pytest.mark.integration`でマーク）
  - モックテストクラスで必要なプロパティを実装：
    - `provider_name` - プロバイダー名（小文字）
    - `provider_module` - 完全なモジュールパス
    - `api_function` - API 関数参照
    - `api_key_env_var` - API キーの環境変数名（ローカルプロバイダーの場合は None）
    - `model_name` - テスト用のデフォルトモデル名
    - `success_response` - モック成功 API レスポンス
    - `empty_content_response` - モック空コンテンツレスポンス

- [ ] **7. バージョンをアップ** (`src/gac/__version__.py`)
  - **マイナー**バージョンを増やす（例: 1.10.2 → 1.11.0）
  - プロバイダーの追加は新機能であり、マイナーバージョンアップが必要

### 実装例

MiniMax プロバイダー実装を参考として見てください：

- プロバイダー: `src/gac/providers/minimax.py`
- テスト: `tests/providers/test_minimax.py`

### 重要な点

1. **エラーハンドリング**: 常に異なるエラーシナリオに適切な `AIError` タイプを使用
2. **null/空コンテンツ**: レスポンスで `None` と空文字列の両方を常にチェック
3. **テスト**: `BaseProviderTest` クラスはすべてのプロバイダーが継承すべき 9 つの標準テストを提供
4. **アルファベット順**: メンテナンスのためにプロバイダーリストをアルファベット順に保つ
5. **API キーの命名**: `<PROVIDER>_API_KEY` 形式を使用（すべて大文字、スペースはアンダースコア）
6. **プロバイダー登録**: `src/gac/providers/__init__.py` と `src/gac/init_cli.py` のみを変更し、`ai.py` と `ai_utils.py` はレジストリから自動的に読み込む
7. **プロバイダー名形式**: 複数単語の場合は小文字とハイフンを使用（例: "lm-studio"）
8. **バージョンアップ**: プロバイダーの追加には**マイナー**バージョンアップが必要（新機能）

## コーディング標準

- ターゲット Python 3.10+（3.10, 3.11, 3.12, 3.13, 3.14）
- すべての関数パラメータと戻り値に型ヒントを使用
- コードをクリーン、コンパクト、読みやすく保つ
- 不必要な複雑さを避ける
- print 文の代わりに logging を使用
- フォーマットは `ruff` で処理（linting、フォーマット、インポートソートを一つのツールで；最大行長: 120）
- `pytest` で最小限で効果的なテストを記述

## Git フック（Lefthook）

このプロジェクトは [Lefthook](https://github.com/evilmartians/lefthook) を使用してコード品質チェックを高速で一貫性のあるものに保ちます。設定されたフックは以前の pre-commit セットアップをミラーリングします：

- `ruff` - Python linting とフォーマット（black、isort、flake8 を置換）
- `markdownlint-cli2` - Markdown linting
- `prettier` - ファイルフォーマット（markdown、yaml、json）
- `check-upstream` - 上流変更をチェックするカスタムフック

### セットアップ

**推奨アプローチ:**

```bash
make dev
```

**手動セットアップ（ステップバイステップを希望する場合）:**

1. Lefthook をインストール（セットアップに合わせてオプションを選択）：

   ```sh
   brew install lefthook          # macOS (Homebrew)
   # または
   cargo install lefthook         # Rust toolchain
   # または
   asdf plugin add lefthook && asdf install lefthook latest
   ```

2. git フックをインストール：

   ```sh
   lefthook install
   ```

3. (オプション) すべてのファイルで実行：

   ```sh
   lefthook run pre-commit --all
   ```

フックは各コミットで自動的に実行されるようになります。チェックが失敗した場合、コミットする前に問題を修正する必要があります。

### Git フックのスキップ

Lefthook チェックを一時的にスキップする必要がある場合、`--no-verify` フラグを使用します：

```sh
git commit --no-verify -m "Your commit message"
```

注意: これは重要なコード品質チェックをバイパスするため、絶対に必要な場合にのみ使用してください。

## テストガイドライン

このプロジェクトは pytest をテストに使用します。新しい機能を追加したりバグを修正したりする際、変更をカバーするテストを含めてください。

`scripts/` ディレクトリには、pytest で簡単にテストできない機能のテストスクリプトが含まれていることに注意してください。複雑なシナリオや標準の pytest フレームワークでは実装が困難な統合テストのために、ここにスクリプトを自由に追加してください。

### テストの実行

```sh
# 標準テストを実行（リアルAPIコールを含む統合テストを除く）
make test

# プロバイダー統合テストのみを実行（APIキーが必要）
make test-integration

# プロバイダー統合テストを含むすべてのテストを実行
make test-all

# カバレッジ付きでテストを実行
make test-cov

# 特定のテストファイルを実行
uv run -- pytest tests/test_prompt.py

# 特定のテストを実行
uv run -- pytest tests/test_prompt.py::TestExtractRepositoryContext::test_extract_repository_context_with_docstring
```

#### プロバイダー統合テスト

プロバイダー統合テストは、プロバイダー実装が実際の API で正しく動作することを確認するためにリアル API コールを行います。これらのテストは `@pytest.mark.integration` でマークされ、デフォルトでスキップされます：

- 定期的な開発中の API クレジット消費を避けるため
- API キーが設定されていない場合のテスト失敗を防ぐため
- 高速な反復開発のためにテスト実行を高速に保つため

プロバイダー統合テストを実行するには：

1. **テストするプロバイダーの API キーを設定**:

   ```sh
   export ANTHROPIC_API_KEY="your-key"
   export CEREBRAS_API_KEY="your-key"
   export GEMINI_API_KEY="your-key"
   export GROQ_API_KEY="your-key"
   export OPENAI_API_KEY="your-key"
   export OPENROUTER_API_KEY="your-key"
   export STREAMLAKE_API_KEY="your-key"
   export ZAI_API_KEY="your-key"
   # LM StudioとOllamaはローカルインスタンスの実行が必要
   # LM StudioとOllamaのAPIキーは、デプロイで認証を要求する場合を除きオプション
   ```

2. **プロバイダーテストを実行**:

   ```sh
   make test-integration
   ```

API キーが設定されていないプロバイダーのテストはスキップされます。これらのテストは API 変更を早期に検出し、プロバイダー API との互換性を確保するのに役立ちます。

## 行動規範

尊重的で建設的であること。ハラスメントや虐待的な行動は容認されません。

## ライセンス

貢献することで、あなたの貢献がプロジェクトと同じライセンスの下でライセンスされることに同意するものとします。

---

## ヘルプの入手先

- トラブルシューティングについては [../TROUBLESHOOTING.md](../TROUBLESHOOTING.md) を参照
- 使用法と CLI オプションについては [../USAGE.md](../USAGE.md) を参照
- ライセンス詳細については [../LICENSE](../LICENSE) を参照

gac の改善にご協力いただきありがとうございます！
