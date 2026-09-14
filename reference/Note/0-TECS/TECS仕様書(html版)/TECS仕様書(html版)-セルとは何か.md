---
date: 2026-06-18
description: "TECSにおけるセル（Cell）の定義 — コンポーネントのインスタンス、CDLでの記述方法（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# セルとは何か

**セル (Cell)** はTECSコンポーネントの**インスタンス**（実行時の実体）です。セルタイプを型として持ち、CDLの組上げ記述（セル記述）によって定義されます。

## セルの特性

- セルタイプという型定義に基づいて生成される
- 実行時に実際に存在するコンポーネントの実体
- 属性値・変数・結合先を持つ
- 一つのセルタイプから複数のセルを生成できる（シングルトンを除く）

## CDLでの記述

```cdl
[id(1)]
cell tCelltype CellName {
    attr1 = 42;
    cPort = OtherCell.ePort;   // 呼び口を受け口に結合
};
```

## 組上げ指定子

| 指定子 | 意味 |
|--------|------|
| `[id(n)]` | IDを指定（省略時 tecsgen が自動割当） |
| `[prototype]` | プロトタイプ宣言（定義なし） |
| `[allocator(c::f = e)]` | アロケータを指定 |
| `[generate(Plugin)]` | セル生成時プラグイン適用 |

## 出典

- tecs_html wiki: [TECS概要](C:/Users/ykomi/wiki/topics/tecs_html/wiki/concepts/tecs-overview.md) (confidence: high)
- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-コンポーネントとは何か]] | [[TECS仕様書(html版)-セルタイプとは何か]] | [[TECS仕様書(html版)-結合とは何か]] | [[TECS仕様書(html版)-目次]]
