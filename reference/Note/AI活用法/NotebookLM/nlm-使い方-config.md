---
date: 2026-06-17T00:00:00.000Z
description: "nlm config コマンドリファレンス — CLI設定の取得・更新・管理"
tags:
  - reference
  - notebooklm
  - cli
---

 Usage: nlm config [OPTIONS] COMMAND [ARGS]...

 Manage configuration

╭─ Options
│ --help          Show this message and exit.
╭─ Commands
│ show  Show current configuration.
│ get   Get a specific configuration value.
│ set   Set a configuration value.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm config show --help

 Usage: nlm config show [OPTIONS]

 Show current configuration.

╭─ Options
│ --json  -j        Output as JSON
│ --help            Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm config get --help

 Usage: nlm config get [OPTIONS] KEY

 Get a specific configuration value.

╭─ Arguments
│ *    key      TEXT  Configuration key (e.g. output.format) [required]
╭─ Options
│ --help          Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm config set --help

 Usage: nlm config set [OPTIONS] KEY VALUE

 Set a configuration value.

╭─ Arguments
│ *    key        TEXT  Configuration key (e.g. output.format) [required]
│ *    value      TEXT  Value to set [required]
╭─ Options
│ --help          Show this message and exit.



## 関連

- [[_NotebookLM-まとめ]]

