---
date: 2026-06-17T00:00:00.000Z
description: "nlm audio コマンドリファレンス — NotebookLMのオーディオ概要生成・管理"
tags:
  - reference
  - notebooklm
  - cli
---

 Usage: nlm audio [OPTIONS] COMMAND [ARGS]...

 Create audio overviews

╭─ Options
│ --help          Show this message and exit.
╭─ Commands
│ create  Create an audio overview (podcast) from notebook sources.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm audio create --help

 Usage: nlm audio create [OPTIONS] NOTEBOOK_ID

 Create an audio overview (podcast) from notebook sources.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --format      -f      TEXT  Overview format (deep_dive, brief, critique, debate) [default: deep_dive]
│ --length      -l      TEXT  Length (short, default, long) [default: default]
│ --language            TEXT  BCP-47 language code (en, es, fr, de, ja) [default: en]
│ --focus               TEXT  Optional focus topic
│ --source-ids  -s      TEXT  Comma-separated source IDs
│ --confirm     -y            Skip confirmation
│ --profile     -p      TEXT  Profile to use
│ --help                      Show this message and exit.



## 関連

- [[_NotebookLM-まとめ]]

