---
date: 2026-08-19
description: "検索・記憶系ツール一覧（QMD, PMB, rqmd等）の簡易メモ"
tags:
  - work-note
---
# Code-Search
## Code-Search-etc
- [Retrieval\-Augmented Code Generation: A Survey with Focus on Repository\-Level Approaches](https://arxiv.org/pdf/2510.04905)
### [[cocoindex]]
## semble
## graphify
- 
## pmb-code-analyzer
## CodeGraph - techsavvy
## CodeGraph - colbymch
## CodeGraphContext
## Serena
- [技術調査 \- Serena MCP](https://zenn.dev/suwash/articles/serene_mcp_20250807)
	- ### uvxを利用した推奨インストール
		- uvx --from git+https://github.com/oraios/serena serena start-mcp-server
	- ローカルへのクローンとインストール
		- git clone https://github.com/oraios/serena
		- cd serena
		- uv pip install -e .
		- uv run serena start-mcp-server
	- インデックス作成によるパフォーマンス向上
		- プロジェクトのルートで以下のコマンドを実行
		- uvx --from git+https://github.com/oraios/serena serena project index
# Full-Text-Search
# Semantic-Search
## qmd(下を見て)
## Concept-Search
# Code-Analyzer
## JSON-Compilation-Database
## graphify
## Understand-Anything
# Search-X-etc
# QMD - Markdownファイルを対象とした(フルテキストサーチ-BM25・ベクトル検索-意味検索・LLMによるリランク機能)
- [[qmd-cmd-使い方]]
-  [CMD | MCP] [GitHub \- tobi/qmd: mini cli search engine for your docs, knowledge bases, meeting notes, whatever\. Tracking current sota approaches while being all local · GitHub](https://github.com/tobi/qmd)
- [MCP] - [GitHub \- ehc\-io/qmd: Query Markdown \- MCP server for hybrid search over markdown knowledge bases · GitHub](https://github.com/ehc-io/qmd)
- Rust版 - [GitHub \- qntx\-labs/qmd: Lightweight local search engine for AI agents in Rust\. · GitHub](https://github.com/qntx-labs/qmd)
- Rust版 - [GitHub \- stn/rqmd: Rust port of qmd: mini cli search engine for your docs, knowledge bases, meeting notes, whatever\. Tracking current sota approaches while being all local · GitHub](https://github.com/stn/rqmd)
# PMB - AIエージェントが判断、教訓をプロジェクトごとに記録・検索-SQLiteで保存
- [[pmb-cmd-使い方]]

## Related
-
