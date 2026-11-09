---
date: 2026-04-19
description: "ガジェット一覧 — Dataviewクエリで#gadgetタグ付きノートから使用中/全ガジェットを表形式表示"
tags:
  - reference
  - gadget
---

# ガジェット一覧

## 使用中

```dataview
TABLE brand AS "メーカー", model AS "型番", purchase_date AS "購入日", price AS "価格"
FROM #gadget
WHERE status = "使用中"
SORT purchase_date DESC
```

## すべてのガジェット

```dataview
TABLE category AS "カテゴリ", brand AS "メーカー", model AS "型番", status AS "状態"
FROM #gadget
SORT category, purchase_date DESC
```

## Related
- [[North Star]]
