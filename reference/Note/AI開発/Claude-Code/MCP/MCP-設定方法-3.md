---
date: 2026-08-21
description: "pmb MCPサーバーの削除手順（user/projectスコープ）とshardmindプロジェクトのMCP設定所在メモ"
tags:
  - reference
  - ai
  - mcp
---

# MCP 設定方法 (3) — pmb MCP削除・shardmind プロジェクトMCP

> 関連: [[MCP-設定方法]] / [[MCP-設定方法-2]] / [[reference/Note/AI開発/Claude-Code/MCP/PMB/pmb-cmd-使い方|PMB CMD使い方]]

## pmb MCPサーバーの削除

```
claude mcp remove pmb -s user
claude mcp remove pmb -s project
```

- `user pmb-mcp` — user スコープの pmb MCP
- `project http://127.0.0.1:8765/mcp` — project スコープの pmb MCP（ローカルHTTPエンドポイント）

## shardmind プロジェクトの Project MCPs

- 定義ファイル: `E:\Crepo\github-ai-4-o_s\shardmind\.mcp.json`

## Related

- [[MCP-設定方法]]
- [[MCP-設定方法-2]]
