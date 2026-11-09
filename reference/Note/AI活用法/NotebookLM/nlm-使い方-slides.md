---
date: 2026-06-17T00:00:00.000Z
description: "nlm slides コマンドリファレンス — ノートブックソースからスライド生成"
tags:
  - reference
  - notebooklm
  - cli
---

Usage: nlm slides [OPTIONS] COMMAND [ARGS]...

 Create slide decks

**Options**

| オプション | 短縮 | 型 | 説明 |
| --- | --- | --- | --- |
| --help |  |  | Show this message and exit. |

**Commands**

| コマンド | 説明 |
| --- | --- |
| create | Create a slide deck from notebook sources. |

PS E:\Ccur\python3\notebooklm-cli-x [notebooklm-cli-x:main]> nlm slides create --help

 Usage: nlm slides create [OPTIONS] NOTEBOOK_ID

 Create a slide deck from notebook sources.

**Arguments**

| 必須 | 引数 | 型 | 説明 |
| --- | --- | --- | --- |
| * | notebook_id | TEXT | Notebook ID [required] |

**Options**

| オプション | 短縮 | 型 | 説明 |
| --- | --- | --- | --- |
| --format | -f | TEXT | Format: detailed, presenter [default: detailed] |
| --length | -l | TEXT | Length: short, default [default: default] |
| --language |  | TEXT | BCP-47 language code [default: en] |
| --focus |  | TEXT | Optional focus topic |
| --source-ids | -s | TEXT | Comma-separated source IDs |
| --confirm | -y |  | Skip confirmation |
| --profile | -p | TEXT | Profile to use |
| --help |  |  | Show this message and exit. |



## 関連

- [[_NotebookLM-まとめ]]

