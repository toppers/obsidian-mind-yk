---
date: 2026-08-27
description: "dahatake/skills リポジトリのmarkdown-query・code-query・tool-searcchスキルのメモ — トークン削減目的の横断検索アプローチ"
tags:
  - reference
  - ai
  - agents
---

# dahatake skills

- [Vibe Coding のトークン消費量の40\-60%を占めることもある、Markdownファイルの読み込みトークン消費量を最大98%以上圧縮する markdown\-query スキル \#GitHubCopilot \- Qiita](https://qiita.com/dahatake/items/ce9917268d8d18aa9b6c)
- [GitHub \- dahatake/skills: agent plugin providing skills · GitHub](https://github.com/dahatake/skills)
- md( [[dahatake skills mdq index]]) - 読み取り専用で、関連する見出しチャンクだけを抽出して渡す。
	- BM25検索: 自然言語クエリで関連度順に上位N件
	- grep検索: 完全一致したいキーワード用
	- タグ/パス絞り込み: frontmatter のtags やglobで範囲限定
	- 見出し階層の俯瞰: mdq list でファイル横断見出し一覧 
	- [[dahatake skills graphrag]]
- cq( [[dahatake skills code-query|code-query]]) 
	- skill - ソースコードを横断検索し、定義・参照・小さな snippet だけを返す
- tool-searcch - ライブラリ - Copilot SDK セッションへ渡すツール定義を、必要なものだけに絞る 
	- markdown-queryとcode-queryは索引対象が排他。.mdとCSV/TSVはmarkdown-query, ソースコードはcode-query
- インストール
```
 RepoRoot <path>
	- SkipPrereq
	- WithGui
	- WithWatch
	- WithTokenizer
	- NoIndex
	
	pwsh -NoLogo -NoProfile -File tools\kits\markdown-query\install.ps1 -SkipPrereq -WithGui -WithWatch -WithTokenizer -NoIndex	
	--repo-root <path>
	--skip-prereq
	--with-gui
	--with-watch
	--with-tokenizer
	--no-index
```
- 使用例
	```
	bash tools/kits/markdown-query/mdq.sh index --strategy graphrag \
    --root <対象ディレクトリ> \
    --graphrag-working-dir .mdq/graphrag-ja-jp \
    --graphrag-llm-provider ollama --graphrag-llm-model qwen2.5:7b \
    --graphrag-embed-provider ollama --graphrag-embed-model nomic-embed-text

	bash tools/kits/markdown-query/mdq.sh index --strategy graphrag \
    --root .\docs\from_source_2\spec\external \
    --graphrag-working-dir .mdq/graphrag-ja-jp \
    --graphrag-llm-provider ollama --graphrag-llm-model qwen2.5:7b \
    --graphrag-embed-provider ollama --graphrag-embed-model nomic-embed-text

	pwsh tools/kits/markdown-query/mdq.ps1 index --strategy graphrag \
    --root .\docs\from_source_2\spec\external \
    --graphrag-working-dir .mdq/graphrag-ja-jp \
    --graphrag-llm-provider ollama --graphrag-llm-model qwen2.5:7b \
    --graphrag-embed-provider ollama --graphrag-embed-model nomic-embed-text

	pwsh tools/kits/markdown-query/mdq.ps1 index --strategy graphrag --root .\docs\from_source_2\spec\external --graphrag-working-dir .mdq/graphrag-ja-jp     --graphrag-llm-provider ollama --graphrag-llm-model qwen2.5:7b --graphrag-embed-provider ollama --graphrag-embed-model nomic-embed-text

	```
- 使用例2
```
bash tools/kits/markdown-query/mdq.sh index --strategy graphrag \
    --root <対象ディレクトリ> \
    --graphrag-working-dir .mdq/graphrag-ja-jp \
    --graphrag-llm-provider ollama --graphrag-llm-model qwen2.5:7b \
    --graphrag-embed-provider ollama --graphrag-embed-model nomic-embed-text
	
tools/kits/markdown-query/mdq.ps1 index --strategy graphrag \
    --root .\src \
    --graphrag-working-dir .mdq/graphrag-ja-jp \
    --graphrag-llm-provider ollama --graphrag-llm-model qwen2.5:7b \
    --graphrag-embed-provider ollama --graphrag-embed-model nomic-embed-text
	
tools/kits/markdown-query/mdq.ps1 index --strategy graphrag --root .\src --graphrag-working-dir .mdq/graphrag-ja-jp --graphrag-llm-provider ollama --graphrag-llm-model qwen2.5:7b --graphrag-embed-provider ollama --graphrag-embed-model nomic-embed-text
```
