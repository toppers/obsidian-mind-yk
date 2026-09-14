---
date: 2026-09-10
description: "qmd MCP サーバーが持つコレクション9件の一覧と実パス（as of 2026-09-10）。全て ~/wiki/topics/ 配下の llm-wiki ハブが対象で、この Obsidian vault 自身は含まれない。vault の索引は別枠の 0-MD-2（CLI専用）。"
tags:
  - reference
  - qmd
  - mcp
---

# QMD コレクション一覧（as of 2026-09-10）

`qmd collection list` / `qmd collection show <name>` の結果。**9コレクションすべてが `C:\Users\ykomi\wiki\topics\` 配下**＝別の [[ベクトルDB活用-セマンティック検索ツール|llm-wiki]] ハブが対象で、**この Obsidian vault（`C:\0-MD-2\...\0-MD-2`）は1件も含まれない**。

| コレクション | 実パス | Files | Updated |
|---|---|---|---|
| `wiki-tecs-wiki` | `~/wiki/topics/tecs/wiki` | 21 | 87d ago |
| `wiki-tecs-0-wiki` | `~/wiki/topics/tecs-0/wiki` | 10 | 87d ago |
| `wiki-tecs-0-raw` | `~/wiki/topics/tecs-0/raw` | 13 | 87d ago |
| `wiki-tecs-raw` | `~/wiki/topics/tecs/raw` | 64 | 87d ago |
| `wiki-tecs-all` | `~/wiki/topics/tecs` | 89 | 87d ago |
| `wiki-tecs-0-all` | `~/wiki/topics/tecs-0` | 27 | 87d ago |
| `tecs_html` | `~/wiki/topics/tecs_html/raw` | 92 | 85d ago |
| `tecs_md` | `~/wiki/topics/tecs_md/raw` | 7 | 81d ago |
| `tecs-0-md` | `~/wiki/topics/tecs-0-md/raw` | 7 | 73d ago |

Pattern は全て `**/*.md`、`Include: yes (default)`。

## この vault を検索する索引は別枠

- `mcp__qmd__*`（MCP ツール）と `~/.claude.json` 登録の `qmd` サーバーは、上の9コレクション（llm-wiki 側）を返す。**vault の内容は返さない。**
- この vault 自身の索引名は **`0-MD-2`**（`vault-manifest.json` の `qmd_index` が空 → フォルダ名スラッグ）。CLI で明示指定してのみ到達できる:

  ```
  qmd --index 0-MD-2 query "<...>"
  ```

- `.claude/scripts/qmd-mcp.mjs`（vault 同梱の MCP サーバー）は vault 索引を pre-scope するが、`.mcp.json` は空にしてあり登録は `~/.claude.json` 側。詳細は [[Gotchas - Tooling & Config#プロジェクトの `.mcp.json` は空（`{"mcpServers": {}}`）が正しい — qmd を再追加しない|Gotchas]]。

## 履歴

- 2026-08-11 時点のスナップショットは [[使い方]]（当時は `ob-TECS*` 系3件＋`wiki-tecs*` 系6件、総316文書/162未埋め込み）。コレクション名が `ob-TECS*` → `wiki-tecs*`／`tecs*` に変わっている。

## Related

- [[使い方]] — 2026-08-11 の `qmd status` スナップショット（この一覧の旧版）
- [[QMD-SQLiteの場所]] — 索引 DB ファイル（`index.sqlite`）の探索順
- [[QMD-アーキテクチャ]] — qmd 本体の構成
- [[Gotchas - Tooling & Config]] — 空の `.mcp.json` は正しい（qmd は `~/.claude.json`）
