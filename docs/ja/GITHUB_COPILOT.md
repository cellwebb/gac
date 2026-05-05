# GAC で GitHub Copilot を使用する

[English](../en/GITHUB_COPILOT.md) | [简体中文](../zh-CN/GITHUB_COPILOT.md) | [繁體中文](../zh-TW/GITHUB_COPILOT.md) | **日本語** | [한국어](../ko/GITHUB_COPILOT.md) | [हिन्दी](../hi/GITHUB_COPILOT.md) | [Tiếng Việt](../vi/GITHUB_COPILOT.md) | [Français](../fr/GITHUB_COPILOT.md) | [Русский](../ru/GITHUB_COPILOT.md) | [Español](../es/GITHUB_COPILOT.md) | [Português](../pt/GITHUB_COPILOT.md) | [Norsk](../no/GITHUB_COPILOT.md) | [Svenska](../sv/GITHUB_COPILOT.md) | [Deutsch](../de/GITHUB_COPILOT.md) | [Nederlands](../nl/GITHUB_COPILOT.md) | [Italiano](../it/GITHUB_COPILOT.md)

GAC は GitHub Copilot による認証をサポートしており、Copilot サブスクリプションを使用して OpenAI、Anthropic、Google などのモデルにアクセスできます — すべて GitHub Copilot プランに含まれています。

## GitHub Copilot OAuth とは？

GitHub Copilot OAuth は **Device Flow** を使用します — ローカルコールバックサーバーを必要としない、安全なブラウザベースの認証方法です。URL にアクセスしてワンタイムコードを入力し、GAC が Copilot アクセスを使用することを承認します。背後で、GAC は長寿命の GitHub OAuth トークンを、Copilot API へのアクセスを許可する短寿命の Copilot セッショントークン（約30分）と交換します。

これにより、単一のサブスクリプションで複数のプロバイダーのモデルにアクセスできます：

- **OpenAI** — `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`
- **Anthropic** — `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5`
- **Google** — `gemini-2.5-pro`, `gemini-2.5-flash`

## 利点

- **マルチプロバイダーアクセス**：単一のサブスクリプションで OpenAI、Anthropic、Google のモデルを使用
- **コスト効果**：別の API キーの支払いの代わりに既存の Copilot サブスクリプションを使用
- **API キー管理不要**：Device Flow 認証 — 回転や保存するキーなし
- **GitHub Enterprise 対応**：`--host` フラグで GHE インスタンスに対応

## セットアップ

### オプション 1：初期セットアップ中（推奨）

`gac init` を実行するときは、プロバイダーとして「Copilot」を選択するだけです：

```bash
gac init
```

ウィザードは次のことを行います：

1. プロバイダーリストから「Copilot」を選択するように求めます
2. ワンタイムコードを表示し、Device Flow 認証のためにブラウザを開きます
3. OAuth トークンを `~/.gac/oauth/copilot.json` に保存します
4. デフォルトモデルを設定します

### オプション 2：後で Copilot に切り替える

すでに GAC を別のプロバイダーで構成している場合：

```bash
gac model
```

プロバイダーリストから「Copilot」を選択して認証します。

### オプション 3：直接ログイン

デフォルトモデルを変更せずに直接認証します：

```bash
gac auth copilot login
```

### GAC を通常通り使用する

認証後、通常どおり GAC を使用します：

```bash
# 変更をステージする
git add .

# Copilot で生成してコミットする
gac

# または、単一のコミットのためにモデルを上書きする
gac -m copilot:gpt-4.1
gac -m copilot:claude-sonnet-4.5
gac -m copilot:gemini-2.5-pro
```

## 利用可能なモデル

Copilot は複数のプロバイダーのモデルへのアクセスを提供します。現在のモデルには次のものがあります：

| プロバイダー | モデル                                                                                         |
| ------------ | ---------------------------------------------------------------------------------------------- |
| OpenAI       | `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`                                           |
| Anthropic    | `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5` |
| Google       | `gemini-2.5-pro`, `gemini-2.5-flash`                                                           |

