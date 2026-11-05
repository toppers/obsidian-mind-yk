---
date: 2026-08-29
description: "Serena — LSPによるシンボルレベル操作でトークン効率96%向上するコーディングツールキット。対応クライアント・対応言語・メモリシステムの使い方メモ"
tags:
  - reference
  - tool
  - serena
  - mcp
---

- [Github - serena](https://github.com/oraios/serena)
- [Serenaとは？ AIエージェントを劇的に強化するコーディングツールキットの全貌 \#ClaudeCode \- Qiita](https://qiita.com/nogataka/items/e017f6066f374ffbb640)
- [[Serena ykominami-svn-2 実行結果]]
- シンボルレベルでピンポイント操作 
-  LSPによる意味解析 
- トークン効率96%向上 
- プロジェクト知識を永続化
- 対応クライアント
	- - Claude Desktop,
	- Claude Code
	- VSCode
	- Cursor
	- Windsurf
	- Cline
	- Roo Code
	- OpenWebUI
	- Jan
	- Agno
	- Codex
	- Gemini-CLI
	- Qwen3-Coder
- 20以上の言語に対応
	- Python         
	- TypeScript/JavaScript   
	- PHP
	- Go              
	- Rust                   
	- C/C++
	- C#              
	- Ruby                    
	- Swift
	- Kotlin          
	- Java                   
	- Clojure
	- Dart            
	- Bash                    
	- Lua
	- Nix             
	- Elixir                  
	- Erlang
	- Zig             
	- AL (Dynamics 365)       
	- R
- 利点
	- コンテキストの大幅な節約
		- シンボルレベル操作
		- キャッシュ(.serena/cache)
			- pickle - Pythonオブジェクトの直列化 - _pickle_ はバイナリの直列化フォーマット
			- [pickle \-\-\- Python オブジェクトの直列化 — Python 3\.13\.14 ドキュメント](https://docs.python.org/ja/3.13/library/pickle.html)
	- AIエージェントの精度向上
		- LSPによる意味理解
	- プロジェクト知識の永続化(メモリシステム)
		- Markdown形式ファイル(.serena/memories/
		- ↓ 8. メモリ作成 
		- ├─ project_structure.md 
		- ├─ how_to_test.md
		- ├─ how_to_build.md
		- ├─ architecture.md
		- └─ key_symbols.md)
		- コンテキスト枯渇時の継続性
			1. prepare_for_new_conversation ツールを実行
			   → 現在の進捗状況をサマリ化
			2. write_memory で "task_progress.md" に保存
			   内容:
			   - 完了した作業
			   - 現在の状態
			   - 次にやるべきこと
			   - 重要な決定事項
			3. 新しいセッションを開始
			4. read_memory("task_progress.md") で前回の状態を復元
			5. 作業を継続

## Related

- [[AIコーディングツール・知識グラフ・コードベース分析・リポジトリ管理ツールのリファレンスリスト]]
- [[serena/serena-index|serena-index]]
