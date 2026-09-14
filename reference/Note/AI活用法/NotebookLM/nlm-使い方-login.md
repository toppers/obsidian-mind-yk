---
date: 2026-06-17T00:00:00.000Z
description: "nlm login コマンドリファレンス — NotebookLM CLIへのログイン・認証フロー"
tags:
  - reference
  - notebooklm
  - cli
---

 Usage: nlm login [OPTIONS]

 Authenticate with NotebookLM.

 Default: Uses Chrome DevTools Protocol to extract cookies automatically.
 Use --manual to import cookies from a file.

╭─ Options
│ --manual   -m            Manually provide cookies from a file
│ --check                  Only check if current auth is valid
│ --profile  -p      TEXT  Profile name to save credentials to [default: default]
│ --file     -f      TEXT  Path to file containing cookies (for manual mode)
│ --help                   Show this message and exit.



## 関連

- [[_NotebookLM-まとめ]]

