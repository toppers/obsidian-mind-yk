---
date: 2026-06-18
description: "TECSウィキ（tecs-0-md）クエリ回答 — 基本的なコンポーネント図の書き方。二つのセルが結合された状態を描く手順（§3.2.1）"
tags:
  - reference
  - tecs
  - wiki-query
---

# TECS仕様書(tecs-0-md)-基本的なコンポーネント図の書き方を教えて

基本的なTECSコンポーネント図（§3.2.1）は、二つのセルが結合された状態を表す。以下の手順で描く。

---

## 描き方の手順

### 1. セルを描く

セルは**長方形**により表す。長方形の内側に以下を記す：
- **セルタイプ名**（上段または左）
- **セル名**（下段または右）

### 2. 受け口を描く

受け口は長方形の辺に沿って**塗りつぶした三角形**を長方形の**内向き**に置く。三角形の横に受け口名を添える。

### 3. 呼び口を描く

呼び口はセルの長方形の辺から始まる**線分**により表す。線分に呼び口名を添える。

### 4. 結合を描く

結合は呼び口から受け口へ向かう**線分**により表す。線分に沿って**シグニチャ名**を添える。

---

## 基本例（図3.1のイメージ）

```
+------------------+         +------------------+
| tCellTypeA       |         | tCellTypeB       |
| cellA            |         | cellB            |
|           cCall -----sig--->▶ eEntry          |
+------------------+         +------------------+
```

- `cellA` の呼び口 `cCall` からシグニチャ `sig` の結合線が伸び
- `cellB` の受け口 `eEntry`（塗りつぶし三角形）に接続される

---

## CDLでの対応記述

```
celltype tCellTypeA {
    call tSig cCall;
};

celltype tCellTypeB {
    entry tSig eEntry;
};

cell tCellTypeA cellA {
    cCall = cellB.eEntry;   // 結合
};
cell tCellTypeB cellB {};
```

---

**Sources used:**
- TECS仕様書 V1.3.0.1 raw — §3.2.1「基本的なコンポーネント図」
- [TECS CDL](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/topics/tecs-cdl.md) (confidence: high) — CDLでの対応記述

**Knowledge gaps:**
- 実際の図（図3.1）はPDF変換の都合上rawソースに含まれない
