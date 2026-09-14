---
date: 2026-08-29
description: "dahatake/skills code-query（cq）の実装詳細 — Pythonパッケージ・SQLite索引・7層構成・fail-closed設定・cAST chunking・trigram正規表現検索の設計判断"
tags:
  - reference
  - tool
  - dahatake-skills
  - code-search
---

code-query（cq）の実装

Python パッケージとして実装されており、.cq/ 配下に SQLite で索引を永続化するローカル完結型ツールです（外部API呼び出しなし、文法ファイルのネットワーク取得なし）。実体は code-query/vendor/cq/ にあります。

全体構成（7層）

Agent/CLI
  → ② CLI層:      cq/cli.py, cq/__main__.py（argparseでサブコマンド振り分け）
  → ③ 設定/列挙:   cq/config.py（profile解決）, cq/discovery.py（git ls-files + 拡張子allowlist）
  → ④ Indexing層:  cq/indexer.py, cq/languages/（言語別パーサ）, cq/chunking.py（cAST）, cq/traces.py
  → ⑤ Search層:    cq/search.py（route判定+BM25/trigram）, cq/freshness.py（自動再索引）, cq/repomap.py
  → ⑥ Watcher層:   cq/watcher.py（watchdog、任意）
  → ⑦ Storage層:   cq/store.py + .cq/index-<profile>.sqlite

主な設計判断

1. fail-closed な設定 — markdown-queryと違い既定rootsが存在せず、cq.tomlが無ければ推測せずエラー終了する。誤ったツリーを索引して自信満々の誤答を返すのを防ぐため。

2. ファイル列挙はgit経由 — git ls-files --cached --others --exclude-standard。.gitignoreは尊重するがgit管理外ディレクトリは索引不可（DiscoveryError）。

3. 索引ビルド（cq index）
- SHA-1とサイズが一致したファイルはスキップ（増分索引）
- 言語別extractor（cq/languages/）がRawSymbol[]を抽出。失敗時はlite（正規表現ベース）へ自動降格し、索引全体は失敗させない
- chunking.pyがcAST（split-then-merge、arXiv:2506.15655）でチャンク分割
- symbol_idはsha1(path|qualname|kind|occurrence)で安定（行番号が動いてもIDは変わらない）

4. 言語プラグイン契約 — Python標準のast、それ以外はtree-sitter公式文法（任意依存、wheel同梱でネットワーク取得なし）。SQLはsqlglot主・sqlfluff補助。未導入言語はlite降格のみで他言語には影響しない。新言語追加はextract()を実装するだけでstore.py/indexer.py/search.pyは変更不要。

5. 4層の索引構造（SQLite内）

│ 層  │      テーブル       │      方式      │               用途               │
│ L0  │ symbols             │ 通常索引       │ 定義の直接引き                   │
│ L1  │ chunks_tri          │ FTS5 trigram   │ 部分一致・正規表現の前段絞り込み │
│ L2  │ chunks_fts          │ FTS5 unicode61 │ BM25自然文検索                   │
│ L3  │ refs/imports/traces │ 通常索引       │ 呼び出し元・依存・設計文書対応   │

ランキングはSQLite内で完結（mdqと違いPython側へ全チャンクをロードしない）。BM25の列重みはname:10.0, signature:5.0, ident_text:3.0, text:1.0。

6. 検索時の自動修復（freshness） — cq search実行のたびに索引済みファイルのstat()だけで差分を突合し、50件以下なら自動再索引。超過時は{"warning":"stale"}を返す。ただし新規未索引ファイルはこの対象外（索引済みパスしかstatしない）。

7. モードルーティング（choose_route()） — 優先順位: --re指定→regex / ID完全一致→trace / 識別子完全一致→symbol / 記号含む3文字以上→substr / それ以外→bm25。0件時は経路ごとに決まったフォールバック順で再試行する。

8. 正規表現検索 — Russ Cox方式のtrigram2段構え。パターンからリテラル部分列を抽出しtrigram索引で候補を絞り、候補にだけPythonのreを適用。

主要ファイルの対応（SoT）は code-query/docs/skills-code-query.md の §1.3 に一覧があり、cq/cli.py・config.py・discovery.py・indexer.py・chunking.py・search.py・freshness.py・store.py・repomap.py・traces.py・watcher.pyがそれぞれ上記の役割を担っています。より詳細（メッセージフロー図、チャンク分割の内部仕様、索引データファイル一覧など）は同ドキュメントの§1〜§4を参照してください。

## Related

- [[dahatake skills code-query]]
- [[AIコーディングツール・知識グラフ・コードベース分析・リポジトリ管理ツールのリファレンスリスト]]
