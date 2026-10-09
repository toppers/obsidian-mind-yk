---
date: 2026-08-19
description: "QMD の CLAUDE.md 記載コマンド一覧の使い方（tobl版）— フュージョン戦略・スコア解釈は README.md 参照"
tags:
  - work-note
---
❯ このプロジェクトのコマンドの使い方を教えて

QMD コマンドの使い方

セットアップ

# グローバルインストール
npm install -g @tobilu/qmd
# または
bun install -g @tobilu/qmd

# インストールせず直接実行も可能
npx @tobilu/qmd ...
bunx @tobilu/qmd ...

1. コレクション管理（インデックス対象の登録）

まず検索したいディレクトリを「コレクション」として登録します。

# カレントディレクトリを登録
qmd collection add . --name myproject

# パスとglobパターンを指定して登録
qmd collection add ~/Documents/notes --name notes --mask '**/*.md'

# 一覧表示
qmd collection list

# 削除・リネーム
qmd collection remove myproject
qmd collection rename myproject my-project

# コレクション内のファイル一覧
qmd ls notes
qmd ls notes/subfolder

⚠️ qmd collection add はユーザーが手動実行するコマンドです。Claude Codeから自動実行しません。

2. コンテキスト追加（検索精度を上げる肝）

パスごとに説明文を紐づけると、検索結果と一緒にコンテキストが返り、LLMがより適切な文書を選べるようになります。

# カレントディレクトリに追加（コレクションは自動検出）
cd ~/notes && qmd context add "個人的なメモとアイデア"

# 特定パスに追加（qmd://仮想パス）
qmd context add qmd://notes "Personal notes and ideas"
qmd context add qmd://docs/api "API documentation"

# 全コレクション共通のグローバルコンテキスト
qmd context add / "常にこの文脈を考慮する"

# 一覧・不足チェック・削除
qmd context list
qmd context check
qmd context rm qmd://notes/old

3. インデックス作成・更新

qmd update            # ファイルシステムを再スキャンして再インデックス
qmd update --pull     # git pullしてから再インデックス（リモートリポジトリ用）
qmd embed             # ベクトル埋め込みを生成（初回はGGUFモデルを自動DL）
qmd embed -f          # 強制的に全件再埋め込み
qmd embed --chunk-strategy auto   # コードファイルをtree-sitterでAST分割
qmd status            # インデックス状態・コレクション一覧を表示

⚠️ qmd embed / qmd update も自動実行はしません。実行例だけ提示します。

4. 検索コマンド（3種類）

┌─────────────────────┬─────────────────────────────────────────────────────┬──────────────────────┐
│      コマンド       │                        内容                         │      速度/品質       │
├─────────────────────┼─────────────────────────────────────────────────────┼──────────────────────┤
│ qmd search "query"  │ BM25全文検索のみ                                    │ 速い・キーワード一致 │
├─────────────────────┼─────────────────────────────────────────────────────┼──────────────────────┤
│ qmd vsearch "query" │ ベクトル意味検索のみ                                │ 意味的類似度         │
├─────────────────────┼─────────────────────────────────────────────────────┼──────────────────────┤
│ qmd query "query"   │ ハイブリッド（クエリ拡張＋FTS＋ベクトル＋リランク） │ 最高品質・推奨       │
└─────────────────────┴─────────────────────────────────────────────────────┴──────────────────────┘

qmd search "authentication flow"
qmd vsearch "how to login"
qmd query "user authentication"

# 特定コレクションに絞る
qmd search "API" -c notes

# 件数・スコア閾値
qmd query -n 10 --min-score 0.3 "API design patterns"

# 全件出力（エージェント向け）
qmd search "API" --all --files --min-score 0.3

# スコアリングの内訳を見る
qmd query --json --explain "quarterly reports"

5. 文書取得

# docidまたはパスで取得（検索結果に #abc123 の形で表示される）
qmd get "docs/readme.md"
qmd get "#abc123"
qmd get abc123              # 先頭の#は省略可

# 行範囲を指定
qmd get notes/meeting.md:50 -l 100

# 複数取得（globまたはカンマ区切り、docid混在OK）
qmd multi-get "journals/2025-05*.md"
qmd multi-get "doc1.md, doc2.md, #abc123"
qmd multi-get "docs/*.md" --max-bytes 20480

6. 出力フォーマット

search / query / get / multi-get 共通で指定可能:

--json    # LLM/スクリプト向けJSON
--csv
--md      # LLMコンテキスト用Markdown
--xml
--files   # docid,score,filepath,context のみ（エージェント向け軽量出力）
--full    # 全文表示
--line-numbers

エージェント連携の定番パターン:
qmd search "authentication" --json -n 10
qmd query "error handling" --all --files --min-score 0.4
qmd get "docs/api-reference.md" --full

7. MCPサーバー（AIエージェント連携）

qmd mcp                       # stdioトランスポート（Claude Desktop/Codeが子プロセスとして起動）
qmd mcp --http                # HTTP、localhost:8181
qmd mcp --http --port 8080    # ポート指定
qmd mcp --http --daemon       # バックグラウンドデーモンとして起動
qmd mcp stop                  # 停止

公開される4ツール: query, get, multi_get, status

Claude Code へは plugin としてインストールするのが簡単です:
claude plugin marketplace add tobi/qmd
claude plugin install qmd@qmd

8. メンテナンス

qmd cleanup     # 孤立データ・キャッシュのクリーンアップ
qmd doctor      # 環境診断（モデル、GPU、DB状態など）

---

より詳しいオプション一覧は CLAUDE.md の「Commands」節、フュージョン戦略やスコア解釈は README.md を参照してください。何か特定のコマンド（例: コレクション設計、MCP設定）を深掘りしましょうか？


## Related
- [[reference/Note/AI開発/Claude-Code/MCP/QMD/QMD-使い方|QMD の使い方]]
