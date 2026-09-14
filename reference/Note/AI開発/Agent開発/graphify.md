---
date: 2026-08-29
description: "空キャプチャ（本文未記入）。graphify関連メモ用に確保したプレースホルダ — 詳細は graphify skill・下記リファレンスリストを参照"
tags:
  - reference
  - tool
  - stub
---
[[graphify ykominami-svn-2 実行結果]]
[Graphify\-Labs/graphify: Turn any codebase, with its docs, SQL schemas, configs, and PDFs, into a queryable knowledge graph\. A /graphify skill for Claude Code, Cursor, Codex, and Gemini CLI: local deterministic AST parsing, every edge explained, no vector store\.](https://github.com/Graphify-Labs/graphify)
# 概要
- code, docs, image, video, SQL schemas, configs, PDFs, を （質問可能な）knowledge graph　に変換
- graph.html(クリック可能)
- skill /graphify (Claude Code, Cursor, Codex, Gemini CLI)
- vector store は使わない。埋め込みなし。
# インストール
uv tool install graphifyy      # install the CLI (or: pipx install graphifyy)
graphify install               # register the skill with your AI assistant
# 使用法
/graphify .

# 出力ファイル構成
graphify-out/
├── graph.html       open in any browser — click nodes, filter, search
├── GRAPH_REPORT.md  the highlights: key concepts, surprising connections, suggested questions
└── graph.json       the full graph — query it anytime without re-reading your files
# 実装
- コードは、tree-sitter で構文解析。
## Related

- [[AIコーディングツール・知識グラフ・コードベース分析・リポジトリ管理ツールのリファレンスリスト]]
