---
date: 2026-08-16
description: "tecsgen外部仕様書 第10章（用語集）— CDL・セル・セルタイプ・呼び口・受け口ほかCDL言語一般の用語集。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen外部仕様]] (2026-08-16, 25KB threshold). Chapter 10 of 10.

## 10. 用語集

| 用語 | 定義 |
|------|------|
| CDL | Component Description Language。TECS のコンポーネント記述言語 |
| セル | コンポーネントのインスタンス |
| セルタイプ | コンポーネントの型定義 |
| 呼び口（Call Port） | 機能を要求するポート |
| 受け口（Entry/Receptacle） | 機能を提供するポート |
| シグニチャ | 呼び口・受け口のインターフェース定義（関数ヘッダ集合） |
| CELLCB | Cell Control Block。セルの属性・変数を格納する構造体 |
| CELLIDX | Cell Index。セルを識別するインデックス |
| ファクトリ | CDL から設定ファイル（tecsgen.cfg）を生成する記述 |
| 複合セルタイプ（composite） | 複数のセルを内包するセルタイプ |
| ネームスペース（namespace） | 名前衝突を防ぐためのスコープ機能 |
| リージョン（region） | セルのレイアウト・アクセス制御単位 |
| restrict 指定子 | 受け口への呼び出しをリージョン単位で制限する |
| 動的結合（Dynamic Join） | 実行時に呼び口の結合先を切り替える機能 |

---

