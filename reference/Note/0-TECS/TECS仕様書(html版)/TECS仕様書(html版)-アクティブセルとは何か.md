---
date: 2026-06-18
description: "TECSにおけるアクティブセル（Active Cell）の定義 — [active]セルタイプのインスタンス、タスク・ハンドラを含む自律動作セル（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# アクティブセルとは何か

**アクティブセル**は、`[active]` 指定子を持つセルタイプから生成されたセルです。受け口関数が呼ばれなくても**自律的に動作**するコンポーネント（タスク・ハンドラ等）を表します。

## アクティブとパッシブの違い

| | アクティブ | パッシブ |
|--|-----------|---------|
| **動作開始** | 自律的に動作（OS起動時から） | 呼び口から呼ばれたときのみ |
| **含むもの** | タスク、割込みハンドラ等 | 通常のコンポーネント |
| **CDL指定子** | `[active]` | （なし） |
| **TCD表記** | 長方形の辺が**二重線** | 通常の長方形 |

## CDLでの宣言

```cdl
[active]
celltype tMyTask {
    entry sTask eTask;
    call sSysLog cSysLog;
    attr {
        int32_t priority = 5;
        int32_t stackSize = 1024;
    };
    factory {
        write("tecsgen.cfg",
              "CRE_TSK(TSKID_%s, { TA_ACT, $cbp$, tMyTask_start, %s, %s, NULL });",
              id, priority, stackSize);
    };
};
```

## TCD表記

```
+==================+
| tMyTask          |   ← 二重線でアクティブを示す
|                  |----> cSysLog
+==================+
```

## 出典

- tecs_html wiki: [TECS概要](C:/Users/ykomi/wiki/topics/tecs_html/wiki/concepts/tecs-overview.md) (confidence: high)
- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)
- tecs_html wiki: [TCDリファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/tcd-reference.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-セルタイプとは何か]] | [[TECS仕様書(html版)-アクティブの書き方を教えて]] | [[TECS仕様書(html版)-目次]]
