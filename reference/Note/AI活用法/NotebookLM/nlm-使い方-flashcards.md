---
date: 2026-06-17T00:00:00.000Z
description: "nlm flashcards コマンドリファレンス — ノートブックソースからフラッシュカード生成"
tags:
  - reference
  - notebooklm
  - cli
---

Usage: nlm flashcards [OPTIONS] COMMAND [ARGS]...

 Create flashcards

╭─ Options
│ --help          Show this message and exit.
╭─ Commands
│ create  Create flashcards from notebook sources.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm flashcards create --help

 Usage: nlm flashcards create [OPTIONS] NOTEBOOK_ID

 Create flashcards from notebook sources.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --difficulty  -d      TEXT  Difficulty: easy, medium, hard [default: medium]
│ --source-ids  -s      TEXT  Comma-separated source IDs
│ --confirm     -y            Skip confirmation
│ --profile     -p      TEXT  Profile to use
│ --help                      Show this message and exit.



## 関連

- [[_NotebookLM-まとめ]]

