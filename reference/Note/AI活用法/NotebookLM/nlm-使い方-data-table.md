---
date: 2026-06-17T00:00:00.000Z
description: "nlm data-table コマンドリファレンス — ノートブックソースからデータテーブルを作成する"
tags:
  - reference
  - notebooklm
  - cli
---

 Usage: nlm data-table [OPTIONS] COMMAND [ARGS]...

 Create data tables

╭─ Options
│ --help          Show this message and exit.
╭─ Commands
│ create  Create a data table from notebook sources.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm data-table create --help

 Usage: nlm data-table create [OPTIONS] NOTEBOOK_ID DESCRIPTION

 Create a data table from notebook sources.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
│ *    description      TEXT  Description of the data table to create [required]
╭─ Options
│ --language            TEXT  BCP-47 language code [default: en]
│ --source-ids  -s      TEXT  Comma-separated source IDs
│ --confirm     -y            Skip confirmation
│ --profile     -p      TEXT  Profile to use
│ --help                      Show this message and exit.



## 関連

- [[_NotebookLM-まとめ]]

