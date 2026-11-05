---
date: 2026-06-17T00:00:00.000Z
description: "nlm video コマンドリファレンス — ノートブックソースからビデオ概要生成"
tags:
  - reference
  - notebooklm
  - cli
---

 Usage: nlm video [OPTIONS] COMMAND [ARGS]...

 Create video overviews

╭─ Options
│ --help          Show this message and exit.
╭─ Commands
│ create  Create a video overview from notebook sources.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm video create --help

 Usage: nlm video create [OPTIONS] NOTEBOOK_ID

 Create a video overview from notebook sources.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --format      -f      TEXT  Format: explainer, brief [default: explainer]
│ --style       -s      TEXT  Visual style: auto_select, classic, whiteboard, kawaii, anime, watercolor, retro_print,
│                             heritage, paper_craft
│                             [default: auto_select]
│ --language            TEXT  BCP-47 language code [default: en]
│ --focus               TEXT  Optional focus topic
│ --source-ids          TEXT  Comma-separated source IDs
│ --confirm     -y            Skip confirmation
│ --profile     -p      TEXT  Profile to use
│ --help                      Show this message and exit.



## 関連

- [[_NotebookLM-まとめ]]

