# GAC での ChatGPT OAuth の使用

**English** | [简体中文](../zh-CN/CHATGPT_OAUTH.md) | [繁體中文](../zh-TW/CHATGPT_OAUTH.md) | [日本語](../ja/CHATGPT_OAUTH.md) | [한국어](../ko/CHATGPT_OAUTH.md) | [हिन्दী](../hi/CHATGPT_OAUTH.md) | [Tiếng Việt](../vi/CHATGPT_OAUTH.md) | [Français](../fr/CHATGPT_OAUTH.md) | [Русский](../ru/CHATGPT_OAUTH.md) | [Español](../es/CHATGPT_OAUTH.md) | [Português](../pt/CHATGPT_OAUTH.md) | [Norsk](../no/CHATGPT_OAUTH.md) | [Svenska](../sv/CHATGPT_OAUTH.md) | [Deutsch](../de/CHATGPT_OAUTH.md) | [Nederlands](../nl/CHATGPT_OAUTH.md) | [Italiano](../it/CHATGPT_OAUTH.md)

GAC は ChatGPT OAuth による認証をサポートしており、OpenAI API キーを別途支払うことなく、ChatGPT サブスクリプションを使用して OpenAI の Codex API にアクセスできます。これは OpenAI の Codex CLI と同じ OAuth フローを使用します。

