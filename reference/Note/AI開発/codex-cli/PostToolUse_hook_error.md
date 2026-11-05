---
date: 2026-07-07
description: "PostToolUse フックのエラー原因 — Obsidian vault 用のフックが gistx の作業ディレクトリで実行され、存在しないスクリプトを参照していた"
tags:
  - reference
  - codex
  - hook
  - troubleshooting
---

• 原因は、Obsidian vault 用の PostToolUse hook が gistx 作業ディレクトリで実行され、存在しない script を参照しているため
  です。

  確認できた実体はこれです。

  - 現在の gistx には .codex\hooks.json がありません。
  - グローバル C:\Users\ykomi\.codex\hooks.json には PostToolUse はなく、PreToolUse だけです。
  - Codex の trusted hook state は C:\0-MD-2\_ARCHIVE\ObsidianVault2\0-MD-2\.codex\hooks.json の post_tool_use を指して
    います。

  - その hook は以下を実行します。
      - .claude/scripts/validate-write.ts
      - .claude/scripts/qmd-refresh.ts

  - しかし E:\Ccur\python3\gistx\.claude\scripts\... は存在しません。

  再現結果も MODULE_NOT_FOUND でした。

  Cannot find module 'E:\Ccur\python3\gistx\.claude\scripts\validate-write.ts'
  Cannot find module 'E:\Ccur\python3\gistx\.claude\scripts\qmd-refresh.ts'

  つまり、hook 定義自体は Obsidian vault では成立しますが、CODEX_PROJECT_DIR=E:\Ccur\python3\gistx の状態で走ると、gistx
  配下の存在しない .claude\scripts を見に行って失敗します。

  対処はどちらかです。

  1. gistx ではその PostToolUse hook を無効化する
  2. hook コマンド側で script が存在しない場合は exit 0 するガードを入れる
  3. gistx に必要な .claude\scripts を用意する

  このケースでは 2 が一番安全です。Obsidian vault では動かしつつ、他 project では何もしない動きにできます。
