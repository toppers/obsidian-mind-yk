---
date: 2026-06-17T00:00:00.000Z
description: "nlm studio コマンドリファレンス — NotebookLMスタジオ機能（カスタマイズ・設定）"
tags:
  - reference
  - notebooklm
  - cli
---

Usage: nlm studio [OPTIONS] COMMAND [ARGS]...

 Manage studio artifacts

╭─ Options
│ --help          Show this message and exit.
╭─ Commands
│ status  List all studio artifacts and their status.
│ delete  Delete a studio artifact permanently.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm studio status --help

 Usage: nlm studio status [OPTIONS] NOTEBOOK_ID

 List all studio artifacts and their status.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --full     -a            Show all details
│ --json     -j            Output as JSON
│ --profile  -p      TEXT  Profile to use
│ --help                   Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm studio delete --help

 Usage: nlm studio delete [OPTIONS] NOTEBOOK_ID ARTIFACT_ID

 Delete a studio artifact permanently.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
│ *    artifact_id      TEXT  Artifact ID to delete [required]
╭─ Options
│ --confirm  -y            Skip confirmation
│ --profile  -p      TEXT  Profile to use
│ --help                   Show this message and exit.



## 関連

- [[_NotebookLM-まとめ]]

