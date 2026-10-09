---
date: 2026-06-30
description: "shardmind（obsidian-mind テンプレート配布・更新CLI）のコマンド早見表と、v6.2.1 導入の実行ログ。更新手順は Patterns / Gotchas ノートへリンク"
tags:
  - reference
  - agent
  - obsidian
---

## 使い方（コマンド早見表、2026-09-29 時点）

`shardmind` は obsidian-mind テンプレートの配布・更新用CLI。このVaultには `.shardmind/`、`.shardmindignore`、`shard-values.yaml` がある。

| コマンド | 用途 |
|---|---|
| `shardmind` | 現在のシャード状態を表示 |
| `shardmind --verbose` | 詳細表示（値・モジュール・ファイル・「modified by you」一覧など） |
| `shardmind install <ref>` | カレントにシャードをインストール（例: `breferrari/obsidian-mind`） |
| `shardmind adopt <ref>` | シャードなしでクローン済みのVaultにエンジンを後付け |
| `shardmind update` | 最新版へ更新。`--dry-run --json` で更新プランのみ確認 |
| `--no-update-check` | 1日1回のnpm更新チェックを無効化 |

**更新は事故りやすい**（managed ファイルが再描画され、地元カスタマイズが巻き戻る。v8.4.0 で実例あり）。更新前後の手順・`ownership: modified` 固定・`--yes` 禁止などは重複記載せずここを参照:

- [[Patterns - 検証と調査 Archive#shardmind をクロバーなしで更新する（2026-09-09）]] — 更新前チェック・更新実行・更新後レビューの手順
- [[Gotchas - Git & Vault Integrity#shardmind の更新は managed ファイルを再レンダーして地元のカスタマイズを巻き戻す]] — 巻き戻し事故の詳細と復旧

## 導入ログ（2026-06-30）

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
