---
date: 2026-06-17T00:00:00.000Z
description: "nlm chat コマンドリファレンス — NotebookLMノートブックへのチャット・質問応答"
tags:
  - reference
  - notebooklm
  - cli
---

 Usage: nlm chat [OPTIONS] COMMAND [ARGS]...

 Configure chat settings

╭─ Options
│ --help          Show this message and exit.
╭─ Commands
│ configure  Configure how AI responds in notebook chat.
│ start      Start interactive chat session with a notebook.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm chat configure --help

 Usage: nlm chat configure [OPTIONS] NOTEBOOK_ID

 Configure how AI responds in notebook chat.

 Goals:
 - default: Standard helpful responses
 - learning_guide: Educational, step-by-step explanations
 - custom: Use your own prompt to guide the AI

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --goal             -g      TEXT  Chat goal: default, learning_guide, or custom [default: default]
│ --prompt                   TEXT  Custom prompt (required when goal=custom, max 10000 chars)
│ --response-length  -r      TEXT  Response length: default, longer, or shorter [default: default]
│ --profile          -p      TEXT  Profile to use
│ --help                           Show this message and exit.

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm chat start --help

 Usage: nlm chat start [OPTIONS] NOTEBOOK_ID

 Start interactive chat session with a notebook.

 Enter a REPL where you can have multi-turn conversations.
 Use /help for commands, /exit to quit.

╭─ Arguments
│ *    notebook_id      TEXT  Notebook ID [required]
╭─ Options
│ --profile  -p      TEXT  Profile to use
│ --help                   Show this message and exit.



## 関連

- [[_NotebookLM-まとめ]]

