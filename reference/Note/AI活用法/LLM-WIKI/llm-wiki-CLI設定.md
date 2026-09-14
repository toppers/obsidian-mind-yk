---
date: 2026-07-27
description: "llm-wiki CLI の設定ファイル所在・リポジトリ・スラッシュコマンド一覧と、プラグイン wiki@llm-wiki の定義所在（cache/commands/skills・enabledPlugins・marketplace の連鎖）。バージョンは自動更新される（2026-09-13時点でv0.24.4）ため本文中は都度installed_plugins.jsonを参照する前提で記述"
tags:
  - reference
  - llm-wiki
  - cli
---

# llm-wiki CLI 設定

> [!note]
> 2026-07-27 に vault root の `llm-wiki.md` から移動（vault 規約の「No user notes at root」に合わせて整理）。

## Related

- [[_LLM-WIKIまとめ]] — LLM-WIKI 関連ノートの索引
- [[Skills]] — vault 側のスラッシュコマンド・スキル一覧

# config
## ~/.config/llm-wiki/config.json
{
  "hub_path": "~/wiki",
  "resolved_path": "C:/Users/ykomi/wiki"
}
## repository
https://github.com/nvk/llm-wiki
# commands
/wiki:ingest
/wiki:assess
/wiki:compile
/wiki:librarian
/wiki:lint
/wiki:ll
/wiki:output
/wiki:plan
/wiki:project
/wiki:query
/wiki:refresh
/wiki:research
/wiki:retract
/wiki:thesis
/wiki:wiki

/wiki-manager

# topics (hub_path 配下)
確認済みのトピックフォルダ（`C:\Users\ykomi\wiki\topics`、2026-08-21時点）:
- tecs
- tecs_html
- tecs_md
- tecs-0
- tecs-0-md
=======
# plugin
## llm-wiki
## obsidian-skill

## wikiスキルの使い方を教えて

> [!warning] 以下は当時のセッション記録（verbatim）。
> 本文中の `/llm-wiki:wiki …` というプレフィックスは**現行では誤り**。有効なプラグインは `wiki@llm-wiki`（バージョンは自動更新される。2026-09-13時点でv0.24.4）で、正しくは `/wiki:ingest` のように `wiki:` プレフィックスを使う（下の「プラグイン定義の所在」節を参照）。記録として原文のまま保存している。

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

# プラグイン定義の所在（as of 2026-09-13、v0.24.4に更新済み）

`/wiki:*` の実体はどこにあるのか、を追った結果。**プラグイン `wiki@llm-wiki`** が定義元。バージョンはバックグラウンドで自動更新される——本節の初版はv0.4.4時点で書いたが、同日中（2026-09-13 07:27 UTC）にv0.24.4へ自動更新され、コマンド数も15本→29本に増加した。**バージョン番号・コマンド一覧は都度`installed_plugins.json`で確認し、鵜呑みにしない**（本節の内容自体もいずれ古くなる）。

## 実体（cache 配下）

```
C:\Users\ykomi\.claude\plugins\cache\llm-wiki\wiki\0.24.4\
├── .claude-plugin\plugin.json   ← プラグイン定義（name: "wiki", version: 0.24.4, author: nvk）
├── commands\                     ← /wiki:xxx の実体（29本、2026-09-13時点）
│   adapter / archive / assess / audit / checkpoint / collect / compile /
│   dataset / feedback / idea / ingest / ingest-collection / inventory /
│   librarian / lint / ll / output / plan / portfolio / project / query /
│   refresh / research / retract / session / specialist / thesis / wiki
└── skills\wiki-manager\SKILL.md  ← wiki:wiki-manager スキル本体（v0.4.4時点から変わらず1本）
```

旧v0.4.4のcache（`...\wiki\0.4.4\`）も削除されずに残っている——自動更新は新バージョンを追加するだけで旧cacheの掃除はしない模様。

**セッションの一覧に `wiki:assess` などが「スキル」として並ぶが、中身はスラッシュコマンド（`commands/*.md`）**。真の Skill は `wiki:wiki-manager` の1本だけ。上の「# commands」節の一覧とこの構成が対応する。

## 定義の連鎖

| レイヤ | ファイル | 内容 |
|---|---|---|
| 有効化 | `~/.claude/settings.json`（`enabledPlugins`） | `"wiki@llm-wiki": true` |
| インストール記録 | `~/.claude/plugins/installed_plugins.json` | installPath / version（自動更新されるため都度確認） / lastUpdated |
| マーケットプレイス登録 | `~/.claude/plugins/known_marketplaces.json` | GitHub `nvk/llm-wiki` |
| マーケットプレイス実体 | `~/.claude/plugins/marketplaces/llm-wiki\` | git clone。`claude-plugin/` に cache と同内容のソース。marketplace.jsonの`version`もマーケットプレイス側の最新値に追従するため、これ単体を「現在有効なバージョン」と読まないこと |

同じマーケットプレイスから **`llm-wiki@llm-wiki` v2.0.0（2026-04-22 導入、hooks/scripts 付きの新系統）も cache に存在するが、`enabledPlugins` に記載がなく無効**（2026-09-13再確認時点でも変化なし）。調査時に 2.0.0 側のファイルを読むと現行挙動と食い違う → [[Gotchas - Tooling & Config]]

## Related

- [[_LLM-WIKIまとめ]] — LLM-WIKI 関連ノートの索引
- [[Claude-Code-Plugins]] — Claude Code のプラグイン機構そのもの
- [[Gotchas - Tooling & Config]] — 2系統同居の罠
