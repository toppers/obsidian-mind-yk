---
date: 2026-06-17T00:00:00.000Z
description: "nlm research コマンドリファレンス — NotebookLMのリサーチ・深掘り機能"
tags:
  - reference
  - notebooklm
  - cli
---

 Usage: nlm research [OPTIONS] COMMAND [ARGS]...

 Research and discover sources

╭─ Options
│ --help          Show this message and exit.
╭─ Commands
│ start   Start a research task to find new sources.
│ status  Check research task progress.
│ import  Import discovered sources from a completed research task.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm research start --help

 Usage: nlm research start [OPTIONS] QUERY

 Start a research task to find new sources.

 This searches the web or Google Drive to discover relevant sources
 for your research topic. Use 'nlm research status' to check progress
 and 'nlm research import' to add discovered sources to your notebook.

╭─ Arguments
│ *    query      TEXT  What to search for [required]
╭─ Options
│ --source       -s      TEXT  Where to search: web or drive [default: web]
│ --mode         -m      TEXT  Research mode: fast (~30s, ~10 sources) or deep (~5min, ~40 sources, web only)
│                              [default: fast]
│ --notebook-id  -n      TEXT  Add to existing notebook
│ --title        -t      TEXT  Title for new notebook
│ --force        -f            Start new research even if one is already pending
│ --profile      -p      TEXT  Profile to use
│ --help                       Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm research status --help

 Usage: nlm research status [OPTIONS] NOTEBOOK_ID

 Check research task progress.

 By default, polls until the task completes or times out.
 Use --max-wait 0 for a single status check.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --task-id        -t            TEXT     Specific task ID to check
│ --compact            --full             Show compact or full details [default: compact]
│ --poll-interval                INTEGER  Seconds between status checks [default: 30]
│ --max-wait                     INTEGER  Maximum seconds to wait (0 for single check) [default: 300]
│ --profile        -p            TEXT     Profile to use
│ --help                                  Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm research import --help

 Usage: nlm research import [OPTIONS] NOTEBOOK_ID [TASK_ID]

 Import discovered sources from a completed research task.

 If TASK_ID is not provided, automatically imports from the first
 available completed or in-progress research task.

╭─ Arguments
│ *    notebook_id      TEXT       Notebook ID [required]
│      task_id          [TASK_ID]  Research task ID (auto-detects if not provided)
╭─ Options
│ --indices  -i      TEXT  Comma-separated indices of sources to import (default: all)
│ --profile  -p      TEXT  Profile to use
│ --help                   Show this message and exit.



## 関連

- [[_NotebookLM-まとめ]]

