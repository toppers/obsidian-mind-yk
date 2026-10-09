---
date: 2026-06-18
description: "AIコーディングツール・知識グラフ・コードベース分析・リポジトリ管理ツールのリファレンスリスト — Repomix/AgentMemory/graphify/CodeGraph/rtk/headroom/qmd/MarkItDown"
tags:
  - reference
  - ai-tools
  - index
---
# コード解析
[[pmd]]
- もともとJava向けに実装された。現在、JavaScript（ルールベース解析とコピペ検出）、Ruby(コピペ検出のみ)なども対象としている
## 未使用コード・デッドコードの検出
### [[knip]]
## 依存関係の分析
### [[Madge]]
### [[dependency-cruiser]]
## バンドルサイズ・パッケージ管理
### [[bundle-phobia]]
### [[Bundle Analyzer]]
### `package.json`の依存関係を最新バージョンに更新するツール
[[npm-check-updates]]
### [[wtp]]
### [[gh-poi]]
### [[semgrep]]
[[type-coverage]]
[[react-doctor]]
[[react-best-practices]]
[[mermaid-cli]]
[[textlint]]
## Racc
- 
## tree-sitter
- 文法からパーサ(構文解析器)を自動生成するパーサジェネレータツール
	- 抽象構文木(AST)を構築するのではなく、具象構文木(CST)を構築する
		- ASTが意味のない情報(例: コメントや多重括弧など)を保持しないのに対して、CSTはそのような情報も保持します
- 生成されたパーサで構文解析するライブラリでもある
- [tree\-sitter文法入門 \| フューチャー技術ブログ](https://future-architect.github.io/articles/20221215a/)
- [Tree\-sitter \- Wikipedia](https://ja.wikipedia.org/wiki/Tree-sitter)
- [プロジェクト内の全コードをTree\-sitterで構造化 → RLMによるQAを試してみた](https://zenn.dev/yumefuku/articles/codetwine-rlm)
	- [GitHub \- yumeiriowl/codetwine: A CLI tool that analyzes source code with tree\-sitter, extracts key definitions and dependencies, generates design documents via LLM, and consolidates everything into a single unified JSON\. · GitHub](https://github.com/yumeiriowl/codetwine)
- 
# Obsidian
## Plugin
### Excalidraw
---
- [[reference/Note/TECS-WG/tecsgen/tecsgen-tecsgen]] 
# [[リポジトリのMarkDown化]]
---
# ソースコードの知識グラフ化
- [[Understand-Anything]] (TypeScript)
-  [[graphify]]
-  [[CodeGraphContext(cgc)]] - Python
	- CodeGraphContext (CGC)
	- An MCP server plus a CLI tool that indexes local code into a graph database to provide context to AI assistants.

- [[CodeGraph - colbymchenry]] - 実装 Go - 対象:Go, TypeScript, 
	- CodeGraph: Neo4j-Based Code Intelligence Platform
	- Pre-indexed code knowledge graph, auto syncs on code changes, for Claude Code, Codex, Gemini, Cursor, OpenCode, AntiGravity, Kiro, CoPilot, and Hermes Agent — fewer tokens, fewer tool calls, 100% local

# ソースコードのWiki化
- [[DeepWiki]]
---
# 分散型グラフイシュートラッカー
- [[Beads|bd]]
## 最新のコンテキスト提供
- [[CocoIndex]]
- [[cocoindex-code]]
# ソースコード検索
- [[Serena]]

-  [[code-review-graph]]
-  [[better-code-review-graph]]
# ソースコード解析
- [[sourcegraph]]
---
# トークン消費量
- [[claude-monitor]]
# トークン削減
-  [[dahatake skills]](markdown-query, code-query)
	- mdq(markdown-query)BM25、grep、タグ/パス絞り込み、見出し階層の俯瞰
		- graphrag - LightRAG ベースのナレッジグラフ RAG - RAG が必要なのは「複数文書をまたいだ関係性の要約」のような、snippet 検索では答えられない質問のときだけ
	- cq(code-query) - コード検索、tree-sitter 言語パーサ
- [[rtk]] (Rust Token Killer)(出力を圧縮したいコマンドを指定-コマンドのラッパーとして呼び出す)
- [[headroom-ai]] (大量の結果を圧縮、複数の圧縮方法を選択、ハッシュを指定してオリジナル取得)

---
# エージェントのメモリー関係
## Memory.md
-  [[honcho]]
-  [[AgentMemory]]
	- [[reference/Note/PLAN/20260612]]
---
- [[Bear]]
# 検索(BM25検索、Vector検索、RAGなど)
-  [[qmd]]
# 各種ファイル(PDF,PPTなど)のMarkdown化
## [[MarkItDown]]
[[docling]]
[[doctree]]
# セッション・リポジトリ管理

## [[Entire]]
