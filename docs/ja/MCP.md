# GAC を MCP サーバーとして使用する

[English](../en/MCP.md) | [简体中文](../zh-CN/MCP.md) | [繁體中文](../zh-TW/MCP.md) | **日本語** | [한국어](../ko/MCP.md) | [हिन्दी](../hi/MCP.md) | [Tiếng Việt](../vi/MCP.md) | [Français](../fr/MCP.md) | [Русский](../ru/MCP.md) | [Español](../es/MCP.md) | [Português](../pt/MCP.md) | [Norsk](../no/MCP.md) | [Svenska](../sv/MCP.md) | [Deutsch](../de/MCP.md) | [Nederlands](../nl/MCP.md) | [Italiano](../it/MCP.md)

GAC は [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) サーバーとして実行でき、AI エージェントやエディターがシェルコマンドの代わりに構造化されたツール呼び出しを通じてコミットを生成できるようにします。

## 目次

- [GAC を MCP サーバーとして使用する](#gac-を-mcp-サーバーとして使用する)
  - [目次](#目次)
  - [MCP とは？](#mcp-とは)
  - [メリット](#メリット)
  - [セットアップ](#セットアップ)
    - [Claude Code](#claude-code)
    - [Cursor](#cursor)
    - [その他の MCP クライアント](#その他の-mcp-クライアント)
  - [利用可能なツール](#利用可能なツール)
    - [gac_status](#gac_status)
    - [gac_commit](#gac_commit)
  - [ワークフロー](#ワークフロー)
    - [基本的なコミット](#基本的なコミット)
    - [コミット前のプレビュー](#コミット前のプレビュー)
    - [グループ化されたコミット](#グループ化されたコミット)
    - [コンテキスト付きコミット](#コンテキスト付きコミット)
  - [設定](#設定)
  - [トラブルシューティング](#トラブルシューティング)
  - [関連項目](#関連項目)

## MCP とは？

Model Context Protocol は、AI アプリケーションが構造化されたインターフェースを通じて外部ツールを呼び出すことを可能にするオープンスタンダードです。GAC を MCP サーバーとして実行することで、MCP 互換のクライアントはシェルコマンドを直接実行することなく、リポジトリの状態を検査し、AI 駆動のコミットを作成できます。

## メリット

- **構造化された対話**: エージェントはシェル出力を解析する代わりに、検証済みパラメータを持つ型付きツールを呼び出します
- **2 ツールワークフロー**: `gac_status` で検査、`gac_commit` で実行 -- エージェント推論に自然にフィット
- **完全な GAC 機能**: AI コミットメッセージ、グループ化されたコミット、シークレットスキャン、プッシュ -- すべて MCP 経由で利用可能
- **ゼロ設定**: サーバーは既存の GAC 設定を使用します（`~/.gac.env`、プロバイダー設定など）

## セットアップ

MCP サーバーは `gac serve` で起動し、stdio（標準 MCP トランスポート）で通信します。

### Claude Code

プロジェクトの `.mcp.json` またはグローバルの `~/.claude/claude_code_config.json` に追加：

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

または GAC がグローバルにインストールされている場合：

```json
{
  "mcpServers": {
    "gac": {
      "command": "gac",
      "args": ["serve"]
    }
  }
}
```

### Cursor

Cursor の MCP 設定（`.cursor/mcp.json`）に追加：

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

### その他の MCP クライアント

MCP 互換のクライアントであれば GAC を使用できます。サーバーのエントリポイントは以下の通りです：

```text
command: uvx
args: ["gac", "serve"]
transport: stdio
```

GAC がインストール済みの場合（`uv tool install gac` 経由）、`uvx gac` の代わりに直接 `gac` を使用できます。

## 利用可能なツール

サーバーは 2 つのツールを公開しています：

### gac_status

リポジトリの状態を検査します。コミット前にこれを使用して、何がコミットされるかを把握します。

**パラメータ：**

| パラメータ          | 型                                      | デフォルト  | 説明                                |
| ------------------- | --------------------------------------- | ----------- | ----------------------------------- |
| `format`            | `"summary"` \| `"detailed"` \| `"json"` | `"summary"` | 出力形式                            |
| `include_diff`      | bool                                    | `false`     | 完全な diff 内容を含める            |
| `include_stats`     | bool                                    | `true`      | 行変更の統計情報を含める            |
| `include_history`   | int                                     | `0`         | 含める最近のコミット数              |
| `staged_only`       | bool                                    | `false`     | ステージされた変更のみを表示        |
| `include_untracked` | bool                                    | `true`      | 未追跡ファイルを含める              |
| `max_diff_lines`    | int                                     | `500`       | diff 出力サイズの上限（0 = 無制限） |

**返却値：** ブランチ名、ファイル状態（ステージ済み/未ステージ/未追跡/コンフリクト）、オプションの diff 内容、オプションの統計情報、オプションのコミット履歴。

### gac_commit

AI 駆動のコミットメッセージを生成し、オプションでコミットを実行します。

**パラメータ：**

| パラメータ         | 型             | デフォルト | 説明                                                 |
| ------------------ | -------------- | ---------- | ---------------------------------------------------- |
| `stage_all`        | bool           | `false`    | コミット前にすべての変更をステージ（`git add -A`）   |
| `files`            | list[str]      | `[]`       | ステージする特定のファイル                           |
| `dry_run`          | bool           | `false`    | 実行せずにプレビュー                                 |
| `message_only`     | bool           | `false`    | コミットせずにメッセージのみ生成                     |
| `push`             | bool           | `false`    | コミット後にリモートにプッシュ                       |
| `group`            | bool           | `false`    | 変更を複数の論理的なコミットに分割                   |
| `one_liner`        | bool           | `false`    | 単一行のコミットメッセージ                           |
| `scope`            | string \| null | `null`     | Conventional commit のスコープ（未指定時は自動検出） |
| `hint`             | string         | `""`       | より良いメッセージのための追加コンテキスト           |
| `model`            | string \| null | `null`     | AI モデルを上書き（`provider:model_name`）           |
| `language`         | string \| null | `null`     | コミットメッセージの言語を上書き                     |
| `skip_secret_scan` | bool           | `false`    | セキュリティスキャンをスキップ                       |
| `no_verify`        | bool           | `false`    | pre-commit フックをスキップ                          |
| `auto_confirm`     | bool           | `false`    | 確認プロンプトをスキップ（エージェントに必須）       |

**返却値：** 成功ステータス、生成されたコミットメッセージ、コミットハッシュ（コミットした場合）、変更されたファイルのリスト、および警告。

## ワークフロー

### 基本的なコミット

```text
1. gac_status()                              → 変更内容を確認
2. gac_commit(stage_all=true, auto_confirm=true)  → ステージ、メッセージ生成、コミット
```

### コミット前のプレビュー

```text
1. gac_status(include_diff=true, include_stats=true)  → 変更を詳細にレビュー
2. gac_commit(stage_all=true, dry_run=true)            → コミットメッセージをプレビュー
3. gac_commit(stage_all=true, auto_confirm=true)       → コミットを実行
```

### グループ化されたコミット

```text
1. gac_status()                                           → すべての変更を確認
2. gac_commit(stage_all=true, group=true, dry_run=true)   → 論理的なグループ分けをプレビュー
3. gac_commit(stage_all=true, group=true, auto_confirm=true)  → グループ化されたコミットを実行
```

### コンテキスト付きコミット

```text
1. gac_status(include_history=5)  → スタイル参考のために最近のコミットを確認
2. gac_commit(
     stage_all=true,
     hint="Fixes login timeout bug from issue #42",
     scope="auth",
     auto_confirm=true
   )
```

## 設定

MCP サーバーは既存の GAC 設定を使用します。以下の設定以外に追加のセットアップは不要です：

1. **プロバイダーとモデル**: `gac init` または `gac model` を実行して AI プロバイダーを設定
2. **API キー**: `~/.gac.env` に保存（`gac init` 時に設定）
3. **オプション設定**: すべての GAC 環境変数が適用されます（`GAC_LANGUAGE`、`GAC_VERBOSE` など）

すべての設定オプションについては[メインドキュメント](USAGE.md#設定に関する注意)を参照してください。

## トラブルシューティング

### "No model configured"

MCP サーバーを使用する前に、`gac init` を実行して AI プロバイダーとモデルを設定してください。

### "No staged changes found"

ファイルを手動でステージ（`git add`）するか、`gac_commit` 呼び出しで `stage_all=true` を使用してください。

### サーバーが起動しない

GAC がインストールされていてアクセス可能であることを確認してください：

```bash
uvx gac --version
# or
gac --version
```

`uvx` を使用している場合は、`uv` がインストールされて PATH に含まれていることを確認してください。

### エージェントがサーバーを見つけられない

MCP 設定ファイルがクライアントの正しい場所にあり、`command` パスがシェル環境からアクセス可能であることを確認してください。

### Rich 出力の破損

MCP サーバーは stdio プロトコルの破損を防ぐために、すべての Rich コンソール出力を自動的に stderr にリダイレクトします。文字化けした出力が表示される場合は、MCP 使用時に `gac serve`（`gac` を直接ではなく）を実行していることを確認してください。

## 関連項目

- [メインドキュメント](USAGE.md)
- [Claude Code OAuth セットアップ](CLAUDE_CODE.md)
- [トラブルシューティングガイド](TROUBLESHOOTING.md)
- [MCP 仕様](https://modelcontextprotocol.io/)