> ⚠️ **注意 — 非公式の使用：** これは OpenAI の Codex CLI と同じ OAuth フローを使用しますが、現在機能しているものの、OpenAI はサードパーティのトークン使用をいつでも制限する可能性があります。GAC は小規模なため、これまでのところ目立っていませんが、ここでの ChatGPT OAuth の使用はサードパーティツールに対して**公式に承認されておらず**、いつでも機能しなくなる可能性があります。信頼性の高いコミットメッセージ生成が必要な場合は、直接 API プロバイダー（`openai` など）を使用してください。現在のポリシーについては、[OpenAI の Codex ドキュメント](https://openai.com/codex) を参照してください。

## ChatGPT OAuth とは？

ChatGPT OAuth を使用すると、既存の ChatGPT Plus または Pro サブスクリプションを利用して、コミットメッセージを生成するために Codex API にアクセスできます。API キーとトークンごとの課金を管理する代わりに、ブラウザで 1 回認証するだけで、GAC がトークンのライフサイクルを自動的に処理します。

## 利点

- **コスト効果**：既存の ChatGPT Plus/Pro サブスクリプションを使用し、API アクセスを別途支払う必要がありません
- **同じモデル**：Codex 最適化モデル（`gpt-5.5`、`gpt-5.4`、`gpt-5.3-codex`）にアクセスできます
- **API キー管理不要**：ブラウザベースの OAuth により、API キーをローテーションまたは保存する必要がありません
- **個別課金**：ChatGPT OAuth の使用は、直接 OpenAI API 課金とは別です

## セットアップ

GAC には ChatGPT 用の組み込み OAuth 認証が含まれています。セットアッププロセスは完全に自動化されており、ブラウザを開いて認証を行います。

### オプション 1：初期セットアップ中（推奨）

`gac init` を実行するときは、プロバイダーとして「ChatGPT OAuth」を選択するだけです：

```bash
gac init
```

ウィザードは次のことを行います：

1. プロバイダーリストから「ChatGPT OAuth」を選択するように求めます
2. ブラウザを自動的に開いて OAuth 認証を行います
3. アクセストークンを `~/.gac/oauth/chatgpt-oauth.json` に保存します
4. デフォルトモデルを設定します

### オプション 2：後で ChatGPT OAuth に切り替える

すでに GAC を別のプロバイダーで構成していて、ChatGPT OAuth に切り替えたい場合：

```bash
gac model
```

次に：

1. プロバイダーリストから「ChatGPT OAuth」を選択します
2. ブラウザが自動的に開いて OAuth 認証を行います
3. トークンは `~/.gac/oauth/chatgpt-oauth.json` に保存されます
4. モデルは自動的に構成されます

### GAC を通常通り使用する

認証後、通常どおり GAC を使用します：

```bash
# 変更をステージする
git add .

# ChatGPT OAuth で生成してコミットする
gac

# または、単一のコミットのためにモデルを上書きする
gac -m chatgpt-oauth:gpt-5.5
```

## 利用可能なモデル

ChatGPT OAuth は Codex 最適化モデルへのアクセスを提供します。現在のモデルには次のものがあります：

- `gpt-5.5` — 最新で最も強力な Codex モデル
- `gpt-5.4` — 前世代の Codex モデル
- `gpt-5.3-codex` — 第 3 世代の Codex モデル

利用可能なモデルの完全なリストについては、[OpenAI ドキュメント](https://platform.openai.com/docs/models) を確認してください。

## CLI コマンド

GAC は ChatGPT OAuth 管理用の専用 CLI コマンドを提供します：

### ログイン

ChatGPT OAuth で認証または再認証します：

```bash
gac auth chatgpt login
```

ブラウザが自動的に開き、OAuth フローが完了します。すでに認証されている場合、これはトークンを更新します。

### ログアウト

保存された ChatGPT OAuth トークンを削除します：

```bash
gac auth chatgpt logout
```

これにより、`~/.gac/oauth/chatgpt-oauth.json` に保存されたトークンファイルが削除されます。

### ステータス

現在の ChatGPT OAuth 認証ステータスを確認します：

```bash
gac auth chatgpt status
```

または、すべてのプロバイダーを一度に確認します：

```bash
gac auth
```

## トラブルシューティング

### トークンの有効期限切れ

認証エラーが表示された場合、トークンの有効期限が切れている可能性があります。次のコマンドを実行して再認証します：

```bash
gac auth chatgpt login
```

ブラウザが自動的に開き、新しい OAuth 認証が行われます。GAC は、可能な場合はリフレッシュトークンを使用して、再認証なしでアクセスを更新します。

### 認証ステータスの確認

現在認証されているかどうかを確認するには：

```bash
gac auth chatgpt status
```

または、すべてのプロバイダーを一度に確認します：

```bash
gac auth
```

### ログアウト

保存されたトークンを削除するには：

```bash
gac auth chatgpt logout
```

### 「ChatGPT OAuth トークンが見つかりません」

これは、GAC がアクセストークンを見つけられないことを意味します。次のコマンドを実行して認証します：

```bash
gac model
```

次に、プロバイダーリストから「ChatGPT OAuth」を選択します。OAuth フローが自動的に開始されます。

### 「認証に失敗しました」

OAuth 認証が失敗した場合：

1. 有効な ChatGPT Plus または Pro サブスクリプションがあることを確認してください
2. ブラウザが正しく開くことを確認してください
3. 問題が解決しない場合は、別のブラウザを試してください
4. `auth.openai.com` へのネットワーク接続を確認してください
5. ローカルコールバックサーバーにポート 1455-1465 が利用可能であることを確認してください

### ポートが既に使用されている

OAuth コールバックサーバーは、ポート 1455-1465 を自動的に試行します。すべてのポートが占有されている場合：

```bash
# macOS/Linux の場合：
lsof -ti:1455-1465 | xargs kill -9

# Windows (PowerShell) の場合：
Get-NetTCPConnection -LocalPort 1455,1456,1457,1458,1459,1460,1461,1462,1463,1464,1465 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

次に、`gac auth chatgpt login` を再実行します。

## OpenAI プロバイダーとの違い

| 機能         | OpenAI (`openai:`)          | ChatGPT OAuth (`chatgpt-oauth:`)                     |
| ------------ | --------------------------- | ---------------------------------------------------- |
| 認証         | API キー (`OPENAI_API_KEY`) | OAuth（自動化されたブラウザフロー）                  |
| 課金         | トークンごとの API 課金     | サブスクリプションベース（ChatGPT Plus/Pro）         |
| セットアップ | 手動 API キー入力           | `gac init` または `gac model` による自動 OAuth       |
| トークン管理 | 長寿命の API キー           | OAuth トークン（リフレッシュトークンによる自動更新） |
| モデル       | すべての OpenAI モデル      | Codex 最適化モデル                                   |

## セキュリティに関する注意事項

- **アクセストークンをバージョン管理にコミットしないでください**
- GAC は OAuth トークンを `~/.gac/oauth/chatgpt-oauth.json` に保存します（プロジェクトディレクトリの外）
- OAuth フローは、セキュリティ強化のために PKCE（Proof Key for Code Exchange）を使用します
- ローカルコールバックサーバーは localhost でのみ実行されます（ポート 1455-1465）
- リフレッシュトークンを使用して、再認証なしでアクセスを自動的に更新します

## 関連項目

- [メインドキュメント](USAGE.md)
- [トラブルシューティングガイド](TROUBLESHOOTING.md)
- [OpenAI の Codex ドキュメント](https://openai.com/codex)