> **注意：** ログイン後に表示されるモデルリストは参考情報であり、GitHub が新しいモデルを追加するにつれて古くなる可能性があります。最新の利用可能なモデルについては、[GitHub Copilot ドキュメント](https://docs.github.com/en/copilot) を確認してください。

## GitHub Enterprise

GitHub Enterprise インスタンスで認証するには：

```bash
gac auth copilot login --host ghe.mycompany.com
```

GAC は GHE インスタンス用の正しい Device Flow と API エンドポイントを自動的に使用します。セッショントークンはホストごとにキャッシュされるため、異なる GHE インスタンスは個別に処理されます。

## CLI コマンド

GAC は Copilot 認証管理用の専用 CLI コマンドを提供します：

### ログイン

GitHub Copilot で認証または再認証します：

```bash
gac auth copilot login
```

Device Flow ページでワンタイムコードを入力するためにブラウザが開きます。すでに認証されている場合、再認証するかどうかを確認されます。

GitHub Enterprise の場合：

```bash
gac auth copilot login --host ghe.mycompany.com
```

### ログアウト

保存された Copilot トークンを削除します：

```bash
gac auth copilot logout
```

これにより、`~/.gac/oauth/copilot.json` に保存されたトークンファイルとセッションキャッシュが削除されます。

### ステータス

現在の Copilot 認証ステータスを確認します：

```bash
gac auth copilot status
```

または、すべてのプロバイダーを一度に確認します：

```bash
gac auth
```

## 仕組み

Copilot 認証フローは ChatGPT や Claude Code OAuth とは異なります：

1. **Device Flow** — GAC が GitHub にデバイスコードを要求し、それを表示します
2. **ブラウザ承認** — URL にアクセスしてコードを入力します
3. **トークンポーリング** — 承認が完了するまで GAC が GitHub をポーリングします
4. **セッショントークン交換** — GitHub OAuth トークンが短寿命の Copilot セッショントークンと交換されます
5. **自動リフレッシュ** — セッショントークン（約30分）はキャッシュされた OAuth トークンから自動的に更新されます

PKCE ベースの OAuth（ChatGPT/Claude Code）とは異なり、Device Flow はローカルコールバックサーバーやポート管理を必要としません。

## トラブルシューティング

### 「Copilot 認証が見つかりません」

認証するにはログインコマンドを実行します：

```bash
gac auth copilot login
```

### 「Copilot セッショントークンを取得できませんでした」

これは、GAC が GitHub OAuth トークンを取得したが、Copilot セッショントークンと交換できなかったことを意味します。通常、これは次の理由によります：

1. **Copilot サブスクリプションなし** — GitHub アカウントにアクティブな Copilot サブスクリプションがない
2. **トークン失効** — OAuth トークンが失効しました。`gac auth copilot login` で再認証してください

### セッショントークンの有効期限切れ

セッショントークンは約30分で有効期限が切れます。GAC はキャッシュされた OAuth トークンから自動的にリフレッシュするため、頻繁に再認証する必要はありません。自動リフレッシュが失敗する場合：

```bash
gac auth copilot login
```

### 「無効または安全でないホスト名」

`--host` フラグは SSRF 攻撃を防ぐためにホスト名を厳格に検証します。このエラーが表示された場合：

- ホスト名にポートを含めていないことを確認してください（例：`ghe.company.com:8080` ではなく `ghe.company.com` を使用）
- プロトコルやパスを含めないでください（例：`https://ghe.company.com/api` ではなく `ghe.company.com` を使用）
- プライベート IP アドレスと `localhost` はセキュリティ上の理由でブロックされています

### GitHub Enterprise の問題

GHE 認証が失敗する場合：

1. GHE インスタンスで Copilot が有効になっていることを確認してください
2. GHE ホスト名がマシンからアクセス可能であることを確認してください
3. GHE アカウントに Copilot ライセンスがあることを確認してください
4. `--host` フラグを明示的に試してください：`gac auth copilot login --host ghe.mycompany.com`

## 他の OAuth プロバイダーとの違い

| 機能                 | ChatGPT OAuth                | Claude Code                  | Copilot                                           |
| -------------------- | ---------------------------- | ---------------------------- | ------------------------------------------------- |
| 認証方法             | PKCE（ブラウザコールバック） | PKCE（ブラウザコールバック） | Device Flow（ワンタイムコード）                   |
| コールバックサーバー | ポート 1455-1465             | ポート 8765-8795             | 不要                                              |
| トークン有効期間     | 長寿命（自動リフレッシュ）   | 有効期限あり（再認証）       | セッション約30分（自動リフレッシュ）              |
| モデル               | Codex 最適化 OpenAI          | Claude ファミリー            | マルチプロバイダー（OpenAI + Anthropic + Google） |
| GHE 対応             | なし                         | なし                         | あり（`--host` フラグ）                           |

## セキュリティに関する注意事項

- **OAuth トークンをバージョン管理にコミットしないでください**
- GAC は OAuth トークンを `~/.gac/oauth/copilot.json` に保存します（プロジェクトディレクトリの外）
- セッショントークンは `0o600` 権限で `~/.gac/oauth/copilot_session.json` にキャッシュされます
- ホスト名は SSRF および URL インジェクション攻撃を防ぐために厳格に検証されます
- プライベート IP アドレス、ループバックアドレス、および `localhost` はホスト名としてブロックされています
- Device Flow はローカルポートを公開しないため、攻撃対象領域が削減されます

## 関連項目

- [メインドキュメント](USAGE.md)
- [トラブルシューティングガイド](TROUBLESHOOTING.md)
- [ChatGPT OAuth 設定ガイド](CHATGPT_OAUTH.md)
- [Claude Code 設定ガイド](CLAUDE_CODE.md)
- [GitHub Copilot ドキュメント](https://docs.github.com/en/copilot)
