---
date: 2026-05-31
tags: [tecs, component]
type: concept
status: active
description: "[[tecs-overview]]コンポーネントの型定義。シグニチャ・属性・変数・呼び口・受け口を持つ。"
---

# セルタイプ (Celltype)

セルタイプは、TECSコンポーネントの型を定義する記述単位です。

## 構成要素

- [[tecs-signature]]（シグニチャ）— 受け口・呼び口の型
- 属性 (attribute) — コンパイル時定数
- 変数 (var) — 実行時状態
- [[tecs-port]] — 呼び口 (call) / 受け口 (entry)

## 複合セルタイプ

[[tecs-composite-celltype]] は、複数のセルをひとまとめにして1つのセルタイプとして扱う仕組み。

## 実装

[[imp-celltype-code]] — セルタイプコードで実装を記述。

## See Also

- [[tecs-cell]]
- [[tecs-cdl]]

## Counter-Arguments and Gaps

特になし。
