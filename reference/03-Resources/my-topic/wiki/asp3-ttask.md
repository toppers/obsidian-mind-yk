---
date: 2026-05-31
tags: [tecs, asp3, rtos, task]
type: concept
status: active
description: "ASP3+[[tecs-overview]]のタスク[[tecs-cell]]タイプ。CRE_TSK静的APIでタスクを生成し、eTask受け口で制御する。"
---

# tTask (ASP3+TECS)

`tTask`は、[[asp3-tecs]]でタスクを管理するセルタイプです。

## 主要属性

| 属性 | 型 | 説明 |
|-----|---|------|
| `id` | ID | タスクID（省略可） |
| `attribute` | ATR | タスク属性 (TA_ACT, TA_NOACTQUE, TA_RSTR) |
| `priority` | PRI | 起動時優先度 |
| `stackSize` | size_t | スタックサイズ（バイト） |

## 主要ポート

| ポート | 種別 | 説明 |
|-------|------|------|
| `eTask` | 受け口 | タスク制御・状態参照 |
| `eiTask` | 受け口 | タスク制御（非タスクコンテキスト用） |
| `cTaskBody` | [[tecs-port]] | タスク本体の受け口を結合 |

## 主要API (sTask[[tecs-signature]])

- `activate()` — タスク起動要求 (`act_tsk`)
- `cancelActivate()` — 起動要求キャンセル (`can_act`)
- `terminate()` — タスク終了 (`ter_tsk`)
- `refer(T_RTSK*)` — 状態参照 (`ref_tsk`)

## See Also

- [[asp3-tecs]]
- [[tecs-celltype]]

## Counter-Arguments and Gaps

制約タスク(TA_RSTR)はASP3デフォルトでは非サポート。
