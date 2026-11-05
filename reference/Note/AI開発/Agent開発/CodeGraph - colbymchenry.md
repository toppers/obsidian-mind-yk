---
date: 2026-08-29
description: "colbymchenry/codegraph — 事前索引型のコード知識グラフMCP。ローカル完結、複数AIコーディングエージェント対応。類似ツール2件も記録"
tags:
  - reference
  - tool
  - code-graph
  - mcp
---
 - CodeGraph: Neo4j-Based Code Intelligence Platform - Go
- [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) - Go - codegraph
- Pre\-indexed code knowledge graph, auto syncs on code changes, for Claude Code, Codex, Gemini, Cursor, OpenCode, AntiGravity, Kiro, and Hermes Agent — fewer tokens, fewer tool calls, 100% local
- AI コーディングエージェントのために設計された、事前索引型のコード知識グラフ
- シンボル・呼び出し関係・影響範囲などを事前に索引化した知識グラフへクエリを投げる仕組み
- 索引化と保存はすべてローカルで完結し、外部の DB やクラウドサービスは不要
- 類似名ツール
	- [CodeGraphContext/CodeGraphContext:](https://github.com/CodeGraphContext/CodeGraphContext) (CGC)
		-  An MCP server plus a CLI tool that indexes local code into a graph database to provide context to AI assistants\.
	- [techsavvyash/codegraph](https://github.com/techsavvyash/codegraph) - Go - codegraph - このノートの対象
		- LLM\-powered code intelligence platform with SCIP indexing, Neo4j graph database, and MCP server integration
- 制約
- codegraph index scip は tecsgen に対しては実質使えません。3つの理由があります。

1. tecsgen 本体は Ruby / C（CodeGraph 非対応）

対象ディレクトリのファイル構成:

┌───────────┬───────────────────────────────┬────────────────────────────────────────────────────────────────────────────┐
│  拡張子   │              数               │                            CodeGraph SCIP 対応                             │
├───────────┼───────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ .rb       │ 191（tecsgen 本体）           │ ❌ Ruby 非対応                                                             │
├───────────┼───────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ .c / .h   │ 431 / 162                     │ ❌ C 非対応                                                                │
├───────────┼───────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ .ts / .js │ 239 / 156（tree-sitter 文法） │ ⚠️ 下記バグ                                                                │
├───────────┼───────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ .cdl      │ 235                           │ ❌ 非対応                                                                  │
├───────────┼───────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ .py       │ 39                            │ すべて .claude/.cursor の skill ツール内。tecsgen 自体に Python コードなし │
└───────────┴───────────────────────────────┴────────────────────────────────────────────────────────────────────────────┘

CodeGraph の対応言語は go, typescript, javascript, python, java, scala, kotlin, php のみ。tecsgen のコア（Ruby）はインデックス不可能です。

2. 自動検出された TypeScript 4ルートは scip-typescript の Windows バグで全滅

検出されたのは tools/ tools-ts/ 配下の tree-sitter 文法ディレクトリ4つだけ。そのすべてがこのエラーで失敗:

path.normalize('E:/.../lib/index.ts') !== E:/.../lib/index.ts

原因は @sourcegraph/scip-typescript@0.3.11 の dist/src/Packages.js:40:

if (path.normalize(filePath) !== filePath) { throw ... }

Windows では path.normalize() が / を \ に変換するため、この自己チェックが必ず失敗します。scip-typescript 0.3.11 は絶対パス指定のネイティブ Windows で動作しません（既知の非互換）。

3. 紛らわしい点

プロジェクト内の .codegraph/codegraph.db（25MB）と .cgcignore は 別ツール「CodeGraphContext」（同名の無関係プロジェクト）が生成したもので、この codegraph とは無関係です。

Neo4j 接続自体は正常（5.26.27, connected）。

対応

- TS 文法部分だけでも欲しい場合: WSL / Linux 上で実行してください。scip-typescript も scip-go も Windows より安定します。ネイティブ Windows で通したいなら Packages.js:40 の1行をパッチする方法もあります（node_modules 直編集なので脆い。やるなら指示ください）。
- tecsgen 本体（Ruby）を解析したい場合: CodeGraph は不適です。Ruby 対応のツールが必要です。

## Related

- [[AIコーディングツール・知識グラフ・コードベース分析・リポジトリ管理ツールのリファレンスリスト]]
