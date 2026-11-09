---
date: 2026-04-24
tags: [tecs, toppers, query]
type: query-output
question: "セルとは何ですか"
status: filed
description: "TECSにおけるセル（Cell）の定義・組上げ記述・ポート結合・セルタイプとの関係を解説。"
---

# セルとは何ですか

**セル**（Cell）は、[[tecs-overview]] における**コンポーネントのインスタンス**です。

オブジェクト指向でいう「クラスとインスタンス」の関係に対応して、[[tecs-celltype]]（セルタイプ）が「型」、セルがその「インスタンス」にあたります。

## 定義方法（組上げ記述）

セルは [[tecs-cdl]] の**組上げ記述**（セル記述）で定義します。

```cdl
cell tTask MyTask {
    attribute = C_EXP("TA_ACT");
    stackSize = 1024;
    priority = 42;
    cTaskBody = MyCell.eTaskBody;
};
```

- `tTask` — [[tecs-celltype]]（型）
- `MyTask` — セル名（このインスタンスの名前）
- `attribute`, `stackSize`, `priority` — 属性値（コンパイル時定数）
- `cTaskBody = MyCell.eTaskBody` — [[tecs-port]] の結合（呼び口 → 受け口）

## セル間の結合

セルは [[tecs-port]]（呼び口・受け口）を通じて互いに接続されます。

| ポート種別 | キーワード | 役割 |
|-----------|-----------|------|
| 呼び口 | `call` | 他のセルのサービスを呼び出す |
| 受け口 | `entry` | サービスを提供する |

結合構文: `cXxx = OtherCell.eXxx;`

## セルタイプとの違い

| 概念 | 役割 |
|-----|------|
| [[tecs-celltype]] | コンポーネントの**型**定義（シグニチャ・属性・ポートを含む） |
| [[tecs-cell]] | その型の**インスタンス**（名前・属性値・結合を持つ） |

## 複合セルタイプ

複数のセルをまとめて1つのセルタイプとして扱う [[tecs-composite-celltype]] という仕組みもあります。内部の結合を外部から隠蔽できます。

## Sources

- [[tecs-cell]]
- [[tecs-celltype]]
- [[tecs-overview]]
- [[tecs-port]]
- [[tecs-cdl]]
- [[asp3--task]]
