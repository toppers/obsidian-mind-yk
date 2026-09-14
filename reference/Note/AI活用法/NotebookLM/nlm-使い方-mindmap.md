---
date: 2026-06-17T00:00:00.000Z
description: "nlm mindmap コマンドリファレンス — ノートブックソースからマインドマップ生成"
tags:
  - reference
  - notebooklm
  - cli
---

 Usage: nlm mindmap [OPTIONS] COMMAND [ARGS]...

 Create and manage mind maps

╭─ Options
│ --help          Show this message and exit.
╭─ Commands
│ create  Create a mind map from notebook sources.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm mindmap create --help

 Usage: nlm mindmap create [OPTIONS] NOTEBOOK_ID

 Create a mind map from notebook sources.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --title       -t      TEXT  Mind map title [default: Mind Map]
│ --source-ids  -s      TEXT  Comma-separated source IDs
│ --confirm     -y            Skip confirmation
│ --profile     -p      TEXT  Profile to use
│ --help                      Show this message and exit.



## 関連

- [[_NotebookLM-まとめ]]

