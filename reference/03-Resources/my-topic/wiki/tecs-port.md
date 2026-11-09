---
date: 2026-05-31
tags: [tecs, interface]
type: concept
status: active
description: "[[tecs-overview]]コンポーネント間の接続点。呼び口(call)は依存関係を、受け口(entry)はサービス提供を表す。"
---

# ポート (呼び口・受け口)

ポートは、TECSコンポーネント間の接続点です。

## 種類

| 種別 | キーワード | 役割 |
|------|-----------|------|
| 呼び口 | `call` | 他のセルのサービスを呼び出す側 |
| 受け口 | `entry` | サービスを提供する側 |

## 非タスクコンテキスト

タスクコンテキスト外では `ei` プレフィックスの受け口を使用（例: `eiTask`）。

## See Also

- [[tecs-signature]]
- [[tecs-celltype]]
- [[tecs-cell]]

## Counter-Arguments and Gaps

特になし。
