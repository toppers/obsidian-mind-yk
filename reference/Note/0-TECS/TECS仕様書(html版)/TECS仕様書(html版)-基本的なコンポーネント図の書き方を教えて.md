---
date: 2026-06-18
description: "基本的なTECSコンポーネント図（TCD）の書き方 — セル・受け口・呼び口・結合の描き方とCDL対応（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# 基本的なコンポーネント図の書き方を教えて

TECSコンポーネント図（TCD）の基本パターンです。セル・受け口・呼び口・結合の4要素を使います。

## 基本図の構成

```
+------------------+      sSignature      +------------------+
| tCellA           |                      | tCellB           |
|    cCall ------->|--------------------->|> eEntry          |
+------------------+                      +------------------+
```

## 各要素の書き方

| 要素 | 描き方 | 例 |
|------|--------|-----|
| **セル** | 長方形。内側にセルタイプ名とセル名 | `tCellA / CellA` |
| **受け口** | 辺に塗りつぶし三角形（`|>`）、受け口名 | `> eEntry` |
| **呼び口** | 辺から始まる矢印（`---->`）、呼び口名 | `cCall ---->` |
| **結合** | 呼び口→受け口への線。シグニチャ名を添える | `sSignature` |

## レイアウトの原則

- **上/左**: 上位層（アプリケーション側、呼び口を持つ側）
- **下/右**: 下位層（OS・デバイス側、受け口を持つ側）

## CDLとの対応

```cdl
// tCellA のセルタイプ
celltype tCellA {
    call sSignature cCall;
};

// tCellB のセルタイプ
celltype tCellB {
    entry sSignature eEntry;
};

// 組上げ記述（結合）
cell tCellA CellA {
    cCall = CellB.eEntry;
};
cell tCellB CellB {};
```

## 出典

- tecs_html wiki: [TCDリファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/tcd-reference.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-TECSコンポーネント図とは何か]] | [[TECS仕様書(html版)-TECSコンポーネント図の書き方を教えて]] | [[TECS仕様書(html版)-目次]]
