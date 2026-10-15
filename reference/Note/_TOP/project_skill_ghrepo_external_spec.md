---
date: 2026-06-03
name: project-skill-ghrepo-external-spec
description: ghrepo-external-spec スキルの作成記録とドキュメント構造
tags:
  - reference
  - skill
  - ghrepo
  - spec
metadata: 
  node_type: memory
  type: project
  originSessionId: 6b138a42-4cad-4205-8470-f9d8a2fd50c4
---

`ghrepo-external-spec` スキルを `C:\Users\ykomi\.claude\skills\ghrepo-external-spec\SKILL.md` に作成。

**Why:** `docs/req/detail_claude/*.md`（要求仕様）+ `src/ghrepo/*.py`（ソース）+ `docs/spec/external_/*.md`（フォーマット参照）→ `docs/spec/external_claude/*.md` を生成するワークフローを自動化するため。

**How to apply:** `/ghrepo-external-spec` で呼び出すと、7つの仕様書ファイルを `docs/spec/external_claude/` に生成する。

## ドキュメント構造（2026-06-03 時点）

- `docs/req/detail_claude/*.md` — Claude 向け詳細要求仕様（現在: `req-subcommand-search.md` のみ）
- `docs/spec/external_/*.md` — 参照用外部仕様書 7 件（index + 6 クラス）
- `docs/spec/external_claude/` — AI 生成版出力先（空）
- `src/ghrepo/*.py` — ソースコード 7 ファイル
