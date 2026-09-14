---
date: 2026-06-18
description: "TECSにおけるセルタイプ（Celltype）の定義 — コンポーネントの型、CDLでの宣言構文（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# セルタイプとは何か

**セルタイプ (Celltype)** はTECSコンポーネントの**型定義**です。属性・受け口・呼び口・変数・ファクトリを宣言します。セルはセルタイプのインスタンスです。

## CDLでの宣言

```cdl
[active]
[singleton]
celltype tMyCelltype {
    entry sSignature eEntry;          // 受け口
    call  sSignature cCall;           // 呼び口
    [optional] call sSignature cOpt;  // オプション呼び口
    [omit] call sSignature cOmit;     // 省略可能呼び口

    call sSignature cArray[];         // 呼び口配列（静的サイズ）
    call[3] sSignature cFixed;        // 呼び口配列（固定サイズ）

    attr {
        int32_t mode = 0;             // 属性（静的パラメータ）
    };
    var {
        int32_t state;                // 変数（動的状態）
    };
    factory {
        write("output.cfg", "MACRO(%s);", id);
    };
};
```

## セルタイプ指定子

| 指定子 | 意味 |
|--------|------|
| `[active]` | アクティブセルタイプ（タスク・ハンドラを含む） |
| `[singleton]` | シングルトン（セルが1つのみ） |
| `[idx_is_id]` | idx をそのまま ID として使用 |
| `[generate(Plugin, opt)]` | セルタイププラグインを適用 |

## 出典

- tecs_html wiki: [TECS概要](C:/Users/ykomi/wiki/topics/tecs_html/wiki/concepts/tecs-overview.md) (confidence: high)
- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-セルとは何か]] | [[TECS仕様書(html版)-アクティブセルとは何か]] | [[TECS仕様書(html版)-複合セルとは何か]] | [[TECS仕様書(html版)-目次]]
