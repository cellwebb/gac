[English](../en/QWEN.md) | [简体中文](../zh-CN/QWEN.md) | [繁體中文](../zh-TW/QWEN.md) | **日本語** | [한국어](../ko/QWEN.md) | [हिन्दी](../hi/QWEN.md) | [Tiếng Việt](../vi/QWEN.md) | [Français](../fr/QWEN.md) | [Русский](../ru/QWEN.md) | [Español](../es/QWEN.md) | [Português](../pt/QWEN.md) | [Norsk](../no/QWEN.md) | [Svenska](../sv/QWEN.md) | [Deutsch](../de/QWEN.md) | [Nederlands](../nl/QWEN.md) | [Italiano](../it/QWEN.md)

# GACでQwen.aiを使用する

GACはQwen.ai OAuthによる認証をサポートしており、Qwen.aiアカウントを使用してコミットメッセージを生成できます。これはOAuthデバイスフロー認証を使用しており、シームレスなログイン体験を提供します。

## Qwen.aiとは？

Qwen.aiは、Qwenシリーズの大規模言語モデルへのアクセスを提供するAlibaba CloudのAIプラットフォームです。GACはOAuthベースの認証をサポートしているため、APIキーを手動で管理することなくQwen.aiアカウントを使用できます。

## メリット

- **簡単な認証**: OAuthデバイスフロー - ブラウザでログインするだけ
- **APIキー管理不要**: 認証は自動的に処理されます
- **Qwenモデルへのアクセス**: 強力なQwenモデルを使用してコミットメッセージを生成

## セットアップ

GACには、デバイスフローを使用したQwen.ai用の組み込みOAuth認証が含まれています。セットアッププロセスでは、コードが表示され、認証のためにブラウザが開きます。

### オプション1：初期セットアップ時（推奨）

`gac init`を実行する際、プロバイダーリストから「Qwen.ai (OAuth)」を選択するだけです：

```bash
gac init
```

ウィザードは以下の手順を実行します：

1. プロバイダーリストから「Qwen.ai (OAuth)」を選択するように求めます
2. デバイスコードを表示し、ブラウザを開きます
3. Qwen.aiで認証し、コードを入力します
4. アクセストークンを安全に保存します
5. デフォルトモデルを設定します

### オプション2：後でQwen.aiに切り替える

すでに別のプロバイダーでGACを設定しており、Qwen.aiに切り替えたい場合：

```bash
gac model
```

その後：

1. プロバイダーリストから「Qwen.ai (OAuth)」を選択します
2. デバイスコード認証フローに従います
3. トークンは`~/.gac/oauth/qwen.json`に安全に保存されます
4. モデルが自動的に設定されます

### オプション3：直接ログイン

次のコマンドを使用して直接認証することもできます：

```bash
gac auth qwen login
```

これにより：

1. デバイスコードが表示されます
2. ブラウザがQwen.ai認証ページを開きます
3. 認証後、トークンは自動的に保存されます

### GACを通常通り使用する

認証が完了したら、通常通りGACを使用します：

```bash
# 変更をステージング
git add .

# Qwen.aiで生成してコミット
gac

# または単一のコミットでモデルを上書き
gac -m qwen:qwen3-coder-plus
```

## 利用可能なモデル

Qwen.ai OAuth統合では以下を使用します：

- `qwen3-coder-plus` - コーディングタスク向けに最適化（デフォルト）

これはportal.qwen.ai OAuthエンドポイントを通じて利用可能なモデルです。他のQwenモデルについては、追加のQwenモデルオプションを提供するOpenRouterプロバイダーの使用を検討してください。

## 認証コマンド

GACは、Qwen.ai認証を管理するためのいくつかのコマンドを提供します：

```bash
# Qwen.aiにログイン
gac auth qwen login

# 認証ステータスを確認
gac auth qwen status

# ログアウトして保存されたトークンを削除
gac auth qwen logout

# すべてのOAuthプロバイダーのステータスを確認
gac auth
```

### ログインオプション

```bash
# 標準ログイン（ブラウザを自動的に開く）
gac auth qwen login

# ブラウザを開かずにログイン（手動でアクセスするURLを表示）
gac auth qwen login --no-browser

# 静音モード（最小限の出力）
gac auth qwen login --quiet
```

## トラブルシューティング

### トークンの期限切れ

認証エラーが表示される場合は、トークンの期限が切れている可能性があります。以下を実行して再認証してください：

```bash
gac auth qwen login
```

デバイスコードフローが開始され、再認証のためにブラウザが開きます。

### 認証ステータスの確認

現在認証されているかどうかを確認するには：

```bash
gac auth qwen status
```

または、すべてのプロバイダーを一度に確認します：

```bash
gac auth
```

### ログアウト

保存されたトークンを削除するには：

```bash
gac auth qwen logout
```

### "Qwen authentication not found"（Qwen認証が見つかりません）

これは、GACがアクセストークンを見つけられないことを意味します。以下を実行して認証してください：

```bash
gac auth qwen login
```

または、`gac model`を実行し、プロバイダーリストから「Qwen.ai (OAuth)」を選択します。

### "Authentication failed"（認証に失敗しました）

OAuth認証に失敗した場合：

1. Qwen.aiアカウントを持っていることを確認してください
2. ブラウザが正しく開くことを確認してください
3. デバイスコードを正しく入力したことを確認してください
4. 問題が解決しない場合は、別のブラウザを試してください
5. `qwen.ai`へのネットワーク接続を確認してください

### デバイスコードが機能しない

デバイスコード認証が機能しない場合：

1. コードの期限が切れていないことを確認してください（コードは期間限定で有効です）
2. `gac auth qwen login`を再度実行して新しいコードを取得してください
3. ブラウザを開くのに失敗した場合は、`--no-browser`フラグを使用してURLに手動でアクセスしてください

## セキュリティ上の注意

- **アクセストークンをバージョン管理にコミットしないでください**
- GACはトークンを`~/.gac/oauth/qwen.json`（プロジェクトディレクトリ外）に自動的に保存します
- トークンファイルには制限された権限があります（所有者のみ読み取り可能）
- トークンは期限切れになる可能性があり、再認証が必要になります
- OAuthデバイスフローは、ヘッドレスシステムでの安全な認証のために設計されています

## 関連項目

- [メインドキュメント](USAGE.md)
- [Claude Code セットアップ](CLAUDE_CODE.md)
- [トラブルシューティングガイド](TROUBLESHOOTING.md)
- [Qwen.ai ドキュメント](https://qwen.ai)
