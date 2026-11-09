---
date: 2026-05-31
tags: [tecs, component]
type: concept
status: active
description: "セルタイプをインスタンス化した[[tecs-overview]]コンポーネント。組上げ記述でセル間を結合する。"
---

# セル (Cell) / 組上げ記述

セルは、[[tecs-celltype]]をインスタンス化したTECSコンポーネントです。

## 組上げ記述（セル記述）

```cdl
cell [[asp3-ttask]] MyTask {
    attribute = C_EXP("TA_ACT");
    stackSize = 1024;
    priority = 42;
    cTaskBody = MyCell.eTaskBody;
};
```

## セル間結合

- `cXxx = OtherCell.eXxx;` の形式で[[tecs-port]]を接続

## See Also

- [[tecs-celltype]]
- [[tecs-signature]]
- [[tecs-cdl]]

## Counter-Arguments and Gaps

特になし。
