---
date: 2026-06-18
description: "TECSコンポーネント図（TCD）の定義 — CDL組上げ記述と一対一対応するビジュアル表記法、基本記号と用途（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# TECSコンポーネント図とは何か

**TECSコンポーネント図（TCD: TECS Component Diagram）** は、セルの構成と結合関係を視覚的に表現するための記法です。CDLの組上げ記述（セル記述）と**一対一に対応**し、CDLソースとして直接使用可能です。

## 基本原則

- **セル** → 長方形で表現。内側にセルタイプ名とセル名を記載
- **受け口** → 長方形の辺に**塗りつぶした三角形**（内向き）、受け口名を添える
- **呼び口** → 長方形の辺から始まる**線分**、呼び口名を添える
- **結合** → 呼び口から受け口への線分、シグニチャ名を添える
- **レイア（階層）** → 上位（アプリ）を上/左に、下位（OS/デバイス）を下/右に配置

## CDLとの対応関係

| TCD要素 | CDL対応 |
|---------|---------|
| セル長方形 | `cell tType Name { ... };` |
| 受け口三角 | `entry sSignature eName;` |
| 呼び口線分 | `call sSignature cName;` |
| 結合線 | `cName = OtherCell.eName;` |
| アクティブ二重線 | `[active] celltype tType { ... }` |
| 逆結合矢印 | `cCallback <= eCallbackEntry;` |

## 基本的な図の例

```
+------------------+      sSignature      +------------------+
| tCellA           |                      | tCellB           |
|    cCall ------->|--------------------->|> eEntry          |
+------------------+                      +------------------+
```

## 出典

- tecs_html wiki: [TCDリファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/tcd-reference.md) (confidence: high)
- tecs_html wiki: [TECS概要](C:/Users/ykomi/wiki/topics/tecs_html/wiki/concepts/tecs-overview.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-基本的なコンポーネント図の書き方を教えて]] | [[TECS仕様書(html版)-TECSコンポーネント図の書き方を教えて]] | [[TECS仕様書(html版)-結合とは何か]] | [[TECS仕様書(html版)-目次]]
