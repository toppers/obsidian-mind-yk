---
date: 2026-06-17T00:00:00.000Z
description: "nlm alias コマンドリファレンス — IDエイリアスの作成・取得・一覧・削除"
tags:
  - reference
  - notebooklm
  - cli
---

Usage: nlm alias [OPTIONS] COMMAND [ARGS]...

 Manage ID aliases

╭─ Options
│ --help          Show this message and exit.
╭─ Commands
│ set     Create or update an alias for an ID.
│ get     Get the value of an alias.
│ list    List all aliases.
│ delete  Delete an alias.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm alias set --help

 Usage: nlm alias set [OPTIONS] NAME VALUE

 Create or update an alias for an ID.

╭─ Arguments
│ *    name       TEXT  Alias name (e.g. 'my-notebook') [required]
│ *    value      TEXT  ID value (e.g. valid UUID) [required]
╭─ Options
│ --type     -t      TEXT  Type: notebook, source, artifact, task (auto-detected if not specified)
│ --profile  -p      TEXT  Profile to use for detection
│ --help                   Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm alias get --help

 Usage: nlm alias get [OPTIONS] NAME

 Get the value of an alias.

╭─ Arguments
│ *    name      TEXT  Alias name [required]
╭─ Options
│ --help          Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm alias list --help

 Usage: nlm alias list [OPTIONS]

 List all aliases.

╭─ Options
│ --help          Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm alias delete --help

 Usage: nlm alias delete [OPTIONS] NAME

 Delete an alias.

╭─ Arguments
│ *    name      TEXT  Alias name [required]
╭─ Options
│ --confirm  -y        Skip confirmation
│ --help               Show this message and exit.



## 関連

- [[_NotebookLM-まとめ]]

