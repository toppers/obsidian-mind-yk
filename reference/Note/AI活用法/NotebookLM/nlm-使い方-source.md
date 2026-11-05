---
date: 2026-06-17T00:00:00.000Z
description: "nlm source コマンドリファレンス — ノートブックへのソース追加・一覧・削除管理"
tags:
  - reference
  - notebooklm
  - cli
---

 Usage: nlm source [OPTIONS] COMMAND [ARGS]...

 Manage sources

╭─ Options
│ --help          Show this message and exit.
╭─ Commands
│ list      List sources in a notebook.
│ add       Add a source to a notebook.
│ get       Get source details.
│ describe  Get AI-generated source summary with keywords.
│ content   Get raw source content (no AI processing).
│ delete    Delete a source permanently.
│ stale     List Drive sources that need syncing.
│ sync      Sync Drive sources with latest content.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm source list --help

 Usage: nlm source list [OPTIONS] NOTEBOOK_ID

 List sources in a notebook.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --full            -a            Show all columns
│ --drive           -d            Show Drive sources with freshness status
│ --skip-freshness  -S            Skip freshness checks (faster, use with --drive)
│ --json            -j            Output as JSON
│ --quiet           -q            Output IDs only
│ --url             -u            Output as ID: URL
│ --profile         -p      TEXT  Profile to use
│ --help                          Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm source add --help

 Usage: nlm source add [OPTIONS] NOTEBOOK_ID

 Add a source to a notebook.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --url      -u      TEXT  URL to add (website or YouTube)
│ --text     -t      TEXT  Text content to add
│ --drive    -d      TEXT  Google Drive document ID
│ --youtube  -y      TEXT  YouTube URL
│ --title            TEXT  Title for the source
│ --type             TEXT  Drive doc type: doc, slides, sheets, pdf [default: doc]
│ --profile  -p      TEXT  Profile to use
│ --help                   Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm source get --help

 Usage: nlm source get [OPTIONS] SOURCE_ID

 Get source details.

╭─ Arguments
│ *    source_id      TEXT  Source ID [required]
╭─ Options
│ --json     -j            Output as JSON
│ --profile  -p      TEXT  Profile to use
│ --help                   Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm source describe --help

 Usage: nlm source describe [OPTIONS] SOURCE_ID

 Get AI-generated source summary with keywords.

╭─ Arguments
│ *    source_id      TEXT  Source ID [required]
╭─ Options
│ --profile  -p      TEXT  Profile to use
│ --help                   Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm source content --help

 Usage: nlm source content [OPTIONS] SOURCE_ID

 Get raw source content (no AI processing).

╭─ Arguments
│ *    source_id      TEXT  Source ID [required]
╭─ Options
│ --output   -o      TEXT  Write content to file
│ --profile  -p      TEXT  Profile to use
│ --help                   Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm source delete --help

 Usage: nlm source delete [OPTIONS] SOURCE_ID

 Delete a source permanently.

╭─ Arguments
│ *    source_id      TEXT  Source ID [required]
╭─ Options
│ --confirm  -y            Skip confirmation
│ --profile  -p      TEXT  Profile to use
│ --help                   Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm source stale --help

 Usage: nlm source stale [OPTIONS] NOTEBOOK_ID

 List Drive sources that need syncing.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --json     -j            Output as JSON
│ --profile  -p      TEXT  Profile to use
│ --help                   Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm source sync --help

 Usage: nlm source sync [OPTIONS] NOTEBOOK_ID

 Sync Drive sources with latest content.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --source-ids  -s      TEXT  Comma-separated source IDs to sync (default: all stale)
│ --confirm     -y            Skip confirmation
│ --profile     -p      TEXT  Profile to use
│ --help                      Show this message and exit.



## 関連

- [[_NotebookLM-まとめ]]

