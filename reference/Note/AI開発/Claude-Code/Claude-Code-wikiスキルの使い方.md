---
date: 2026-05-22
description: "llm-wiki スキルの使い方を尋ねたセッションログ。init/ingest/compile/query/lint の各コマンドと標準ワークフロー、ingest がURL・ローカルMDを raw/ にフロントマッター付きで取り込む挙動"
tags:
  - reference
  - claude-code
  - llm-wiki
  - skill
---

> wikiスキルの使い方を教えて

● Read(C:/0-MD-2/_ARCHIVE/ObsidianV...2/reference/llm_wiki-MEMO.md)
● Search(Search for llm-wiki)
● Read(C:/0-MD-2/_ARCHIVE/ObsidianVault2/0-MD-2/brain/Skills.md) (ctrl+o to
expand)

  llm-wikiスキル（ llm-wiki:wiki ）は、Obsidian
  Vault内に永続的な知識ベース（Wiki）を構築・管理するためのコマンド群です。

  現在は  reference/03-Resources/my-topic/
  ディレクトリ配下でTECSに関するWikiが運用されています。
  ──────
  ### 🛠️ 主なコマンド一覧

   コマンド│ 使用例                         │ 説明
  ─────────┼────────────────────────────────┼────────────────────────────────
    init   │  /llm-wiki:wiki init <topic-nam│ 新しいWikiトピック（フォルダ構…
    ingest │  /llm-wiki:wiki ingest <file-pa│ 指定したマークダウンファイルやW
    compile│  /llm-wiki:wiki compile        │  raw/  内の生ソースを解析し、 w
    query  │  /llm-wiki:wiki query "<質問文>│ 構築されたWiki知識ベースをもと…
    lint   │  /llm-wiki:wiki lint           │ Wiki内のフロントマッター、バッ…
  ──────
  ### 📝 一般的なワークフロー（例：新しいドキュメントの追加と質問）

  1. ドキュメントのインポート ( ingest ):
    /llm-wiki:wiki ingest https://example.com/tecs-new-spec

  2. Wikiのビルド・更新 ( compile ):
    /llm-wiki:wiki compile

  3. Wikiへの問い合わせ・クエリ ( query ):
    /llm-wiki:wiki query "新しい仕様の変更点は何ですか"

  4. クエリ結果の確認:
  生成された回答ファイルは  /wiki/queries/YYYY-MM-DD-slug.md
  に保存されます。内容を確認し、問題なければコンセプトページ（ /wiki/
  配下）に昇格（ promote ）させることができます。

────────────────────────────────────────────────────────────
> /llm-wiki:wiki ingest の使い方を教えて

● Search(Search for ingest)
● Read(C:/0-MD-2/_ARCHIVE/ObsidianV...nce/Obsidian_nvk_llm-wiki.md)
● Read(C:/0-MD-2/_ARCHIVE/ObsidianV...pic/raw/ingest_html_batch.py) (ctrl+o to
expand)

▸ Thought Process
  Locating Essential Documentation
   /llm-wiki:wiki ingest （または  /wiki:ingest
  ）コマンドは、指定したファイルやURLからテキストを抽出してWikiの生ソース（
  raw/  フォルダ配下）に取り込むためのコマンドです。


取り込まれたソースはフロントマッターが付与されたマークダウン形式に整理され、そ
の後のビルド（
  compile ）コマンドのインプットとして使用されます。
  ──────
  ### 📝 基本的な使い方

    /llm-wiki:wiki ingest <ソースのパスまたはURL>

  #### 1. WebサイトのURLから取り込む


指定したURLのWebページから余計なナビゲーションやフッターを排し、メイン記事をク
リーンな状態で取り込みます。

    /llm-wiki:wiki ingest https://toppers.jp/tecs.html

  #### 2. ローカルのマークダウンやテキストファイルから取り込む

  既存のローカルドキュメントを取り込んでWikiソース化します。

    /llm-wiki:wiki ingest ~/Documents/tecs_specification.md
  ──────
  ### 🔍 内部で何が行われるか？

  1. コンテンツの解析:
  HTMLやテキストからメインテキストとタイトルを自動抽出します。
  2. 生ソースの生成:
  Wikiトピックフォルダ配下の  raw/ （または  raw/articles/
  ）フォルダに、フロントマッター付きの  .md  ファイルとして保存されます。
      • 生成されるフロントマッターの例:
        ---
        date: 2026-05-20
        source-type: article
        source-url: https://toppers.jp/tecs.html
        title: "TECSの概要"
        compiled: false
        tags: [tecs, toppers, documentation]
        description: "..."
        ---

  3. 履歴の記録:
  Wikiの運用ログファイル（ log.md ）に、ingestされた履歴が追記されます。

  │ [!TIP]
  │

複数のファイルをまとめて処理する場合は、プロジェクト内に用意されているPythonス
クリプト（例:
  │ reference/03-Resources/my-topic/raw/ingest_html_batch.py
  │

などのバッチインジェストスクリプト）を実行して一括取り込みを行うことも可能です
。

## Related

- [[llm_wiki-MEMO]]
- [[Obsidian_nvk_llm-wiki]]

