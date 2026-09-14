---
date: 2026-06-17T00:00:00.000Z
description: "nlm report コマンドリファレンス — ノートブックソースからレポート生成"
tags:
  - reference
  - notebooklm
  - cli
---

 Usage: nlm report [OPTIONS] COMMAND [ARGS]...

 Create reports

╭─ Options
│ --help          Show this message and exit.
╭─ Commands
│ create  Create a report from notebook sources.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm report create --help

 Usage: nlm report create [OPTIONS] NOTEBOOK_ID

 Create a report from notebook sources.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --format      -f      TEXT  Format: 'Briefing Doc', 'Study Guide', 'Blog Post', 'Create Your Own'
│                             [default: Briefing Doc]
│ --prompt              TEXT  Custom prompt (required for 'Create Your Own')
│ --language            TEXT  BCP-47 language code [default: en]
│ --source-ids  -s      TEXT  Comma-separated source IDs
│ --confirm     -y            Skip confirmation
│ --profile     -p      TEXT  Profile to use
│ --help                      Show this message and exit.



## 関連

- [[_NotebookLM-まとめ]]

