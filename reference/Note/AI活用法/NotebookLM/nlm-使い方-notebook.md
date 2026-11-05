---
date: 2026-06-17T00:00:00.000Z
description: "nlm notebook コマンドリファレンス — ノートブックの作成・一覧・削除・管理"
tags:
  - reference
  - notebooklm
  - cli
---

 Usage: nlm notebook [OPTIONS] COMMAND [ARGS]...

 Manage notebooks

╭─ Options
│ --help          Show this message and exit.
╭─ Commands
│ list      List all notebooks.
│ create    Create a new notebook.
│ get       Get notebook details.
│ describe  Get AI-generated notebook summary with suggested topics.
│ rename    Rename a notebook.
│ delete    Delete a notebook permanently.
│ query     Chat with notebook sources.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm notebook list --help

 Usage: nlm notebook list [OPTIONS]

 List all notebooks.

╭─ Options
│ --full     -a            Show all columns
│ --json     -j            Output as JSON
│ --quiet    -q            Output IDs only
│ --title    -t            Show ID: Title format
│ --profile  -p      TEXT  Profile to use
│ --help                   Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm notebook create --help

 Usage: nlm notebook create [OPTIONS] [TITLE]

 Create a new notebook.

╭─ Arguments
│   title      [TITLE]  Notebook title
╭─ Options
│ --profile  -p      TEXT  Profile to use
│ --help                   Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm notebook get --help

 Usage: nlm notebook get [OPTIONS] NOTEBOOK_ID

 Get notebook details.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --json     -j            Output as JSON
│ --profile  -p      TEXT  Profile to use
│ --help                   Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm notebook describe --help

 Usage: nlm notebook describe [OPTIONS] NOTEBOOK_ID

 Get AI-generated notebook summary with suggested topics.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --profile  -p      TEXT  Profile to use
│ --help                   Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm notebook rename --help

 Usage: nlm notebook rename [OPTIONS] NOTEBOOK_ID NEW_TITLE

 Rename a notebook.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
│ *    new_title        TEXT  New title [required]
╭─ Options
│ --profile  -p      TEXT  Profile to use
│ --help                   Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm notebook delete --help

 Usage: nlm notebook delete [OPTIONS] NOTEBOOK_ID

 Delete a notebook permanently.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --confirm  -y            Skip confirmation
│ --profile  -p      TEXT  Profile to use
│ --help                   Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm notebook query --help

 Usage: nlm notebook query [OPTIONS] NOTEBOOK_ID QUESTION

 Chat with notebook sources.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
│ *    question         TEXT  Question to ask [required]
╭─ Options
│ --conversation-id  -c      TEXT  Conversation ID for follow-up questions
│ --source-ids       -s      TEXT  Comma-separated source IDs to query (default: all)
│ --profile          -p      TEXT  Profile to use
│ --help                           Show this message and exit.



## 関連

- [[_NotebookLM-まとめ]]

