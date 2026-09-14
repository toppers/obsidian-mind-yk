---
date: 2026-06-30
description: "shardmind で breferrari/obsidian-mind を導入した実行ログ — v6.2.1・145ファイルを1.1秒で展開し Bootstrap フックまで完了"
tags:
  - reference
  - agent
  - obsidian
---

PS C:\0-MD-2\_ARCHIVE\ObsidianVault2\0-MD-3> shardmind install github:breferrari/obsidian-mind
✔ Installed breferrari/obsidian-mind@6.2.1 — 145 files in 1.1s

Bootstrap hook completed.

Hook stdout:
  git: initialized repository at vault root
  qmd: bootstrapping semantic index (this may take a moment on first run)…
  → Bootstrapping QMD index 'obsidian-mind'
  → Registering collection 'obsidian-mind' (mask **/*.md)
  → Verifying collection 'obsidian-mind' is registered

Hook stderr:
  error: unexpected argument '--index' found

  Usage: qmd <COMMAND>

  For more information, try '--help'.
  … 11 more lines (full log at .shardmind/logs/bootstrap.log)

Personalize hook completed.

Hook stdout:
  obsidian-mind: personalized brain/North Star.md for Yasuo Kominami

Next:
  start "" "C:\0-MD-2\_ARCHIVE\ObsidianVault2\0-MD-3"
PS C:\0-MD-2\_ARCHIVE\ObsidianVault2\0-MD-3 [0-MD-3:main]> start "" "C:\0-MD-2\_ARCHIVE\ObsidianVault2\0-MD-3"
Start-Process: Cannot validate argument on parameter 'FilePath'. The argument is null or empty. Provide an argument that is not null or empty, and then try the command again.
