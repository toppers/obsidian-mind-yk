---
date: 2026-06-18
description: "TECSにおける合流（多対一結合）の書き方 — 一つの受け口に複数の呼び口を結合するCDL記述とTCD表記（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# 合流の書き方を教えて

**合流**とは、一つの受け口に複数の呼び口が結合することです。一対多の制約はありませんが（一つの呼び口が接続できる受け口は一つだけ）、一つの受け口に複数の呼び口を結合することは可能です。

## CDLでの記述

複数のセルが同じ受け口に結合するだけです：

```cdl
// サービス提供側
celltype tService {
    entry sMySignature eMain;
};

// 呼び元（複数のセルから同じ受け口へ）
cell tClientA ClientA {
    cPort = ServiceCell.eMain;    // ClientA が eMain に結合
};
cell tClientB ClientB {
    cPort = ServiceCell.eMain;    // ClientB も同じ eMain に結合
};
cell tService ServiceCell {};
```

## TCD表記

合流点では3本の線分が集まる形で表現します：

```
+------------------+
| tClientA         |
|    cPort -----\  |
+------------------+ \       +------------------+
                      >------>|> eMain           |
+------------------+ /       |   tService       |
| tClientB         |         +------------------+
|    cPort -----/  |
+------------------+
```

## 制約

- **呼び口 → 受け口**: 一対一（呼び口は一つの受け口にしか結合できない）
- **受け口 ← 呼び口**: 多対一可能（一つの受け口に複数の呼び口が結合できる）

## 出典

- tecs_html wiki: [TECS概要](C:/Users/ykomi/wiki/topics/tecs_html/wiki/concepts/tecs-overview.md) (confidence: high)
- tecs_html wiki: [TCDリファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/tcd-reference.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-結合とは何か]] | [[TECS仕様書(html版)-受け口とは何か]] | [[TECS仕様書(html版)-TECSコンポーネント図の書き方を教えて]] | [[TECS仕様書(html版)-目次]]
