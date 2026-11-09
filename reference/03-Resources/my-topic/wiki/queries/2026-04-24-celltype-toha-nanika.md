---
date: 2026-04-24
tags: [tecs, toppers, query]
type: query-output
question: "セルタイプとは何ですか"
status: filed
description: "TECSにおけるセルタイプ（Celltype）の定義・構成要素・CDL記述・実装モデル・複合セルタイプを解説。"
---

# セルタイプとは何ですか

**セルタイプ**（Celltype）は、[[tecs-overview]] における**コンポーネントの型定義**です。

オブジェクト指向の「クラス」に相当し、[[tecs-cell]]（セル）はそのインスタンスにあたります。

## 構成要素

セルタイプは以下の要素を持ちます。

| 要素 | キーワード | 役割 |
|-----|-----------|------|
| シグニチャ | [[tecs-signature]] | 呼び口・受け口の関数インタフェースを定義 |
| 属性 | `attribute` | コンパイル時定数（セルごとに値を指定） |
| 変数 | `var` | 実行時の内部状態を保持 |
| 呼び口 | `call` | 他のセルのサービスを呼び出す[[tecs-port]] |
| 受け口 | `entry` | サービスを提供する[[tecs-port]] |

## CDL記述例

[[tecs-cdl]] でのセルタイプ記述:

```cdl
celltype tMyCellType {
    entry sTask eTask;          /* 受け口 — sTask シグニチャ */
    call  sTaskBody cTaskBody;  /* 呼び口 — sTaskBody シグニチャ */
    attr  int32_t priority = 10;
    var   int32_t count;
};
```

## 実装（セルタイプコード）

[[imp-celltype-code]] として C コードで実装します。

| モデル | 記述者 | 内容 |
|-------|-------|------|
| ユーザー実装モデル | アプリ開発者 | 受け口関数の本体 |
| システム実装モデル | [[tecsgen]] が自動生成 | インタフェースコード、マクロ群 |

## 複合セルタイプ

[[tecs-composite-celltype]] を使うと、複数のセルをまとめて1つのセルタイプとして外部に公開できます。内部の結合を隠蔽するカプセル化手段です。

## セルタイプとセルの関係

```
celltype tTask   →   cell tTask MyTask { ... }
   ↑ 型（クラス）          ↑ インスタンス（オブジェクト）
```

1つの [[tecs-celltype]] から複数の [[tecs-cell]] を生成できます。それぞれのセルが独立した属性値と状態を持ちます。

## Sources

- [[tecs-celltype]]
- [[tecs-signature]]
- [[tecs-port]]
- [[tecs-cell]]
- [[tecs-cdl]]
- [[imp-celltype-code]]
- [[tecs-composite-celltype]]
