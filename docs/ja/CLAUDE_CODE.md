# GAC で Claude Code を使用する

[English](../en/CLAUDE_CODE.md) | [简体中文](../zh-CN/CLAUDE_CODE.md) | [繁體中文](../zh-TW/CLAUDE_CODE.md) | **日本語** | [한국어](../ko/CLAUDE_CODE.md) | [हिन्दी](../hi/CLAUDE_CODE.md) | [Tiếng Việt](../vi/CLAUDE_CODE.md) | [Français](../fr/CLAUDE_CODE.md) | [Русский](../ru/CLAUDE_CODE.md) | [Español](../es/CLAUDE_CODE.md) | [Português](../pt/CLAUDE_CODE.md) | [Norsk](../no/CLAUDE_CODE.md) | [Svenska](../sv/CLAUDE_CODE.md) | [Deutsch](../de/CLAUDE_CODE.md) | [Nederlands](../nl/CLAUDE_CODE.md) | [Italiano](../it/CLAUDE_CODE.md)

GAC は Claude Code サブスクリプションによる認証をサポートしており、高価な Anthropic API を支払う代わりに Claude Code サブスクリプションを使用できます。これは、すでにサブスクリプションで Claude Code へのアクセス権を持っているユーザーに最適です。

## Claude Code とは？

Claude Code は Anthropic のサブスクリプションサービスで、OAuth ベースの Claude モデルアクセスを提供します。API キー（トークンごとに課金）を使用する代わりに、Claude Code はサブスクリプションの OAuth トークンを使用します。

## 利点

- **コスト効率**: 既存の Claude Code サブスクリプションを使用し、API アクセスを別途支払う必要がありません
- **同じモデル**: 同じ Claude モデル（例: `claude-sonnet-4-5`）にアクセスできます
- **独立課金**: Claude Code の使用は Anthropic API 課金から分離されています

## 設定

GAC には Claude Code 用の内蔵 OAuth 認証が含まれています。設定プロセスは完全自動化されており、認証のためにブラウザが開きます。

### オプション 1: 初期設定中（推奨）

`gac init` を実行する際、プロバイダーとして「Claude Code」を選択するだけです：

```bash
gac init
```

ウィザードは以下を行います：

1. プロバイダーリストから「Claude Code」を選択するよう求めます
2. OAuth 認証のためにブラウザを自動的に開きます
3. アクセストークンを `~/.gac.env` に保存します
4. デフォルトモデルを設定します

### オプション 2: 後で Claude Code に切り替える

他のプロバイダーで GAC を設定済みで、Claude Code に切り替えたい場合：

```bash
gac model
```

その後：

1. プロバイダーリストから「Claude Code」を選択します
2. OAuth 認証のためにブラウザが自動的に開きます
3. トークンが `~/.gac.env` に保存されます
4. モデルが自動的に設定されます

### GAC を通常通り使用

認証されると、いつも通り GAC を使用できます：

```bash
# 変更をステージング
git add .

# Claude Code で生成してコミット
gac

# または単一コミットのためにモデルを上書き
gac -m claude-code:claude-sonnet-4-5
```

## 利用可能なモデル

Claude Code は Anthropic API と同じモデルへのアクセスを提供します。現在の Claude 4.5 ファミリーモデルには以下が含まれます：

- `claude-sonnet-4-5` - 最新で最もインテリジェントな Sonnet モデル、コーディングに最適
- `claude-haiku-4-5` - 高速で効率的
- `claude-opus-4-1` - 複雑な推理で最も高性能なモデル

利用可能なモデルの完全なリストについては、[Claude ドキュメント](https://docs.claude.com/en/docs/about-claude/models/overview)を確認してください。

## トラブルシューティング

### トークンの有効期限切れ

認証エラーが表示される場合、トークンの有効期限が切れている可能性があります。以下を実行して再認証してください：

```bash
gac auth
```

ブラウザが自動的に開き、新しい OAuth 認証が行われます。または、`gac model` を実行し、「Claude Code」を選択してから「再認証（新しいトークンを取得）」を選択することもできます。

### 「CLAUDE_CODE_ACCESS_TOKEN が見つかりません」

これは GAC がアクセストークンを見つけられないことを意味します。以下を実行して認証してください：

```bash
gac model
```

その後プロバイダーリストから「Claude Code」を選択します。OAuth フローが自動的に開始されます。

### 「認証に失敗しました」

OAuth 認証が失敗した場合：

1. アクティブな Claude Code サブスクリプションがあることを確認してください
2. ブラウザが正しく開くことを確認してください
3. 問題が続く場合は別のブラウザを試してください
4. `claude.ai` へのネットワーク接続を確認してください
5. ポート 8765-8795 がローカルコールバックサーバーで利用可能であることを確認してください

## Anthropic プロバイダーとの違い

| 機能         | Anthropic (`anthropic:`)       | Claude Code (`claude-code:`)                               |
| ------------ | ------------------------------ | ---------------------------------------------------------- |
| 認証         | API キー (`ANTHROPIC_API_KEY`) | OAuth（自動ブラウザフロー）                                |
| 課金         | トークンごとの API 課金        | サブスクリプションベース                                   |
| 設定         | 手動 API キー入力              | `gac init` または `gac model` による自動 OAuth             |
| トークン管理 | 長期 API キー                  | OAuth トークン（期限切れの場合あり、`model` で簡単再認証） |
| モデル       | 同じモデル                     | 同じモデル                                                 |

## セキュリティに関する注意事項

- **アクセストークンをバージョン管理にコミットしないでください**
- GAC はトークンを `~/.gac.env`（プロジェクトディレクトリ外）に自動的に保存します
- トークンは期限切れになる可能性があり、`gac model` による再認証が必要です
- OAuth フローはセキュリティ強化のために PKCE（Proof Key for Code Exchange）を使用します
- ローカルコールバックサーバーはローカルホストのみで実行されます（ポート 8765-8795）

## 関連情報

- [メインドキュメント](USAGE.md)
- [トラブルシューティングガイド](TROUBLESHOOTING.md)
- [Claude Code ドキュメント](https://claude.ai/code)
