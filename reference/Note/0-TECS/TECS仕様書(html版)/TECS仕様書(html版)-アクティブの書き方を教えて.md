---
date: 2026-06-18
description: "TECSにおけるアクティブセルタイプの書き方 — [active]指定子のCDL構文、ファクトリ記述、TCD二重線表記（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# アクティブの書き方を教えて

**アクティブセルタイプ**は `[active]` 指定子を付けて宣言します。タスク・割込みハンドラ等の自律動作コンポーネントに使用します。

## CDLでの宣言

```cdl
[active]
celltype tMyTask {
    entry sTask eTask;               // タスク本体受け口
    call sSysLog cSysLog;            // ログ出力呼び口

    attr {
        int32_t priority  = 5;       // タスク優先度
        int32_t stackSize = 1024;    // スタックサイズ
    };

    // ファクトリ：静的API記述を生成
    factory {
        write("tecsgen.cfg",
              "CRE_TSK(TSKID_%s, { TA_ACT, $cbp$, tMyTask_start, %s, %s, NULL });",
              id, priority, stackSize);
    };
};
```

## 組上げ記述

```cdl
cell tMyTask MyTask {
    priority  = 10;
    stackSize = 2048;
    cSysLog   = SysLog.eSysLog;
};
```

## TCD表記

アクティブセルタイプのセルは長方形の辺を**二重線**で描きます：

```
+==================+
|| tMyTask         ||
||    cSysLog ----->||--->|> eSysLog (tSysLog)
+==================+
```

## Cコードでの実装

```c
#include "tMyTask_tecsgen.h"

// タスク本体
void tMyTask_start(intptr_t exinf) {
    CELLIDX idx = (CELLIDX)exinf;
    CELLCB *p_cellcb = GET_CELLCB(idx);

    while (1) {
        cSysLog_write(LOG_DEBUG, "running");
        dly_tsk(1000);
    }
}
```

## 出典

- tecs_html wiki: [TECS概要](C:/Users/ykomi/wiki/topics/tecs_html/wiki/concepts/tecs-overview.md) (confidence: high)
- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)
- tecs_html wiki: [TCDリファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/tcd-reference.md) (confidence: high)
- tecs_html wiki: [実装モデル](C:/Users/ykomi/wiki/topics/tecs_html/wiki/concepts/tecs-implementation-model.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-アクティブセルとは何か]] | [[TECS仕様書(html版)-セルタイプとは何か]] | [[TECS仕様書(html版)-目次]]
