---
date: 2026-06-17T00:00:00.000Z
description: "nlm infographic コマンドリファレンス — ノートブックソースからインフォグラフィック生成"
tags:
  - reference
  - notebooklm
  - cli
---

Usage: nlm infographic [OPTIONS] COMMAND [ARGS]...

 Create infographics

╭─ Options
│ --help          Show this message and exit.
╭─ Commands
│ create  Create an infographic from notebook sources.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm infographic create --help

 Usage: nlm infographic create [OPTIONS] NOTEBOOK_ID

 Create an infographic from notebook sources.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --orientation  -o      TEXT  Orientation: landscape, portrait, square [default: landscape]
│ --detail       -d      TEXT  Detail level: concise, standard, detailed [default: standard]
│ --language             TEXT  BCP-47 language code [default: en]
│ --focus                TEXT  Optional focus topic
│ --source-ids   -s      TEXT  Comma-separated source IDs
│ --confirm      -y            Skip confirmation
│ --profile      -p      TEXT  Profile to use
│ --help                       Show this message and exit.



## 関連

- [[_NotebookLM-まとめ]]

