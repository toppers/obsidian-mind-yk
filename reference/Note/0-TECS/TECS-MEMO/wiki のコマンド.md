---
date: 2026-06-18
description: "llm-wiki のコマンド早見 — query / lint / ingest / compile の用法。wiki-command.md とほぼ同内容"
tags:
  - reference
  - wiki
  - cheatsheet
---

- /wiki:query "シグニチャの引数方向" --wiki tecs-0-md — 記事への質問
- /wiki:lint --wiki tecs-0-md — リンク・構造の整合性チェック

- /wiki:ingest <url|ファイルパス> — Markdownソースを投入
- /wiki:compile --wiki tecs_md — ソースをwiki記事にコンパイル
- /wiki:query "質問" --wiki tecs_md — wiki に質問

/wiki:ingest --wiki tecs_md C:\Users\ykomi\Downloads\TECS-Documentation-20280608\TECS.md