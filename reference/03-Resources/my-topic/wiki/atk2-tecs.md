---
date: 2026-05-31
tags: [tecs, atk2, autosar, rtos]
type: concept
status: active
description: "AUTOSAR OS (ATK2) をTECSコンポーネントとして扱うための統合。自動車組込み向け。"
---

# ATK2+TECS

ATK2+TECSは、AUTOSAR準拠のATK2カーネルのオブジェクトを[[tecs-cell]]として扱うための統合です。

## 提供[[tecs-celltype]]

| セルタイプ | 説明 |
|-----------|------|
| [[atk2-tkernel]] | カーネル |
| [[atk2-ttask]] | タスク |
| atk2-tisr | 割込み管理 |
| [[atk2-tcounter]] | カウンタ |
| [[atk2-talarm]] | アラーム |
| [[atk2-tresource]] | リソース |

## See Also

- [[tecs-overview]]
- [[asp3-tecs]]

## Counter-Arguments and Gaps

特になし。
