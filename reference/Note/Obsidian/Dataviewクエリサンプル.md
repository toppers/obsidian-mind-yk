---
date: 2026-05-25
description: "Obsidian Dataviewクエリサンプル — ステータスと期限でフィルタリングしてリスト表示する基本パターン。"
tags:
  - reference
  - obsidian
  - dataview
---

# Dataview クエリサンプル

## 進行中・期限7日以内のリスト

```dataview
LIST file.link
FROM "プロジェクトA"
WHERE status = "進行中" AND deadline <= date(today) + dur(7 days)
SORT deadline ASC
```

## 関連

- [[10分でわかるObsidian-検索とタグ]]
