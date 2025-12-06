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
