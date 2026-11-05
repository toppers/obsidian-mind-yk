---
date: 2026-06-17T00:00:00.000Z
description: "nlm quiz コマンドリファレンス — ノートブックソースからクイズ生成"
tags:
  - reference
  - notebooklm
  - cli
---

 Usage: nlm quiz [OPTIONS] COMMAND [ARGS]...

 Create quizzes

╭─ Options
│ --help          Show this message and exit.
╭─ Commands
│ create  Create a quiz from notebook sources.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm quiz create --help

 Usage: nlm quiz create [OPTIONS] NOTEBOOK_ID

 Create a quiz from notebook sources.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --count       -c      INTEGER  Number of questions [default: 2]
│ --difficulty  -d      INTEGER  Difficulty 1-5 (1=easy, 5=hard) [default: 2]
│ --source-ids  -s      TEXT     Comma-separated source IDs
│ --confirm     -y               Skip confirmation
│ --profile     -p      TEXT     Profile to use
│ --help                         Show this message and exit.



## 関連

- [[_NotebookLM-まとめ]]

