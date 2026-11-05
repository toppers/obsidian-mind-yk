---
date: 2026-09-09
description: "cocoindex-code（ccc）— AST ベースの軽量な組み込みコード検索エンジン CLI。意味検索・構造的 grep・MCP サーバ、コーディングエージェント向けにローカル埋め込み同梱。"
tags:
  - reference
---

# cocoindex-code

> `cocoindex-code`（コマンドは `ccc`）。[[CocoIndex]] のコード検索特化版。親リストは [[AIコーディングツール・知識グラフ・コードベース分析・リポジトリ管理ツールのリファレンスリスト]]。

- [CocoIndex Code — speed up Claude Code, Cursor & Codex](https://cocoindex.io/cocoindex-code/)
- AST-aware semantic code search context. Works with all coding agents. Sees your _whole_ repo at once.
- CLI, skills, MCP
- [GitHub \- cocoindex\-io/cocoindex\-code: A super light\-weight embedded code search engine CLI \(AST based\) that just works \- improves speed and efficiency for coding agent 🌟 Star if you like it\! · GitHub](https://github.com/cocoindex-io/cocoindex-code)
- インストール
	- pipx
		- pipx install 'cocoindex-code[full]'         # batteries included (local embeddings)
		- pipx upgrade cocoindex-code                  # upgrade
	- uv
		- uv tool install --upgrade 'cocoindex-code[full]'

	- Docker
		- cocoindex-code[full]
			- batteries-included. Pulls in `sentence-transformers` so local embeddings (no API key required) work out of the box. The `ccc init` interactive prompt defaults to [Snowflake/snowflake-arctic-embed-xs](https://huggingface.co/Snowflake/snowflake-arctic-embed-xs).
		- `cocoindex-code` (slim) 
			- LiteLLM-only; requires a cloud embedding provider and API key. Use when you don't want the local-embedding deps (~1 GB of torch + transformers).
- コーディングエージェント統合
	- このリポジトリ自体が1個のプラグインマーケットプレイス(.claude-plugin/marketplace.json)
		- Claude CodeとGrokが購読。同一のplugin id `cocoindex-code`, 同一のスキル`ccc`
		- Grokはオプションとして、hooksとMCPサーバを活性化する
		- Claude Codeはskillのみ。必要に応じてhooks/MCPサーバをロードする
	- npx skills add cocoindex-io/cocoindex-code
		- ccc init も ccc index も要らない
		- エージェントが初期化、インデック化、インデックス更新を行う
- CLI
	- ccc init
	- ccc index
	- ccc search  `<query>` 意味検索
	- ccc grep `<patterm>` 構造的コード検索(インデックス不要) 
	-  ccc status
	-  ccc mcp stdioモードでMCPサーバとして実行
	-  ccc doctor 検査 
	-  ccc reset インデックス削除
	-  ccc version
	-  ccc daemon status
	-  ccc daemon restart
	-  ccc daemon stop
	- ccc search database schema
	- ccc search --lang python --lang markdown schema
	- ccc search --path "`src/utils/*`" query handler
	- ccc search --offset 10 --limit 5 database schema ページネーション
	- ccc grep 'def \NAME(\(ARGS\\)'
	- ccc grep 'foo(\(ARGS*\))' src/
	- ccc grep 'foo(\(ARGS*\))'  --lang rust
	- ccc grep 'class \NAME:' --path 'tests/**'
	- ccc grep 'TODO(\A*\)' path/to/file.py
	- メタ変数
		- \ 
		- \NAME 1個のノード
		- \(NAME*\\) 立て続けに生まれた兄弟
		- `\_`/`\*` 