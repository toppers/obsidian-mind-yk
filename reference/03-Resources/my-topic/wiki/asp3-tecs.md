---
date: 2026-05-31
tags: [tecs, asp3, rtos]
type: concept
status: active
description: "TOPPERSのASP3カーネルをTECSコンポーネントとして扱うための統合。カーネルオブジェクトをセルで管理。"
---

# ASP3+TECS

ASP3+TECSは、TOPPERS/ASP3カーネルのオブジェクトを[[tecs-cell]]として扱うための統合です。

## 提供[[tecs-celltype]]

| セルタイプ | 説明 |
|-----------|------|
| [[asp3-ttask]] | タスク |
| [[asp3-teventflag]] | イベントフラグ |
| [[asp3-tdataqueue]] | データキュー |
| [[asp3-tsemaphore]] | セマフォ |
| [[asp3-tisr]] | 割込みサブルーチン |
| [[asp3-tprioritydataqueue]] | 優先度データキュー |
| [[asp3-tfixedsizememorypool]] | 固定長メモリプール |
| [[asp3-tinitializeroutine]] | 初期化ルーチン |
| [[asp3-tterminateroutine]] | 終了処理ルーチン |

## See Also

- [[tecs-overview]]
- [[atk2-tecs]]

## Counter-Arguments and Gaps

- 制約タスクはASP3カーネルではデフォルト非サ[[tecs-port]]
